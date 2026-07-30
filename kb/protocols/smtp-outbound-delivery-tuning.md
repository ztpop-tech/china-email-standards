---
title: "SMTP 外发投递性能调优"
source: "https://ztpop.net/kb/smtp-outbound-delivery-tuning.html"
license: CC-BY 4.0
---

# SMTP 外发投递性能调优

## 概述

邮件系统的出站投递性能直接决定了消息的及时送达率。不合理的参数配置可能导致队列积压、被目标 MTA 限流甚至列入黑名单。本文系统性地解析 Postfix 外发投递的关键控制参数，帮助运维工程师在吞吐量和对方接受度之间找到最佳平衡。

## 并发连接控制

Postfix 默认对所有目标域使用统一的并发连接池。以下参数用于精细控制并发行为：

### 全局并发限制

```
# main.cf — 全局参数
default_destination_concurrency_limit = 20
default_destination_concurrency_failed_cohort_limit = 10
default_destination_concurrency_positive_feedback = 1
default_destination_concurrency_negative_feedback = 1
```

* `default_destination_concurrency_limit` — 同一个目标域（收件域）的最大并发连接数。设置过高会被对方限流，建议 10-20。
* `default_destination_concurrency_failed_cohort_limit` — 当连续 N 个投递失败后降低并发数（负反馈）。
* `default_destination_concurrency_positive_feedback` / `negative_feedback` — 自适应并发调整的增益系数。

### 为特定域单独配置

```
# main.cf — 通过 transport_maps 实现域级覆盖
example.com  smtp:[mx.example.com]:25:
  -o destination_concurrency_limit=5
  -o destination_rate_delay=2

# 大容量域可以设置更高并发
bulk-provider.com  smtp:[mx.bulk-provider.com]:25:
  -o destination_concurrency_limit=50
  -o destination_rate_delay=0
```

### recipient\_delimiter

`recipient_delimiter = +` 使得 `user+tag@domain` 中的 `+tag` 部分被剥离后投递。对于大量使用别名分发的系统，应确认该参数是否在本地正确设置，以免影响 DSN 路由。

## 重试策略

合理的重试策略可以在避免过度打扰对方 MTA 的前提下，保证邮件最终投递成功。

```
# main.cf — 重试控制
queue_run_delay = 300          # 每 5 分钟检查一次延迟队列
minimal_backoff_time = 300     # 首次重试最小间隔 5 分钟
maximal_backoff_time = 14400   # 最大重试间隔 4 小时
queue_run_interval_reduction = no
maximal_queue_lifetime = 5d    # 队列保留时间 5 天
bounce_queue_lifetime = 5d
bounce_size_limit = 50000      # 退信正文大小上限
```

### 指数退避机制

Postfix 的重试间隔按指数递增：首次延迟 `minimal_backoff_time`，之后每次翻倍直至 `maximal_backoff_time`。例如默认配置下的重试时间线：

| 重试次数 | 延迟 | 累计时间 |
| --- | --- | --- |
| 1 | 5 min | 5 min |
| 2 | 10 min | 15 min |
| 3 | 20 min | 35 min |
| 4 | 40 min | 75 min |
| 5 | 80 min | 155 min |
| 6 | 160 min | 315 min |
| 7 | 320 min | 635 min |
| 8 | 640 min | ~21 h |

对于批量发送系统，建议将 `minimal_backoff_time` 提高到 600 秒，`maximal_backoff_time` 降低至 7200 秒，避免过度挤压队列。

## 超时参数

SMTP 协议交互各阶段都有独立的超时控制：

```
# main.cf — 超时参数
smtp_connection_timeout = 30        # TCP 连接建立超时
smtp_helo_timeout = 120             # HELO/EHLO 回复超时
smtp_mail_timeout = 300             # MAIL FROM 回复超时
smtp_rcpt_timeout = 300             # RCPT TO 回复超时
smtp_data_init_timeout = 120        # DATA 命令回复超时
smtp_data_done_timeout = 600        # 数据传输完成回复超时
smtp_quit_timeout = 30              # QUIT 命令超时
```

### 超时调整建议

| 场景 | 调整方向 | 说明 |
| --- | --- | --- |
| 目标 MX 在海外 | 增大 `smtp_connection_timeout` 至 60s | 跨洋链路延迟较高 |
| 大附件投递 | 增大 `smtp_data_done_timeout` 至 1200s | 传输速度慢时需更长等待 |
| 被频繁 4xx 的重灾区 | 减小 `smtp_helo_timeout` 至 60s | 快速断开无响应的连接 |
| 低延迟内网投递 | 全面减小至 1/3 默认值 | 减少等待时间浪费 |

## 速率限制

速率限制是避免被目标 MTA 标记为滥用的关键手段。

### smtp\_destination\_rate\_delay

```
# main.cf — 全局速率限制
smtp_destination_rate_delay = 1     # 每个目标域投递一封后至少等待 1 秒

# 覆盖特定域配置
fast-target.com     smtp:fast-target.com
  -o smtp_destination_rate_delay=0
```

该参数强制在两次投递之间插入固定间隔，适用于需要温和对待的目标域。

### anvil 速率限制模块

Postfix 自带的 anvil 服务可以限制单个客户端的连接频率：

```
# main.cf
smtpd_client_connection_rate_limit = 30   # 每分钟最多 30 个连接
smtpd_client_connection_count_limit = 10  # 同时最多 10 个连接
smtpd_client_message_rate_limit = 100     # 每分钟最多 100 封邮件
```

这些参数通常用于入站侧保护，但也可用于 submission 端口控制出站客户端的发送频率。

### 使用 anvil 跟踪连接统计

```
# 查看当前 anvil 统计
postfix anvil stats

# 重置特定客户端的速率计数器
postfix anvil flush 192.0.2.1
```

## IPv4/IPv6 双栈投递策略

越来越多的目标 MTA 同时提供 IPv4 和 IPv6 接入。Postfix 的双栈策略决定了优先使用哪种地址族：

```
# main.cf — 双栈配置
smtp_bind_address6 = 2001:db8::1    # 出站 IPv6 源地址
prefer_ipv6 = no                    # 默认优先使用 IPv4

# 可配置域级优先级
# 通过 transport_maps 引用不同的 transport
example.com  smtp-ipv6:
example.org  smtp-ipv4:

# master.cf
smtp-ipv6  unix  -       -       y       -       -       smtp
  -o prefer_ipv6=yes
  -o smtp_bind_address6=2001:db8::1

smtp-ipv4  unix  -       -       y       -       -       smtp
  -o prefer_ipv6=no
  -o smtp_bind_address=198.51.100.1
```

### 双栈投递的注意事项

* 部分目标 MTA 的 IPv4 和 IPv6 到达路径性能差异很大，建议通过实际测量选择
* DKIM 签名不受 IP 版本影响，但 IP 反查（PTR）在 IPv6 上可能配置缺失导致 HELO 检查失败
* 使用 `smtp_host_lookup = dns, native` 确保 IPv6 AAAA 记录和 IPv4 A 记录都被考虑

## 目标 MX 池化管理

Postfix 默认对所有发往同一目标域的邮件使用同一个传输通道。当目标域有多个 MX 时，可以使用 `transport_maps` 进行池化：

```
# /etc/postfix/transport
# 使用 relay transport 将特定域路由到专用传输
gmail.com       relay:[gmail-smtp-in.l.google.com]:25
outlook.com     relay:[outlook-com.olc.protection.outlook.com]:25

# main.cf
transport_maps = hash:/etc/postfix/transport
relay_transport = relay
```

### 多 IP 轮换

对于高发送量系统，可以使用多个源 IP 分散投递：

```
# master.cf — 使用不同源 IP 的多个 smtp 实例
smtp0  unix  -       -       y       -       -       smtp
  -o smtp_bind_address=198.51.100.1
smtp1  unix  -       -       y       -       -       smtp
  -o smtp_bind_address=198.51.100.2
smtp2  unix  -       -       y       -       -       smtp
  -o smtp_bind_address=198.51.100.3
```

然后在 `transport_maps` 中为不同目标域分配不同的 smtp 实例，或使用 `nexthop` 结合 `smtp_bind_address` 参数。*注意：多 IP 出站虽能提高吞吐，但也需确保各 IP 的信誉独立维护。*

## 综合调优清单

以下是一个针对日均发送量在 10 万-100 万之间的出站系统的推荐配置：

```
# 并发控制
default_destination_concurrency_limit = 15
default_destination_concurrency_failed_cohort_limit = 5

# 重试策略
queue_run_delay = 60
minimal_backoff_time = 300
maximal_backoff_time = 7200
maximal_queue_lifetime = 3d

# 超时
smtp_connection_timeout = 30
smtp_helo_timeout = 60
smtp_mail_timeout = 60
smtp_rcpt_timeout = 60
smtp_data_init_timeout = 60
smtp_data_done_timeout = 600
smtp_quit_timeout = 15

# 速率限制
smtp_destination_rate_delay = 1

# 队列管理
qmgr_message_recipient_limit = 40000
qmgr_message_active_limit = 20000
```

实际参数选择应基于对日志中 `delay` / `delays` 字段的持续分析来动态调整。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/smtp-outbound-delivery-tuning.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
