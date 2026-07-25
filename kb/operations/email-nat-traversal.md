---
title: "邮件系统 STUN/TURN/NAT 穿透 — RFC 8489/8656/8445 与自托管邮件 NAT 部署"
source: "https://ztpop.net/kb/email-nat-traversal.html"
license: CC-BY 4.0
---

# 邮件系统 STUN/TURN/NAT 穿透 — RFC 8489/8656/8445 与自托管邮件 NAT 部署

## 一、自托管邮件与 NAT 的冲突

中小企业和个人用户普遍将邮件服务器部署在家庭宽带或小型办公室 NAT 网关之后。NAT 的引入给邮件服务带来了一系列协议层面的挑战：

* **SMTP 入站**
  ：外部 MTA 需要通过 NAT 后的私有 IP 投递邮件。如果没有端口转发，外部连接根本到达不了内部 Mail Server
* **SMTP 出站 HELO/EHLO**
  ：Postfix 在 EHLO 中声明的通常是内网主机名而非公网 FQDN，导致远程 MTA 的反向 DNS 校验（PTR）失败
* **IMAP/POP3 远程访问**
  ：NAT 后的服务器对公网不可见，需要端口映射或 VPN 隧道
* **TLS 证书绑定**
  ：Let's Encrypt 等 ACME 证书的 HTTP-01 挑战需要公网可达的 80 端口

RFC 8489（STUN）、RFC 8656（TURN）和 RFC 8445（ICE）的组合最初为 WebRTC 设计，但其 NAT 穿透原理适用于任何需要在 NAT 环境下建立端到端连接的协议。本文聚焦这些协议在邮件服务场景中的可应用性与局限。

## 二、NAT 类型与邮件服务可达性

RFC 4787（NAT Behavioral Requirements）和 RFC 5382（NAT TCP Requirements）定义了 NAT 设备的行为分类。对于邮件服务，关键分类如下：

二、NAT 类型与邮件服务可达性

| NAT 类型 | 映射行为 | 邮件入站 | 邮件出站 |
| 全锥形（Full Cone） | 内部(IP,Port)→固定外部(IP,Port)，任何外部主机可回连 | ✅ 端口转发有效 | ✅ 双向通信 |
| 受限锥形（Restricted Cone） | 仅允许内部曾发送过数据的外部 IP 回连 | ⚠️ 仅已知 IP 可连接 | ✅ 主动出站后可接收 |
| 端口受限锥形（Port Restricted） | 仅允许内部曾发送过数据的外部(IP,Port)回连 | ❌ 不可预测 | ✅ 主动出站后同端口可接收 |
| 对称 NAT（Symmetric） | 每个外部目标分配不同的外部(IP,Port) | ❌ 不可达 | ✅ 出站通过（有出站 NAT 绑定） |

绝大多数家庭宽带路由器和中小企业的 NAT 网关属于
**端口受限锥形**
或
**对称 NAT**
。对称 NAT 下，即使配置了端口转发，入站连接也可能被路由器的连接跟踪表（conntrack）拒绝，因为外部发起的新连接的源 (IP,Port) 组合与内部之前出站连接的目标不匹配。

## 三、STUN 协议（RFC 8489）

STUN（Session Traversal Utilities for NAT）被设计来回答一个简单问题：
**「我的公网 IP 和端口是什么？」**

STUN 工作流程：

```
邮件服务器 (NAT后)               STUN Server (公网)
  192.168.1.100:45678  ──Binding Request──▶  stun.example.com:3478
                      ◀──Binding Response──
                         XOR-MAPPED-ADDRESS: 203.0.113.45:45678
```

STUN 服务器将 NAT 网关上映射的公网 (IP, Port) 返回给内网客户端。RFC 8489 第 6 节定义了 Binding Request/Response 消息格式以及 XOR-MAPPED-ADDRESS 属性。

在邮件场景中，STUN 的直接用途有限——邮件协议（SMTP/IMAP）是服务器端的被动监听服务，而非 WebRTC 那样的 P2P 主动建联。STUN 能为自托管的邮件服务器提供的信息仅限于：

* 确认公网 IP 地址（用于 PTR 记录验证）
* 检测 NAT 类型（判断是否需要进行额外的穿透配置）
* 辅助 ACME DNS-01 验证的公网可达性诊断

```
# 使用 stunclient 检测 NAT 类型
stunclient stun.l.google.com:19302
# 输出示例：
# Binding test: success
# Local address: 192.168.1.100:45678
# Mapped address: 203.0.113.45:45678
# NAT type: Port Restricted Cone
```

## 四、TURN 协议（RFC 8656）与邮件中继

TURN（Traversal Using Relays around NAT）在 STUN 的基础上增加了一个关键功能：
**中继转发**
。当直接的 P2P 连接不可行（对称 NAT 两侧），TURN 服务器充当中间人（relay），由客户端 Allocate 一个中继地址，对方通过 TURN 服务器中转数据。

TURN 的 Allocate 事务（RFC 8656 第 6 节）：

```
邮件服务器 ──Allocate Request──▶  TURN Server (公网)
            ◀──Allocate Success──
                RELAYED-ADDRESS: 203.0.113.100:50000
```

在邮件服务中，TURN 的中继模式在以下场景有意义：

* **Webmail 实时通知**
  ：WebSocket 长连接经过 TURN 中继以穿透企业内网防火墙
* **IMAP IDLE 推送**
  ：IMAP 的 IDLE 命令（RFC 2177）通过 TURN 中继以维持长时间的 NAT 绑定不被老化
* **SIEVE ManageSieve 远程管理**
  ：邮件过滤规则的管理连接通过 TURN 传递

但是：
**TURN 不适用于 SMTP 入站**
。SMTP 是客户端-服务器模型——发送方 MTA 作为客户端主动连接接收方 MTA 的 25 端口。TURN 是为 P2P 模型设计的中继方案，无法将外部发起到端口 25 的 SMTP 连接透明地中转到内网。

## 五、ICE 框架（RFC 8445）

ICE（Interactive Connectivity Establishment）将 STUN 和 TURN 整合为统一的连接建立框架。ICE 客户端收集所有可能的候选地址（candidates）——本地地址、STUN 反射地址、TURN 中继地址——然后通过连通性检查（connectivity checks）确定哪对候选地址可达（RFC 8445 第 6 节）。

ICE 候选地址的分类：

* **host**
  ：本地网卡地址（如 192.168.1.100:143）
* **srflx**
  ：STUN 反射地址（如 203.0.113.45:45678）
* **relay**
  ：TURN 中继地址（如 203.0.113.100:50000）

ICE 同样面向 P2P 场景。在邮件服务中，ICE 的候选地址收集逻辑可以用于：

* 构建支持 NAT 穿透的自定义邮件客户端（例如：在受控企业环境中部署的专用 IMAP 客户端，通过 WebRTC Data Channel 访问内网邮件服务器）
* 邮件服务健康探测——ICE 连通性检查机制可以周期性探测邮件服务的可达性

## 六、自托管邮件的 NAT 实战配置

### 6.1 标准方案：端口转发 + DNAT

NAT 环境下最可靠的邮件方案仍然是传统的端口转发（Port Forwarding/DNAT）：

```
# Linux iptables DNAT（路由器上）
iptables -t nat -A PREROUTING -p tcp --dport 25  -j DNAT --to 192.168.1.100:25
iptables -t nat -A PREROUTING -p tcp --dport 465 -j DNAT --to 192.168.1.100:465
iptables -t nat -A PREROUTING -p tcp --dport 587 -j DNAT --to 192.168.1.100:587
iptables -t nat -A PREROUTING -p tcp --dport 993 -j DNAT --to 192.168.1.100:993

# 确保 conntrack 允许回程包
iptables -A FORWARD -p tcp -d 192.168.1.100 --dport 25  -j ACCEPT
iptables -A FORWARD -p tcp -s 192.168.1.100 --sport 25  -j ACCEPT
```

Postfix 的相应配置（/etc/postfix/main.cf）：

```
# NAT 后的 Postfix 配置
mynetworks = 127.0.0.0/8 192.168.1.0/24
inet_interfaces = all

# 代理协议支持（HAProxy/Nginx 在前端）—— 获取真实客户端 IP
# postscreen_upstream_proxy_protocol = haproxy

# 关键：EHLO 中声明的域名必须是公网 FQDN
myhostname = mail.example.com
smtp_helo_name = mail.example.com

# SMTP 客户端绑定地址（出站方向）
smtp_bind_address = 192.168.1.100
```

### 6.2 Hairpinning 问题

Hairpinning（NAT 环回）是指内网设备通过公网 IP 访问内网服务器的场景。当内网邮件客户端（如 Thunderbird）配置为使用公网域名
`mail.example.com`
连接 IMAP 时，流量路径是：

```
客户端 (192.168.1.50) → 路由器 (NAT) → 公网 IP → 路由器 (DNAT) → 服务器 (192.168.1.100)
```

许多家用路由器不支持 Hairpinning——内网客户端无法通过公网 IP 访问内网服务。解决方案：

1. **Split-horizon DNS**
   ：内网 DNS 将
   `mail.example.com`
   解析为 192.168.1.100（内网地址），绕开 NAT
2. **内网 SRV 记录**
   ：为内网客户端提供独立的内网端点的 DNS SRV 记录

### 6.3 替代方案：SMTP 中继（推荐）

对于大多数自托管场景，最务实的方案是
**放弃 NAT 下的直接 SMTP 入站，改用 SMTP 中继服务**
：

```
# Postfix 使用外部 SMTP 中继发送邮件
relayhost = [smtp-relay.example.com]:587
smtp_sasl_auth_enable = yes
smtp_sasl_password_maps = hash:/etc/postfix/sasl_passwd
smtp_tls_security_level = encrypt

# 入站邮件通过中继服务转发到自定义端口
# 中继服务端配置：
# 接收 example.com 的邮件 → 转发到 mail.example.com:10025
```

这种方式完全规避了 NAT 穿透问题——中继服务在公网上运行，拥有稳定的公网 IP 和正确的 PTR 记录。自托管服务器只需维持到中继服务的出站连接（NAT 场景下出站天然可用）。

昆仑邮件系统为自托管客户提供 SMTP 中继服务，以解决内网 NAT 部署中入站不可达的典型痛点。

### 6.4 UPnP/NAT-PMP 自动端口映射

对于家庭或小型办公室场景，UPnP IGD（Internet Gateway Device）和 NAT-PMP/PCP（Port Control Protocol, RFC 6887）可以实现自动端口映射：

```
# 使用 miniupnpc 自动映射端口
upnpc -a 192.168.1.100 25 25 TCP
upnpc -a 192.168.1.100 587 587 TCP
upnpc -a 192.168.1.100 993 993 TCP

# 查看当前映射
upnpc -l
```

生产邮件服务
**不应依赖 UPnP**
——其映射缺乏持久性保证，路由器重启后映射可能丢失。UPnP 只在测试环境中作为一种快速验证手段。

## 七、总结

STUN/TURN/ICE 是为 WebRTC P2P 通信设计的 NAT 穿透协议家族，其核心思路——候选地址收集、连通性检查、TURN 中继——对邮件服务有借鉴意义，但不能直接套用。邮件协议（SMTP/IMAP/POP3）本质是 C/S 模型，与 P2P 的建联需求不同。

自托管邮件的 NAT 部署建议优先级：

1. **端口转发 + 静态公网 IP**
   ：最可靠方案，适用于有固定公网 IP 的企业宽带
2. **SMTP 中继服务**
   ：无公网 IP 或 CGNAT（运营商级 NAT）环境的首选，出站通过中继，入站邮件由中继转发
3. **VPN 隧道**
   ：使用 WireGuard 或 IPsec 在 VPS 与内网之间建立隧道，将公网 VPS 作为邮件流量入口
4. **Cloudflare Tunnel / FRP**
   ：隧道工具将公网端点映射到内网服务，免除手动端口转发

NAT 穿透不是协议的失败，而是网络架构的选择。正确评估网络环境、选择合适的穿透方案，自托管邮件完全可以在 NAT 之后稳定运行。

**参考文献：**
  
[1] IETF RFC 8489 — Session Traversal Utilities for NAT (STUN), February 2020
  
[2] IETF RFC 8656 — Traversal Using Relays around NAT (TURN): Relay Extensions to STUN, February 2020
  
[3] IETF RFC 8445 — Interactive Connectivity Establishment (ICE): A Protocol for NAT Traversal, August 2018
  
[4] IETF RFC 4787 — Network Address Translation (NAT) Behavioral Requirements for Unicast UDP, January 2007
  
[5] IETF RFC 5382 — NAT Behavioral Requirements for TCP, October 2008
  
[6] IETF RFC 6887 — Port Control Protocol (PCP), April 2013
  
[7] IETF RFC 5321 — Simple Mail Transfer Protocol, October 2008
  
[8] NIST SP 800-177 Rev.1 — Trustworthy Email, February 2019
  
[9] GB/T 30282-2013 — 信息安全技术 反垃圾邮件产品技术要求和测试评价方法

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-nat-traversal.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
