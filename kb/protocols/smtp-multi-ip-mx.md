---
title: "邮件网关 multi-IP 轮询与 smtp_bind_address 策略"
source: "https://ztpop.net/kb/smtp-multi-ip-mx.html"
license: CC-BY 4.0
---

# 邮件网关 multi-IP 轮询与 smtp_bind_address 策略

## 概述

大型邮件网关每天处理数百万封出站邮件，单一源 IP 地址的风险很高——该 IP 若因某个客户的投递行为被列入 DNSBL，将影响其他所有客户的投递信誉。通过 Multi-homing MX 设计，邮件网关可以在多个源 IP 之间分配出站连接，既提升吞吐又隔离投递信誉。同时，MX 记录的多 IP 轮询机制实现了[1] 接收端的负载均衡。

## Multi-homing MX 设计

### DNS 中的多 IP MX 声明

RFC 5321 §5.1 [1] 允许一个域名声明多个 MX 记录，所有记录均返回 A/AAAA 记录。MTA（发送端）按优先级顺序（preference 值从小到大）尝试 MX 服务器，相同优先级内随机连接。这是 SMTP 协议层面的天然负载均衡机制。

```
; 多 IP MX 记录设计（3 个入站 MX + 多个源 IP）
; 入站 MX - 相同优先级，发送端 MTA 随机选择
example.com.    IN MX 10 mx1.example.com.
example.com.    IN MX 10 mx2.example.com.
example.com.    IN MX 10 mx3.example.com.

mx1.example.com. IN A 203.0.113.11
mx1.example.com. IN AAAA 2001:db8:1::11
mx2.example.com. IN A 203.0.113.12
mx2.example.com. IN AAAA 2001:db8:1::12
mx3.example.com. IN A 203.0.113.13
mx3.example.com. IN AAAA 2001:db8:1::13
```

### 出站网关的源 IP 池设计

出站邮件网关应将出站 IP 地址池化，按策略分配：

* **高信誉池**（/29 子网，4–6 个 IP）：用于事务性邮件和主域投递
* **标准池**（/28 子网，8–14 个 IP）：用于批量营销邮件
* **低信誉池**（/27 子网，20+ 个 IP）：用于有投诉历史的客户邮件，作为隔离层

## IP 轮询策略

### Round-Robin（简单轮询）

最简单的策略：顺序分配源 IP 给每个新连接。Postfix 的 `smtp_bind_address_per_policy` 配合数组可实现无状态的 round-robin：

```
# main.cf - 简单的 round-robin
smtp_bind_address = 203.0.113.20

# 使用 transport 按域绑定额外的 bind 地址
# /etc/postfix/transport
# bulk.example.com  smtp-bulk:
# highrep.example.com smtp-highrep:

# /etc/postfix/master.cf
# smtp-bulk  unix  -       -       n       -       -       smtp
#   -o smtp_bind_address=203.0.113.30
#   -o smtp_bind_address6=2001:db8:1::30
# smtp-highrep unix -       -       n       -       -       smtp
#   -o smtp_bind_address=203.0.113.20
#   -o smtp_bind_address6=2001:db8:1::20
```

### 权重轮询（Weighted Round-Robin）

当 IP 池中各 IP 的信誉或带宽不同时，应使用权重分配。权重轮询可以通过 master.cf 中不同 `smtp_bind_address` 的进程数比例实现：

```
# master.cf - 通过进程数实现权重分配
# 高信誉 IP - 更多进程（60% 流量）
outbound-highrep1 unix - - n - 150 smtp
  -o smtp_bind_address=203.0.113.20
outbound-highrep2 unix - - n - 150 smtp
  -o smtp_bind_address=203.0.113.21
outbound-highrep3 unix - - n - 100 smtp
  -o smtp_bind_address=203.0.113.22

# 标准 IP - 中等进程（40% 流量）
outbound-std1 unix - - n - 100 smtp
  -o smtp_bind_address=203.0.113.30
outbound-std2 unix - - n - 60 smtp
  -o smtp_bind_address=203.0.113.31

# 发送类的 transport 配置
# postconf -M | grep outbound
```

### 最小连接策略（Least-Connections）

基于当前活动连接数分配 IP——将新出站连接分配给当前活动连接最少的 IP 地址。Postfix 不自带 least-connections 支持，需通过外部代理（如 HAProxy）或自定义脚本配合 `smtp_bind_address_per_policy` 配置文件实现：

```
# least_connections_bind.py - 外部脚本动态选择绑定地址
# 通过 smtp_bind_address_per_policy 调用
#
# 配置:
# smtp_bind_address_per_policy = check_policy_service
#   unix:private/policy

import socket, subprocess, json, os

# IP 池
IP_POOL = ["203.0.113.20", "203.0.113.21", 
           "203.0.113.22", "203.0.113.30"]

def get_least_connected_ip():
    conn_stats = {}
    for ip in IP_POOL:
        # 检查该 IP 当前建立的出站连接数
        out = subprocess.check_output(
            f"ss -tn state established src {ip} | wc -l", shell=True)
        conn_stats[ip] = int(out.strip())
    return min(conn_stats, key=conn_stats.get)

# ... (Postfix policy service 实现略)
```

## 反向 DNS（PTR）与源 IP 信誉

PTR 记录是邮件投递信誉体系中最重要的基础要素之一。RFC 5321 [1] 建议发送端的 IP 地址应具有匹配的 PTR 记录，且 PTR 返回值应与其 EHLO/HELO 域名一致（FCrDNS - Forward Confirmed Reverse DNS）[3]。缺失或错误配置的 PTR 记录是邮件被接收端临时拒绝（4xx）的常见原因。

### PTR 配置要求

* 每个出站源 IP 必须有 PTR 记录
* PTR 值应与 EHLO 域名一致
* PTR 域名必须存在前向 A/AAAA 记录（Forward Confirmed）
* PTR 不应指向泛域名（\*.example.com）

```
; 反向 DNS 配置示例
; ARPA 反向区域
; /etc/bind/db.203.0.113
1.113.0.203.in-addr.arpa. IN PTR outbound1.example.com.
    2.113.0.203.in-addr.arpa. IN PTR outbound2.example.com.
    3.113.0.203.in-addr.arpa. IN PTR outbound3.example.com.

    ; 前向确认 - 每个 PTR 域名的 A 记录应指回原 IP
    outbound1.example.com. IN A 203.0.113.1
    outbound2.example.com. IN A 203.0.113.2
    outbound3.example.com. IN A 203.0.113.3
```

### 信誉隔离策略

```
# 信誉清单 DNS 查询（检查源 IP 黑名单状态）
for ip in 203.0.113.{1..10}; do
    rev=$(echo $ip | awk -F. '{print $4"."$3"."$2"."$1}')
    result=$(dig +short ${rev}.zen.spamhaus.org A)
    if [ -n "$result" ]; then
        echo "WARNING: $ip listed in Zen: $result"
    fi
done
```

## Postfix smtp\_bind\_address\_per\_policy 配置

Postfix 2.10+ 引入的 `smtp_bind_address_per_policy` [4] 是生产环境中最灵活的 IP 绑定策略实现方式。它允许基于目标域、目标 IP、下一跳主机名等条件动态选择源 IP。

### 配置文件语法

```
# /etc/postfix/main.cf
# 默认绑定地址
smtp_bind_address = 203.0.113.20
smtp_bind_address6 = 2001:db8:1::20

# 按策略表动态选择绑定地址
smtp_bind_address_per_policy = 
    hash:/etc/postfix/smtp_bind_policy

# smtp_bind_policy (hash 格式)
# 键格式: <nexthop> <IP:port>
# 值格式: <source-IP>[:<source-port>]
# postmap /etc/postfix/smtp_bind_policy

# 阿里云 mx - 使用华东 IP
mxhz.example.com:25    203.0.113.30
mxhz.example.com:25     2001:db8:1::30

# 腾讯云 mx - 使用华南 IP
mxnb.example.com:25   203.0.113.40
mxnb.example.com:25     2001:db8:1::40

# 国外 mx - 使用华东境外优化 IP
mxus.example.com:25    198.51.100.10

# 微信/腾讯域 - 专用信誉 IP
mx.qq.com:25           203.0.113.50
```

### PCI-Express 级流量分配（进阶）

```
# /etc/postfix/master.cf - 完整多实例出站配置
# 4 组出站 IP，每组绑定不同源 IP 池
#
# 池-A 高信誉: 203.0.113.20-23 (事务性邮件)
out-a1 unix - - n - 200 smtp
  -o smtp_bind_address=203.0.113.20
  -o smtp_bind_address6=2001:db8:1::20
out-a2 unix - - n - 200 smtp
  -o smtp_bind_address=203.0.113.21
  -o smtp_bind_address6=2001:db8:1::21
out-a3 unix - - n - 200 smtp
  -o smtp_bind_address=203.0.113.22
  -o smtp_bind_address6=2001:db8:1::22

# 池-B 标准: 203.0.113.30-35 (B2B 沟通)
out-b1 unix - - n - 100 smtp
  -o smtp_bind_address=203.0.113.30
out-b2 unix - - n - 100 smtp
  -o smtp_bind_address=203.0.113.31
```

## 运营与监控

```
# 监控各源 IP 的出站连接数
for ip in 203.0.113.{20..50}; do
    cnt=$(ss -tn state established src "$ip" 2>/dev/null | wc -l)
    if [ "$cnt" -gt 0 ]; then
        echo "$ip: $cnt connections"
    fi
done

# 监控各 IP 的投递成功率
# 从邮件日志提取
grep -oP 'status=sent .*? (delay=.*?), dsn=2\..*? ' /var/log/mail.log \
  | awk '{ for(i=1;i<=NF;i++) if($i ~ /src=/) print $i }' \
  | sort | uniq -c | sort -rn

# 动态切换故障 IP（临时从池中移除）
postconf -e "smtp_bind_address=# 203.0.113.22"
# 使其不再接受新连接，等待现有连接完成
ss -K src 203.0.113.22 dport :25
```

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/smtp-multi-ip-mx.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
