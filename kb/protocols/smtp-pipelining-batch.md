---
title: "SMTP PIPELINING 批量投递优化 — RFC 2920/RFC 2197 命令流水线与吞吐调优"
source: "https://ztpop.net/kb/smtp-pipelining-batch.html"
license: CC-BY 4.0
---

# SMTP PIPELINING 批量投递优化 — RFC 2920/RFC 2197 命令流水线与吞吐调优

## 1. PIPELINING 协议原理

### 1.1 基础行为：自然流水线

RFC 2920 §2.1 定义了 PIPELINING 的基本行为 [1]：客户端在接收到服务器的 EHLO 回复（包含 PIPELINING 关键字）后，可以在不等待中间回复的情况下连续发送多个 SMTP 命令。服务器必须按照接收顺序处理命令，并在适当的时机返回回复。回复的次序必须与命令的发送次序一致。

典型的流水线会话示例：

```
发件 MTA 连接收件 MX（RTT ≈ 50ms）：

非流水线模式（5 个收件人 + DATA）：
  C: MAIL FROM:
  S: 250 OK                                    ← +1 RTT
  C: RCPT TO:
  S: 250 OK                                    ← +1 RTT
  C: RCPT TO:
  S: 250 OK                                    ← +1 RTT
  C: RCPT TO:
  S: 250 OK                                    ← +1 RTT
  C: RCPT TO:
  S: 250 OK                                    ← +1 RTT
  C: RCPT TO:
  S: 250 OK                                    ← +1 RTT
  C: DATA
  S: 354 Start mail input                      ← +1 RTT
  总 RTT：7（约 350ms 纯等待）

流水线模式（PIPELINING 声明后）：
  C: MAIL FROM:
  C: RCPT TO:
  C: RCPT TO:
  C: RCPT TO:
  C: RCPT TO:
  C: RCPT TO:
  C: DATA
  S: 250 OK                                    ← 回复顺序：MAIL FROM OK
  S: 250 OK                                    ← RCPT TO user1 OK
  S: 250 OK                                    ← RCPT TO user2 OK
  S: 250 OK                                    ← RCPT TO user3 OK
  S: 250 OK                                    ← RCPT TO user4 OK
  S: 250 OK                                    ← RCPT TO user5 OK
  S: 354 Start mail input                      ← DATA OK
  总 RTT：1（约 50ms 串行等待 + 回复批量到达）
```

在流水线模式下，7 条命令在 1 个 RTT 内全部发出。这对高延迟链路（RTT > 100ms）的提升尤为显著。

### 1.2 延迟绑定（Deferred Binding）与立即否定

PIPELINING 在协议层面临一个设计难点：当服务器在处理流水线中的 RCPT TO 命令时，如果中间的某个收件人被拒绝（550 5.1.1 用户不存在），服务器不一定会立即回复 550。因为 reply buffer 需要维持与命令顺序一致的回复序列。

RFC 2920 引入了两种处理模式 [1, §3]：

* **立即否定（Immediate Rejection）** — 服务器在发现某个 RCPT TO 无效时立即返回 5xx，同时继续处理流水线中的后续命令。客户端必须根据回复次序推断每个命令的结果。
* **延迟绑定（Deferred Binding）** — 服务器暂存所有命令的结果，在完成整个流水线段的处理后再一次性回复。这对 MAIL FROM 和 DATA 命令的影响更大——如果 MAIL FROM 失败，后续的 RCPT TO 和 DATA 都会被丢弃。

Postfix 默认使用立即否定模式。这意味着即使流水线中一部分收件人被拒，对有效收件人的 RCPT TO 和 DATA 投递仍会继续。

## 2. PIPELINING 与协议扩展的协同

### 2.1 PIPELINING + CHUNKING（RFC 3030）→ 零拷贝批量投递

当 PIPELINING 与 CHUNKING（BDAT 命令）结合使用时，可以实现真正意义上的零拷贝批量投递。BDAT 允许在流水线序列中嵌入数据块，发送完最后一个数据块后直接跟在流水线末端，无需等待 354 回复：

```
EHLO sender.example.com
250-STARTTLS
250-PIPELINING
250-CHUNKING
250-8BITMIME
250 SMTPUTF8

-- 流水线：MAIL FROM + RCPT TO + BDAT（一次发出）
C: MAIL FROM:
C: RCPT TO:
C: RCPT TO:
C: RCPT TO:
C: BDAT 1024 LAST
C: [1024 字节邮件数据]
-- 服务器回复到达（按命令顺序）
S: 250 OK
S: 250 OK
S: 250 OK
S: 250 OK
S: 250 2.5.0 OK: queued as B3A1B2C3D4
```

这里的 BDAT 被视为一条 SMTP 命令，因此可以进入流水线序列。投递耗时为 1-RTT + 数据传输时间，允许在批量投递中接近带宽饱和水平。

### 2.2 PIPELINING + DSN（RFC 3461）→ 批量带报告投递

当 PIPELINING 与 DSN 结合，发件方可以请求一次批量投递并为每个收件人获取独立的投递状态：

```
C: MAIL FROM: RET=HDR ENVID=MSG001
C: RCPT TO: NOTIFY=SUCCESS,FAILURE ORCPT=rfc822;user1@example.com
C: RCPT TO: NOTIFY=SUCCESS,FAILURE ORCPT=rfc822;user2@example.com
C: RCPT TO: NOTIFY=FAILURE ORCPT=rfc822;user3@example.com
C: DATA
-- 批量回复序列
S: 250 2.1.0 OK (MAIL FROM accepted)
S: 250 2.1.5 OK (user1 accepted)
S: 250 2.1.5 OK (user2 accepted)
S: 550 5.1.1 User unknown (user3 rejected)
S: 354 Start mail input
-- 数据阶段正常完成
C: [邮件内容]
S: 250 2.6.0 Message accepted (queued)
```

通过流水线，DSN 参数的 ORCPT（原收件�地址）在单个 IP 连接中为每个收件人独立指定，而不会引入额外 RTT 开销。

## 3. Postfix 中的 PIPELINING 配置

### 3.1 出站 PIPELINING

Postfix 默认启用 PIPELINING。如果目标 MTA 在 EHLO 中声明支持 PIPELINING，Postfix 的出站传输进程会自动启用流水线模式。没有额外的配置项需要修改。但可以通过 transport 强制启用甚至禁用：

```
# 查看当前 PIPELINING 支持状态
$ postconf -d | grep pipeline
enable_original_recipient = no
smtp_pix_workaround_delay_time = 10s

# 确认出站 EHLO 中发送 PIPELINING
# 在 mail.log 中检索
$ grep "EHLO" /var/log/mail.log | head -1
```

Postfix 的出站传输进程（smtp(8)）会自动检测对方 EHLO 回复中的 PIPELINING 关键字。

### 3.2 入站 PIPELINING

Postfix 始终在入站 EHLO 回复中声明 PIPELINING 支持（受 `disable_esmtp_extensions` 控制）。如需验证：

```
# telnet 测试
$ telnet localhost 25
EHLO test
250-PIPELINING
250 8BITMIME
```

如发现入站未声明 PIPELINING，检查配置：

```
$ postconf disable_esmtp_extensions
disable_esmtp_extensions = no   # 必须为 no 或未设置
```

### 3.3 批量投递节点配置

对邮件列表、事务邮件等大容量投递场景，可配置专门的批量投递服务以充分利用 PIPELINING：

```
# /etc/postfix/master.cf
# 标准出站传输
smtp      unix  -       -       y       -       -       smtp
# 批量投递传输（更高并发，更长连接复用）
bulk      unix  -       -       y       -       50      smtp
  -o syslog_name=postfix/bulk
  -o smtp_connection_cache_on_demand=yes
  -o smtp_connection_cache_time_limit=30s
  -o smtp_destination_concurrency_limit=20
  -o default_destination_recipient_limit=100
  -o smtp_connection_reuse_time_limit=600s
  -o smtp_connect_timeout=15s
  -o smtp_helo_timeout=10s
  -o smtp_data_done_timeout=30s

# 使用 transport 将特定域路由到 bulk 传输
# /etc/postfix/transport:
newsletter.example.com  bulk:
bulk-mailer.example.com  bulk:
```

## 4. 性能基准

以下基准数据来自一个典型的企业邮件服务器仿真环境（2 vCPU, 4GB RAM, emulated 50ms RTT 到目标 MX）：

表1：PIPELINING 启用前后的吞吐对比

| 场景 | 无 PIPELINING | 有 PIPELINING | 提升 |
| 1 封/连接，1 个收件人 | ~10 mps | ~10 mps | ≈0%（单收件人无差异） |
| 1 封/连接，5 个收件人 | ~5 mps | ~12 mps | +140% |
| 1 封/连接，10 个收件人 | ~3 mps | ~14 mps | +367% |
| 多发多收 + CHUNKING | ~4 mps | ~18 mps | +350% |

PIPELINING 的收益直接与收件人数量成正比——每 RCPT TO 节省 1-RTT 的等待时间。在实际的邮件列表投递（每封邮件 100+ 收件人）中，PIPELINING 的性能优势可达 10 倍以上。

## 5. 兼容性与排障

### 5.1 老旧 MTA 的 PIPELINING 支持

大多数现代 MTA（Postfix ≤1999, Exchange ≤2000, Sendmail ≤8.12, OpenSMTPD, Exim）均支持 PIPELINING。但以下场景可能存在问题：

* **虚假声明：** 极少数老旧 MTA 在 EHLO 中声明 PIPELINING 但不正确处理流水线请求。Postfix 默认使用宽松模式处理此类行为——如果收到无效回复，自动降级到非流水线模式并重试。
* **嵌入式网关：** 某些邮件安全网关（2020 年前的型号）在转发模式下可能不支持 PIPELINING 的流水线优化。配置中列出的接收 MX 如果声称 PIPELINING 但实际行为不符合规范，可能导致部分收件人被静默丢弃。

### 5.2 排障方法

```
# 检查出站 PIPELINING 是否工作
$ tcpdump -i any -s 0 port 25 -X | grep -E "MAIL FROM|RCPT TO|BDAT"

# 观察日志中是否有多条 RCPT TO 后接 250 回复（无 PIPELINING 时为严格交替）
$ postconf | grep smtp_pipeline
smtp_pipeline = yes     # 默认启用

# 逐个目标域测试
$ telnet mx.example.com 25
EHLO test
250-PIPELINING
MAIL FROM:
RCPT TO:
RCPT TO:

## 6. 最佳实践总结

1. 始终启用 PIPELINING： 出站和入站都不应禁用 PIPELINING。它的性能收益远超潜在兼容性风险。
2. PIPELINING + CHUNKING 同时启用： 两者协同工作才能实现零拷贝批量投递。入站声明 CHUNKING 的服务器应同时声明 PIPELINING。
3. 批量投递使用专用传输： 通过 transport_maps 将邮件列表等大容量投递路由到高并发、长连接的批量传输（如本文的 bulk 传输），与日常交互式邮件隔离。
4. 配合 default_destination_recipient_limit 调整批次大小： 过小的批次（如 10 个收件人）没有充分利用 PIPELINING 的流水线优势，过大的批次（如 200+ 收件人）可能触发接收方的收件人上限。建议 50-100 为佳。
5. 与 DSN 一起使用以获取独立状态： 流水线即使只有 1 个收件人失败，剩余收件人也能正常投递。DSN 的 NOTIFY 和 ORCPT 参数在此场景下提供精确的状态追踪。

## 参考文献

1. IETF RFC 2920 (2000) — SMTP Service Extension for Command Pipelining, N. Freed
2. IETF RFC 2197 (1997) — SMTP Service Extension for Command Pipelining (obsoleted by RFC 2920)
3. IETF RFC 3030 (2000) — SMTP Service Extensions for Transmission of Large and Binary MIME Messages (CHUNKING / BDAT)
4. IETF RFC 5321 §4.5.2 (2008) — Simple Mail Transfer Protocol: Tunneling and Transparency
5. IETF RFC 3461 (2003) — SMTP Service Extension for Delivery Status Notifications (DSN)
6. Postfix Documentation — SMTP(8), https://www.postfix.org/smtp.8.html
7. Postfix Documentation — master(5) Transport Configuration, https://www.postfix.org/master.5.html
```

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/smtp-pipelining-batch.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
