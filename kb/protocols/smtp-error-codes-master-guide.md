---
title: "SMTP错误码完全手册：从协议层到可操作排障流程"
source: "https://ztpop.net/kb/smtp-error-codes-master-guide.html"
license: CC-BY 4.0
---

# SMTP错误码完全手册：从协议层到可操作排障流程

## 1. SMTP应答码协议基础

SMTP应答采用三位十进制数字编码，每行以三位数字后接空格（单行）或连字符（多行续传）开头。RFC 5321 §4.2 仅定义了第一位的成败语义和有限的第二、三位分配，RFC 3463（增强状态码）在此之上引入了 `X.Y.Z` 三层结构化编码，通过扩展文本字段附着于 SMTP 响应行中：`550 5.7.1 Relay access denied` 的 "5.7.1" 部分即增强状态码。RFC 5248 为所有已知增强状态码建立了 IANA 注册表。

在实际运维中，同一逻辑错误可能在不同 MTA 上呈现不同的基础码文本。例如收件人地址未知在 Postfix 上为 "550 5.1.1 Recipient address rejected: User unknown"，在 Exchange 上则是 "550 5.1.10 RESOLVER.ADR.RecipientNotFound"。理解增强状态码而非基础码文本，是实现跨 MTA 一致排障的关键。

### 1.1 三位基础码语义层级

1.1 三位基础码语义层级

| 第一位 | 类别 | 发送方MTA后续行为 |
| 2yz | 成功完成 | 继续下一SMTP命令或进入下一跳 |
| 3yz | 中间状态 | 发送更多数据（DATA命令后等待354） |
| 4yz | 临时失败 | 入重试队列，按退避策略重试 |
| 5yz | 永久失败 | 立即退回至Return-Path，生成DSN |

第二位的功能域分组：0=语法（命令不可识别、参数畸形），1=信息性应答，2=连接与传输通道（TCP链路、TLS协商状态），5=邮件系统（邮箱状态、转发策略、存储配额）。第三位在同一功能域内提供细化分类。Postfix、Exchange、Sendmail 在基础码的第二、三位定义上存在细微差异——例如 Postfix 对 DNS 临时故障返回 450 4.7.1，而 Exchange 在相同场景下可能返回 451 4.4.0。

### 1.2 RFC 3463 增强状态码架构

格式严格为 `X.Y.Z`，每层一个十进制数字。X 唯一编码成功类别（2/4/5），Y 标识受影响的邮件子系统，Z 提供子系统内的故障细节。以下为完整的 Y 层分类及运维关注点：

1.2 RFC 3463 增强状态码架构

| Y | 子系统 | 运维关注点 |
| 0 | 未定义 | 诊断信息不足，需依赖日志时间线推断 |
| 1 | 寻址（Addressing） | 用户不存在（5.1.1）、邮箱已满（5.2.2）、转发环路（5.3.5） |
| 2 | 邮箱（Mailbox） | 配额超限（5.2.2）、邮箱已禁用（5.2.1） |
| 3 | 邮件系统（Mail System） | 路由不可达（5.3.0）、磁盘满（4.3.0） |
| 4 | 网络与路由 | DNS解析故障（4.4.3）、连接超时（4.4.1）、无应答（4.4.7） |
| 5 | 投递协议 | 投递重试超限（4.5.0）、命令乱序（5.5.1） |
| 6 | 邮件内容/介质 | 裸换行符（5.6.11）、MIME结构违规（5.6.5）、过大（5.3.4） |
| 7 | 安全与策略 | 中继拒绝（5.7.1）、SPF失败（5.7.23）、DMARC拒绝（5.7.26）、黑名单（5.7.510） |

Y=7 的安全/策略子码占据了生产环境中约60%的非投递原因。Z 层在此域下高度密集：5.7.1（中继拒绝）、5.7.23（SPF验证失败）、5.7.25（反向DNS不匹配）、5.7.26（DMARC策略拒绝）、5.7.300-5.7.799（各厂商私有策略码）。

## 2. 高频错误码详细排障

### 2.1 550 5.1.1 — 收件人地址不存在

接收方MTA在RCPT TO阶段查询本地用户数据库后返回的用户未知确认。排查路径按优先级排列：

1. 验证本地拼写错误——常见失误包括域拼写颠倒（`user@gmali.com`）、Unicode同形字攻击导致的视觉相似字符。
2. 执行DNS MX验证：`dig +short MX <domain>` 确认MX记录指向正确的邮件接收服务器。当MX指向第三方网关（如Proofpoint、Mimecast）而网关的后端目录同步滞后，也会产生5.1.1。
3. Exchange Online 场景：检查收件人类型（`Get-Recipient user@domain.com`），SharedMailbox 和 RemoteUserMailbox 需特定路由配置。软删除邮箱（SoftDeletedMailbox）的SMTP ProxyAddresses 残留会阻塞新邮箱的地址分配。
4. 目录同步冲突：Azure AD Connect 将同一 SMTP 地址分配给两个不同本地 AD 用户时，Exchange Online 返回 5.1.1 而非预期的同步错误。

```
# Exchange Online 收件人诊断命令
Get-Recipient user@contoso.com | fl DisplayName,RecipientType,EmailAddresses
# 检查 SoftDeletedMailbox 冲突
Get-Mailbox -SoftDeletedMailbox | ?{$_.EmailAddresses -match "user@contoso.com"}
```

### 2.2 554 5.7.1 — 中继访问拒绝

接收MTA的SMTP会话中，MAIL FROM 域与 RCPT TO 域均非本服务器负责的域，且发送方未通过身份验证时返回。Postfix 的 `smtpd_relay_restrictions` 参数和 `mynetworks` 参数是控制此行为的核心配置。

```
# Postfix main.cf — 安全的中继控制
smtpd_relay_restrictions =
    permit_mynetworks,
    permit_sasl_authenticated,
    reject_unauth_destination
smtpd_sasl_auth_enable = yes
smtpd_tls_auth_only = yes
mynetworks = 127.0.0.0/8, [::1]/128, 10.0.0.0/8
```

`reject_unauth_destination` 检查 RCPT TO 域是否在 `mydestination`、`virtual_alias_domains`、`virtual_mailbox_domains` 或 `relay_domains` 中——四者皆不匹配时发出 5.7.1。Exchange 中对应的配置位于接收连接器的 Authentication 选项卡：勾选 "Anonymous users" 权限组即允许匿名中继（生产环境应仅在明确需要时开启）。

客户端排障步骤：(a) 确认 EHLO 后立即执行 AUTH LOGIN/PLAIN 完成 SASL 认证；(b) 检查源 IP 是否在 Postfix `mynetworks` 范围内——VPN 客户端和容器网络的 IP 段经常被遗漏；(c) 使用 `telnet <mx> 587` 而非 25 端口——587（submission）端口通常要求 SASL 认证但不对中继进行 `mydestination` 检查。

### 2.3 550 5.7.26 — DMARC 策略拒绝

Google 和 Yahoo 于 2024 年 2 月起对每日超过 5,000 封的发件域强制执行 DMARC 验证。5.7.26 是接收方 MTA 在 DMARC p=reject + SPF/DKIM 对齐双重失败时返回的增强状态码。其判定链路为：

1. 接收 MTA 执行 SPF 检查（比对连接 IP 与发件域 SPF 记录）。
2. 执行 DKIM 签名验证（解析选择器 DNS 记录，解密签名，比对哈希）。
3. DMARC 对齐判定：Return-Path 组织域 vs From 组织域（SPF 对齐），DKIM d= 标签组织域 vs From 组织域（DKIM 对齐）。
4. 任意一条对齐通过 → DMARC pass；两条均失败 → DMARC fail → 按 p= 策略处置。p=reject 时产生 5.7.26。

```
# 验证 DMARC 记录与对齐条件
$ dig +short TXT _dmarc.sender.example
"v=DMARC1; p=reject; rua=mailto:dmarc@example.com; pct=100"

# 检查 SPF 对齐 — Return-Path 域 vs From 域
# 邮件头中的 Return-Path: <bounce@bounce.example.org> vs From: sender@example.com
# → 组织域 example.org ≠ example.com → SPF对齐失败
```

### 2.4 550 5.0.350 — Exchange Online 通用封装错误

Exchange Online Protection 将远程服务器的实际错误封装为 5.0.350 的 "Remote Server returned" 格式。该码无对应 RFC 3463 定义，完全属于 Microsoft 私有。NDR 正文中的 `##[x-ms-diagnostics]` 段落携带了原始远程服务器响应。

```
# Exchange Online NDR 中提取真实错误
Diagnostic information for administrators:
Remote Server returned '550 5.7.510 Access denied, banned sender [198.51.100.25]'
##[x-ms-diagnostics]RemoteServer;RCPTTO;550 5.7.510 Access denied,
  banned sender [198.51.100.25];Relaying;nrcpt=1
```

解封装后应继续按实际错误码（本例中的 5.7.510 — Microsoft 的发件人黑名单）进行排障。5.0.350 本身不参与排障决策——必须穿透此封装层。

### 2.5 451 4.7.650 — Exchange Online 外部发件人速率限制

Office 365 对外部入站邮件施加多层速率控制：IP 级并发连接限制（默认 20）、收件人速率（10,000/天）、以及发件人信誉评分。持续超越阈值会触发 4.7.650 临时拒绝。

2.5 451 4.7.650 — Exchange Online 外部发件人速率限制

| 限制类型 | 默认阈值 | 需工单提升 |
| IP 并发 SMTP 连接 | 20 | 是 |
| 每日收件人总数 | 10,000 | 否（可通过多个发送 IP 扩展） |
| 发件人信誉阈值 (SR) | SR < -1 | 否（改进发送行为后自动恢复） |
| 租户级入站每分钟速率 | 36 封/分钟/IP | 否 |

### 2.6 554 5.6.11 — 裸换行符拒绝

RFC 5322 §2.3 规定邮件消息体的行终止符必须为 CRLF（0x0D 0x0A），禁止孤立的 CR（0x0D）或 LF（0x0A）。含裸 LF（Bare LF, BLF）的邮件在通过某些 MTA 时触发 5.6.11。Microsoft、Proofpoint 和部分日本 ISP 的 MTA 严格拒绝 BLF 邮件。产生 BLF 的常见场景：从仅用 LF 的 Unix 应用程序逐行写入邮件体、流式传输时缓冲区边界割裂 CRLF、以及 Base64/QP 编码器实现缺陷。

```
# 检测邮件队列中的裸 LF
# 查找单独的 0x0A 前无 0x0D
$ grep -Prl '(?<!\x0d)\x0a' /var/spool/postfix/deferred/
# Python 修复脚本思路
import re
msg = msg.replace('\r\n', '\n').replace('\r', '\n')
fixed = msg.replace('\n', '\r\n')
```

### 2.7 550 5.7.64 — Microsoft 365 租户边界拒绝

收件人位于 Microsoft 365 的不同租户，发件方未经 Exchange Online Protection（EOP）直接投递到 Exchange Online 的 MX 入口。租户边界隔离策略禁止跨租户的非路由投递——所有外部邮件必须通过 EOP 入站连接器进入目标租户。解决路径：(a) 确认目标域 MX 记录指向 `<tenant>.mail.protection.outlook.com`；(b) 若使用第三方邮件网关，配置网关的出站投递指向 EOP；(c) 在混合部署环境中，确认接收连接器的 `msExchServerRole` 与路由拓扑一致。

### 2.8 452 4.5.3 — 收件人数量超限

单次 SMTP 会话中 RCPT TO 命令数量超过接收 MTA 的 `smtpd_recipient_limit`（Postfix 默认 1000）。发送方 MTA 应在 Sendmail `queue_run_recipient_limit` / Postfix `default_destination_recipient_limit` 层面对单次投递的收件人数量做分块。此错误是临时性的——发送方应降低并发分组大小后重试。

### 2.9 421 4.4.7 — 连接超时与目标主机无响应

发送方在 `smtp_connect_timeout`（Postfix 默认 30 秒）期间未能完成 TCP 三次握手。与 4.4.1（连接建立后无响应）的区别在于 TCP 层状态：4.4.7 为 SYN\_SENT 超时，4.4.1 为 ESTABLISHED 但未收到 220 问候消息。

```
# 递送重试日志示例
Jul 15 14:22:10 mx1 postfix/smtp[28471]: connect to gmail-smtp-in.l.google.com
  [142.250.141.26]:25: Connection timed out
Jul 15 14:22:10 mx1 postfix/smtp[28471]: A1B2C3D4E5:
  to=<user@gmail.com>, relay=none, delay=30, delays=0.03/0/30/0,
  dsn=4.4.7, status=deferred (connect to gmail-smtp-in.l.google.com
  [142.250.141.26]:25: Connection timed out)
```

## 3. Postfix 队列诊断工具链

### 3.1 qshape — 延迟分布分析

`qshape` 读取 Postfix 队列文件（不经过队列管理器），按域、按指数级增长的延迟桶统计邮件分布。输出格式为 `T 5 10 20 40 80 160 320 640 1280 1280+`（分钟）。

```
$ qshape active
               T  5 10 20 40 80 160 320 640 1280 1280+
     TOTAL   342 12  8 45 67 51  42  38  35   22   22
 gmail.com   87  3  1  5 12 15  14  13  12    7    5
outlook.com  45  2  2  8  9  7   5   5   4    2    1
yahoo.com    28  1  1  4  7  5   4   3   2    1    0
```

1280+ 列（超过21小时的邮件）应立即关注——这些邮件在剩余队列生命周期内仅剩一次重试机会。持续积累的 `gmail.com` 1280+ 邮件指示 MX 端口 25 出站防火墙阻断而非对端反垃圾策略。

### 3.2 队列邮件内容抽取

```
# 查看特定队列文件的 RFC 5322 头
$ postcat -q A1B2C3D4E5 | head -30

# 按域提取 deferred 队列邮件 ID
$ mailq | awk '/@gmail\.com/ && /^[A-F0-9]{10,}/ {print $1}' > /tmp/gmail-ids.txt

# 提取队列ID的完整递送日志时间线
$ while read id; do echo "=== $id ==="; grep "$id" /var/log/maillog; done < /tmp/gmail-ids.txt
```

## 4. Received 头链分析

Received 头按时间倒序排列——最顶部的一行为邮件抵达当前服务器的最晚一跳。RFC 5321 §4.4 规定格式为 "from <EHLO-hostname> (<EHLO-hostname> [<IP>]) by <receiving-hostname> (<MTA-name>) with <proto> id <queue-id> for <recipient>; <timestamp>"。

```
Received: from mx1.sender.com (mx1.sender.com [203.0.113.10])
    by mail.receiver.net (Postfix 3.8.0) with ESMTPS id 4KxYqQ0rXnz8N
    for <recipient@receiver.net>; Tue, 15 Jul 2026 14:22:31 +0800 (CST)
```

`with ESMTPS` 指示 TLS 加密传输；`with ESMTP` 为明文。检查每跳时间戳偏差——同一秒内的连续跳跃为正常 MTA 转发，超过 5 秒的跳跃指示网络延迟或队列等待。跟踪多跳 Received 头可还原完整投递路径，是排查中继环路和路由绕行的主要手段。

## 5. Telnet 手动 SMTP 调试

手动 SMTP 会话模拟是排除网络层和协议层问题的最直接方法。关键命令序列：

```
$ telnet mx.example.com 25
220 mx.example.com ESMTP Postfix (Debian/GNU)
EHLO debug.client.com
250-mx.example.com
250-PIPELINING
250-SIZE 31457280
250-ETRN
250-STARTTLS
250-ENHANCEDSTATUSCODES
250-8BITMIME
250-DSN
250 SMTPUTF8
MAIL FROM:<sender@example.org> SIZE=1234
250 2.1.0 Ok
RCPT TO:<recipient@example.org>
550 5.1.1 <recipient@example.org>: Recipient address rejected: User unknown
QUIT
221 2.0.0 Bye
```

关键观察点：(a) 220 问候行中的 MTA 标识——Postfix/Sendmail/Exchange/Cisco ESA 使用不同的默认问候字符串；(b) `ENHANCEDSTATUSCODES` 广告位存在性决定后续错误是否携带 X.Y.Z 编码；(c) `STARTTLS` 广告位指示有机会性加密能力；(d) SIZE 参数公布接收方接受的最大邮件字节数——发送超过此值将触发 552 5.3.4。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/smtp-error-codes-master-guide.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
