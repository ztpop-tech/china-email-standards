---
title: "SMTP 协议深度解析 — RFC 5321：从 HELO/EHLO 到 QUIT 的全链路传输与扩展框架"
source: "https://ztpop.net/kb/smtp-protocol-deep-dive.html"
license: CC-BY 4.0
---

# SMTP 协议深度解析 — RFC 5321：从 HELO/EHLO 到 QUIT 的全链路传输与扩展框架

## 1. 存储转发模型与中继概念

### 1.1 SMTP 的架构设计：存储转发（Store-and-Forward）

SMTP 协议从根本上说是一个
**存储转发**
（Store-and-Forward）协议。RFC 5321 第 2.1 节明确描述了 SMTP 的基本模型：发送方 SMTP 客户端与接收方 SMTP 服务器建立 TCP 连接（默认端口 25），然后在同一个连接中完成握手、信封协商和邮件数据传输。如果下一跳不可达，邮件不会丢失，而是由当前 MTA（Mail Transfer Agent）暂存到本地队列中，等待后续重试。

这里的核心逻辑是
**逐跳传递**
（hop-by-hop），而不是端到端的直连。一封邮件从发件人到达收件人，可能需要经过多台 SMTP 服务器：发送方 MUA → 提交 MSA（Message Submission Agent，端口 587）→ 本地 MTA → 外部中继 MTA → 目标 MX 主机 → 收件方 MDA → 收件人 MUA。每一跳都是一个独立的 SMTP 事务，每个事务都包含独立的 MAIL FROM / RCPT TO 信封交换。

**关键概念 — MTA 队列**
  
当下一跳 SMTP 服务器不可达时，MTA 将消息写入队列目录（典型路径如
`/var/spool/postfix/deferred/`
），按既定重试策略周期性尝试重新投递。RFC 5321 第 4.5.4 节规定了推荐的重试间隔：初始重试至少每 30 分钟一次，随后逐步退避，发件人必须在 4-5 天后生成不可投递通知（NDN / bounce message）。

### 1.2 MX 记录与邮件路由

SMTP 的寻址不直接面向 IP 地址，而是依赖 DNS 中的
**MX（Mail eXchange）记录**
。发送方 MTA 查收件人域名（如
`@example.com`
）的 MX 记录，获取一个按优先级排序的接收服务器列表。RFC 5321 第 5.1 节指出：MX 记录优先级值越低，优先级越高；当最高优先级的 MX 不可达时，发送方应当尝试次高优先级的 MX（回退，fallback）。如果目标域没有任何 MX 记录，SMTP 发送方应回退到该域的 A 或 AAAA 记录。

```
; 查询 example.com 的 MX 记录
$ dig example.com MX +short
10 mail1.example.com.
20 mail2.example.com.
```

### 1.3 中继（Relay）与开放中继

中继是指一台 SMTP 服务器接收来自外部的邮件并将其转发给另一个域。正常的邮件流转中，MTA 会对"本地域"和"外部域"区分处理——本地域（
`mydestination`
）的邮件直接投递到用户邮箱，外部域的邮件通过 relayhost 或 MX 查询中继出去。

开放中继（Open Relay）是指 SMTP 服务器不对发送方做身份检查，无差别接收并转发所有域的邮件。这种服务器很快就会被垃圾邮件发送者利用、被公共黑名单收录（如 Spamhaus、SORBS），导致正常外发邮件也被拒收。

**RFC 5321 第 3.6 节 — 中继控制**
  
RFC 5321 明确规定：SMTP 服务器可以基于连接 IP、HELO/EHLO 域名、MAIL FROM 或 RCPT TO 地址等信息的组合来实施中继策略。默认情况下，未经认证的连接不应当被允许向远程域中继邮件。

## 2. SMTP 会话三阶段

一次完整的 SMTP 会话可以清晰地划分为三个阶段：握手（Handshake）、传输（Transaction）、结束（Termination）。下面用一个实际的 telnet 会话例子来演示全流程。

### 2.1 阶段一：握手 — HELO / EHLO

客户端成功建立 TCP 连接到服务器的 25 端口后，服务器首先发送 220 欢迎消息。客户端随后发送
`HELO`
（或
`EHLO`
）标识自己的身份。

HELO 参数是一个 FQDN（Fully Qualified Domain Name）或地址字面量（address literal）。RFC 5321 第 4.1.1.1 节指出 HELO/EHLO 的参数应当是发送方的合法域名，现代反垃圾检查会严格验证这个参数。

# 建立 TCP 连接到 SMTP 服务器 25 端口

$ telnet mail.example.com 25

220 mail.example.com ESMTP Postfix

# 客户端发送 EHLO（ESMTP 握手）

EHLO sender.example.org

250-mail.example.com

250-PIPELINING

250-SIZE 26214400

250-STARTTLS

250-8BITMIME

250-SMTPUTF8

250 CHUNKING

### 2.2 阶段二：传输 — 信封与数据

握手完成后进入邮件传输阶段。RFC 5321 第 4.1.1.2 节定义了标准的事务序列：

2.2 阶段二：传输 — 信封与数据

| 命令 | 作用 | RFC 5321 章节 |
| --- | --- | --- |
| `MAIL FROM:` | 指定信封发件人（Return-Path），可为空（ `<>` ） | 4.1.1.2 |
| `RCPT TO:` | 指定信封收件人，可重复多次（多收件人） | 4.1.1.3 |
| `DATA` | 开始传输邮件正文（头部 + 正文，以 `.` 结束） | 4.1.1.4 |
| `RSET` | 重置当前事务，清除所有信封状态 | 4.1.1.5 |
| `VRFY` | 验证邮箱地址是否存在 | 4.1.1.6 |
| `NOOP` | 无操作，服务器返回 250 OK（保活探测） | 4.1.1.9 |

# MAIL FROM — 指定信封发件人

MAIL FROM:

250 2.1.0 Ok

# RCPT TO — 指定信封收件人

RCPT TO:

250 2.1.5 Ok

# DATA — 开始传输数据

DATA

354 End data with .

# 邮件头部和正文（RFC 5322 格式）
From: "Alice" 
To: bob@example.com
Subject: Hello from SMTP
Date: Sat, 04 Jul 2026 16:00:00 +0800
This is the message body.
And a second line.
.

250 2.0.0 Ok: queued as 7B3F1A0B2C

注意
`DATA`
阶段的数据内容同时包含邮件头部（RFC 5322 格式）和邮件正文，两者用空行分隔。服务器从
`MAIL FROM`
/
`RCPT TO`
获取的是 SMTP 信封信息（envelope），而
`DATA`
内的
`From:`
/
`To:`
头部属于信头（message header），这两个层面在概念上完全独立。

### 2.3 阶段三：结束 — QUIT

数据传输完成后，客户端发出
`QUIT`
命令结束会话。RFC 5321 第 4.1.1.10 节规定了 QUIT 的语义：服务器响应 221 关闭码并终止 TCP 连接。

QUIT

221 2.0.0 Bye

Connection closed by foreign host.

如果在事务中途（例如 RCPT TO 返回永久失败）需要取消当前事务但不关闭连接，应当使用
`RSET`
而非
`QUIT`
`RSET`
清空所有信封状态，恢复到握手完成后的状态，可以接着开始一个新事务。

## 3. 信封 vs 信头：RFC 5321 信封与 RFC 5322 头部

这是 SMTP 协议中最重要、也最容易被误解的概念区别。

### 3.1 RFC 5321 信封（Envelope）

信封（envelope）是在 SMTP 协议层通过
`MAIL FROM`
和
`RCPT TO`
命令交换的信息。RFC 5321 第 2.3.1 节将信封发件人称为
**Reverse-Path**
，将信封收件人称为
**Forward-Path**
。这两个字段是 SMTP 路由和投递的
**实际依据**
—— MTA 只看信封，不看头部。

信封发件人会在投递后被记录为邮件头部的
`Return-Path:`
字段。如果投递失败，反弹消息（bounce）将被发送到这个地址。邮件列表软件大量使用这一机制——将反弹邮件导向专门的 VERP 地址而非原始发件人。

### 3.2 RFC 5322 头部（Message Header）

消息头部存在于
`DATA`
命令传输的数据块内部，由 RFC 5322（取代了 RFC 2822）定义格式。其中
`From:`
、
`To:`
、
`Subject:`
、
`Date:`
等字段是 MUA（邮件客户端）向最终用户展示的信息，与 SMTP 路由无关。

### 3.3 三个关键发件人字段的区别

3.3 三个关键发件人字段的区别

| 字段 | 来源 | 用途 | 用户可见 |
| --- | --- | --- | --- |
| `MAIL FROM` （Reverse-Path） | SMTP 命令 | 路由、反弹、SPF 检查 | 不直接可见 → 投递后写入 `Return-Path:` |
| `From:` （RFC 5322 Header） | DATA 内的头部 | 邮件客户端展示"发件人" | 是 |
| `Sender:` （RFC 5322 Header） | DATA 内的头部 | 代发场景的表征：实际发送者 ≠ 名义发件人时使用 | 部分客户端展示 |

**实际案例**
  
邮件列表服务（如 Mailman）的行为是典型的信封/信头分离场景：
  
`MAIL FROM:`
（信封，用于接收 bounce）
  
而
`From: alice@gmail.com`
（头部，用于展示原始发件人）
  
当邮件无法送达时，DSN 通知被发往
`list-bounces@example.org`
，不会骚扰到发件人 alice。

SPF（Sender Policy Framework）验证的是
`MAIL FROM`
域名，即
**RFC 5321.MailFrom**
域（也记作 RFC 5321 From 或 Envelope-From），而非头部
`From:`
。理解这一点对 SPF 配置和排错都很关键。

## 4. ESMTP 扩展机制：EHLO 协商

### 4.1 从 HELO 到 EHLO 的演进

原始 RFC 821（1982 年，由 Jonathan B. Postel 定义）仅使用
`HELO`
作为握手命令，功能极为简单。随着互联网的发展，8bit 传输、认证、加密、流水线等需求不断涌现，RFC 1869（1995 年）引入了
**ESMTP 服务扩展框架**
，RFC 2821 整合了该框架，RFC 5321 在第 2.2 节对扩展机制做了进一步规范化。

ESMTP 的核心思想是：客户端使用
`EHLO`
替代
`HELO`
向服务器声明自己支持扩展；服务器在 250 多行响应中列出自身支持的扩展关键字。如果服务器不支持扩展，会返回 500 错误，客户端此时应回退到
`HELO`
。

### 4.2 EHLO 响应解析

RFC 5321 第 2.2 节定义的扩展注册机制要求每个扩展关键字在 IANA 注册。下面是典型的 EHLO 响应格式，注意最后一行以 "250 "（空格）而非 "250-"（连字符）开头，表示多行响应结束：

```
250-mail.example.com
250-PIPELINING
250-SIZE 52428800
250-ETRN
250-STARTTLS
250-ENHANCEDSTATUSCODES
250-8BITMIME
250-DSN
250-SMTPUTF8
250 CHUNKING
```

4.2 EHLO 响应解析

| 扩展关键字 | RFC | 核心功能 |
| --- | --- | --- |
| `PIPELINING` | RFC 2920 | 允许客户端批量发送多条命令而不等待每条回复，减少 RTT 开销 |
| `8BITMIME` | RFC 6152 | 声明支持 8-bit MIME 内容，无需 quoted-printable/base64 编码传输 |
| `CHUNKING` | RFC 3030 | 用 `BDAT` 命令替代 `DATA` ，按块传输邮件数据，支持精确大小声明 |
| `SIZE` | RFC 1870 | 声明服务器可接受的最大邮件大小（字节），客户端用 `SIZE=` 参数查询 |
| `STARTTLS` | RFC 3207 | 在现有 SMTP 连接上启动 TLS 加密升级 |
| `ENHANCEDSTATUSCODES` | RFC 3463 | 启用增强型状态码（如 `5.1.1` 而非单纯 `550` ） |
| `DSN` | RFC 3461 | 投递状态通知：允许客户端请求 delivery/failure/delay 通知 |
| `SMTPUTF8` | RFC 6531 | 允许信封地址和头部使用 UTF-8 字符（国际化邮件地址/EAI） |
| `AUTH` | RFC 4954 | 启用 SMTP 认证（PLAIN / LOGIN / CRAM-MD5 等 SASL 机制） |

### 4.3 STARTTLS 协商

STARTTLS（RFC 3207）是 SMTP 协议中最常用的传输层加密方式。它在已建立的明文 SMTP 连接上通过 STARTTLS 命令升级到 TLS。这个过程不需要额外端口——这是与 SMTPS（465 端口，隐式 TLS）的主要区别。

```
# 使用 openssl s_client 连接并触发 STARTTLS
$ openssl s_client -starttls smtp -connect mail.example.com:25 -crlf

# 或先 telnet，EHLO 后手动触发
$ telnet mail.example.com 25
EHLO client.local
250-STARTTLS
STARTTLS
220 2.0.0 Ready to start TLS
# 此时连接已升级为 TLS
```

## 5. SMTP 响应码体系

### 5.1 基本响应码结构

RFC 5321 第 4.2 节定义了 SMTP 响应的格式：三位数字 + 可选的文本描述。响应的第一位数决定语义分类，第二位数细化功能类别。每条响应可以是单行（
`250 OK`
）或多行（最后一行以空格开头而非连字符）。

5.1 基本响应码结构

| 首位数字 | 含义 | 示例 |
| --- | --- | --- |
| 2yz | 命令成功完成 | `250 OK` 、 `221 Bye` 、 `220 Ready` |
| 3yz | 命令被接受，但需要更多输入才能完成 | `354 Start mail input` 、 `334` |
| 4yz | 临时失败：重试可能成功 | `421 Service not available` 、 `450 Mailbox unavailable` 、 `451 Local error` 、 `452 Insufficient storage` |
| 5yz | 永久失败：不应重试同一参数 | `550 Mailbox not found` 、 `551 User not local` 、 `554 Transaction failed` |

**4xx vs 5xx 的实践差异**
  
这是 SMTP 生产运维中最需要区分的概念：遇到 4xx 响应，发送方 MTA 将邮件留在延迟队列，按退避策略重试（可达数天）。遇到 5xx 响应，发送方 MTA 立即放弃投递，生成不可投递通知（bounce）。将 5xx 误判为 4xx 意味着永久失败被掩盖；而将 4xx 误判为 5xx 则导致可以成功重试的邮件被过早放弃。

### 5.2 增强型状态码（Enhanced Status Codes）

如果服务器在 EHLO 响应中宣告了
`ENHANCEDSTATUSCODES`
（RFC 3463），响应码会附加
`X.Y.Z`
三位分层编码：

```
550 5.1.1 The email account that you tried to reach does not exist
```

这里的
`5.1.1`
含义：5 = 永久失败，1 = 地址问题（addressing status），1 = 邮箱不存在（bad destination mailbox address）。增强型状态码让邮件系统和日志分析工具可以精确区分失败原因，而不是面对一堆无差别的 550。

### 5.3 常用响应码速查

5.3 常用响应码速查

| 响应码 | 含义 | 出现场景 |
| --- | --- | --- |
| `220` | 服务就绪 | TCP 连接建立后服务器的第一条消息 |
| `221` | 服务关闭 | 响应 QUIT 命令 |
| `250` | 操作成功 | EHLO、MAIL FROM、RCPT TO、DATA 完成等 |
| `334` | AUTH 认证质询 | 服务器发送 Base64 编码的 challenge |
| `354` | 开始数据输入 | 响应 DATA 命令 |
| `421` | 服务暂时不可用 | 连接即将关闭，客户端应稍后重试 |
| `450` | 邮箱不可用（临时） | 例如邮箱被锁定、磁盘满 |
| `451` | 本地处理错误（临时） | 内部错误、处理超时 |
| `452` | 存储不足（临时） | 磁盘空间不足 |
| `500` | 命令语法错误 | 不认识的命令或语法格式错误 |
| `501` | 参数语法错误 | 命令参数格式不正确 |
| `502` | 命令未实现 | 如服务器不支持 VRFY |
| `550` | 邮箱不存在（永久） | 收件地址无效或拒绝投递 |
| `552` | 超出存储限制（永久） | 邮件过大且超出服务器限制 |
| `554` | 事务失败（永久） | 泛用型永久失败 |

## 6. 核心扩展详解

### 6.1 PIPELINING（RFC 2920）

默认的 SMTP 是严格的"命令-响应"同步协议：客户端发一条命令，必须等待服务器回复后，才能发下一条。这对高延迟链路（跨大洲、卫星链路）带来的开销很大。PIPELINING 允许客户端一次性批量发送多条 SMTP 命令，服务器按顺序逐一回复。

```
# 启用 PIPELINING 后可以一次性发送所有信封命令
# 然后批量接收回复
EHLO client.local
MAIL FROM: SIZE=1234
RCPT TO:
RCPT TO:
DATA
# 服务器依次返回：250, 250, 250, 250, 354
```

PIPELINING 的关键限制：在事务边界处不能流水线。具体来说，在
`DATA`
完成后（即
`.`
发送完毕并收到 250 回复前）不能流水线新命令。同样，使用 CHUNKING 时，
`BDAT LAST`
之后必须等待响应。

### 6.2 8BITMIME（RFC 6152）

传统 SMTP 仅支持 7-bit ASCII 传输（RFC 821 时代的约束）。任何 8-bit 数据都必须先用 quoted-printable 或 base64 编码。8BITMIME 扩展让服务器宣告可以接受原始 8-bit 字节。客户端在
`MAIL FROM`
命令中添加
`BODY=8BITMIME`
参数来声明：

```
MAIL FROM: BODY=8BITMIME
```

如果服务器不支持但邮件确实是 8-bit 内容，典型表现是某些字节被截断（strip 高位），导致乱码。在生产环境中，即使双方都支持 8BITMIME，很多管理员仍然强制使用 base64，因为在多跳中继场景中，中间任意一跳不支持就可能导致内容损坏。

### 6.3 CHUNKING / BDAT（RFC 3030）

传统
`DATA`
命令有一个设计缺陷：服务器在接收数据之前不知道邮件的精确大小，只能靠接收缓冲区。CHUNKING 引入
`BDAT`
命令，每个块携带精确的字节数，最后一个块标记
`LAST`
：

```
BDAT 512
(512 字节数据块内容)
250 2.0.0 Ok
BDAT 1024 LAST
(1024 字节数据块内容，这是最后一块)
250 2.0.0 Ok: queued as 8F3B1A0B2C
```

CHUNKING 的核心优势是消除了传统
`DATA`
的"点转义"问题——不再需要对以
`.`
开头的行做
`..`
转义。RFC 5321 第 4.5.2 节描述的透明性问题是传统 DATA 模式下长期存在的痛点，而 CHUNKING 彻底解决了这个问题。

### 6.4 SIZE（RFC 1870）

SIZE 扩展在 EHLO 响应中声明服务器可接受的最大邮件大小。客户端可以在
`MAIL FROM`
命令中携带
`SIZE=`
参数来预声明邮件大小，服务器如果判断超出限制可以
**在接收数据之前**
就拒绝：

```
EHLO client.local
250-SIZE 26214400
250 STARTTLS

MAIL FROM: SIZE=30000000
552 5.3.4 Message size exceeds fixed limit
```

RFC 5321 第 4.5.3.1 节规定，SMTP 服务器最低必须能处理总大小为 64KB 的消息。这个最低要求在实践中已远远不够，现代邮件系统典型配置为 10MB 到 50MB。

### 6.5 SMTPUTF8（RFC 6531 — 国际化邮件地址）

传统 SMTP 的地址（MAIL FROM、RCPT TO）和邮件头部都严格限制在 7-bit ASCII。SMTPUTF8 扩展（由 RFC 6531 定义，是 Internationalized Email / EAI 体系的核心组成）允许使用 UTF-8 字符编码的邮箱地址和头部字段。这意味着像
`用户@例子.中国`
这样的国际化地址在端到端支持 EAI 的链路上可以原生传输：

```
EHLO smtp.example.com
250-SMTPUTF8
250-8BITMIME
...
MAIL FROM:<用户@例子.中国> SMTPUTF8
250 2.1.0 Ok
```

SMTPUTF8 要求链路上所有 MTA 都支持，中间任何中转站不支持时，地址体验会自动降级为 ASCII 替代形式（ACE，即 Punycode 编码的域名部分）。RFC 6531 的落地推进较慢，主要阻碍在于大量遗留系统不支持。

### 6.6 DSN — 投递状态通知（RFC 3461）

DSN（Delivery Status Notification）允许发送方客户端通过
`RCPT TO`
命令中的附加参数请求服务器在投递完成（成功、失败或延迟）时发送通知邮件。RFC 3461 定义了以下关键参数：

* `NOTIFY=NEVER`
  /
  `NOTIFY=SUCCESS`
  /
  `NOTIFY=FAILURE`
  /
  `NOTIFY=DELAY`
  ：指定需要通知的事件类型
* `ENVID=`
  ：客户端分配的事务标识，DSN 通知中会原样回传
* `ORCPT=rfc822;`
  ：原始收件人地址（支持别名展开时的追溯）

```
RCPT TO: NOTIFY=SUCCESS,FAILURE ORCPT=rfc822;original@olddomain.com
```

## 7. SMTP 认证：AUTH 框架

### 7.1 RFC 4954 — SMTP 服务认证扩展

RFC 4954（2007 年，取代了早期 RFC 2554）规范了 SMTP 的 AUTH 命令。AUTH 扩展基于 SASL（Simple Authentication and Security Layer，RFC 4422）框架，定义了 SMTP 服务器验证客户端身份的标准化方式。

### 7.2 常用 AUTH 机制对比

7.2 常用 AUTH 机制对比

| 机制 | 安全特性 | 实现复杂度 | 典型使用场景 |
| --- | --- | --- | --- |
| `PLAIN` | 密码明文传输（Base64 编码但不加密） | 低 | 仅在与 STARTTLS 配合时使用 |
| `LOGIN` | 密码明文传输（独立 Base64 编码用户名和密码） | 低 | 大量客户端兼容；必须搭配 TLS |
| `CRAM-MD5` | 质询-响应（Challenge-Response）HMAC-MD5，不传输密码 | 中 | 无 TLS 时提供基本保护；因 MD5 过时已不推荐 |
| `DIGEST-MD5` | 质询-响应 HMAC-MD5，可选完整性保护 | 高 | 日渐减少使用，类似 CRAM-MD5 |
| `XOAUTH2` | OAuth 2.0 Bearer Token（不依赖密码） | 高 | Gmail、Microsoft 365 等现代邮件服务 |
| `SCRAM-SHA-256` | 现代质询-响应，支持通道绑定 | 中 | 当前推荐的安全认证机制 |

### 7.3 AUTH LOGIN 实际交互过程

# AUTH LOGIN — 分步 Base64 交换

AUTH LOGIN

334 VXNlcm5hbWU6

# VXNlcm5hbWU6 = base64("Username:")

dXNlckBleGFtcGxlLmNvbQ==

# dXNlckBleGFtcGxlLmNvbQ== = base64("user@example.com")

334 UGFzc3dvcmQ6

# UGFzc3dvcmQ6 = base64("Password:")

c2VjcmV0cGFzc3dvcmQ=

# c2VjcmV0cGFzc3dvcmQ= = base64("secretpassword")

235 2.7.0 Authentication successful

**安全提示**
：PLAIN 和 LOGIN 机制在任何非 TLS 通道上使用等同于明文传输密码。所有现代 SMTP 部署都应当要求
`AUTH`
必须在 STARTTLS 之后进行。Postfix 通过
`smtpd_tls_auth_only = yes`
强制实施这一约束。

### 7.4 swaks 认证测试

swaks（Swiss Army Knife for SMTP）是 SMTP 调试的利器。下面演示用 swaks 测试 SMTP AUTH：

```
# 测试 PLAIN 认证
$ swaks --to rcpt@example.com --from sender@example.org \
  --server mail.example.com --port 587 \
  --auth PLAIN --auth-user user@example.com --auth-password 'password' \
  --tls

# 等价的手动 telnet + openssl 方式
$ openssl s_client -starttls smtp -connect mail.example.com:587 -crlf -quiet
EHLO test.local
AUTH PLAIN AHVzZXJAZXhhbXBsZS5jb20AcGFzc3dvcmQ=
235 2.7.0 Authentication successful
```

## 8. 反垃圾邮件相关技术

### 8.1 反向 DNS（PTR）与 FCrDNS

反向 DNS（rDNS）查询返回一个 IP 地址对应的域名（PTR 记录）。FCrDNS（Forward-Confirmed Reverse DNS）要求同时满足两个条件：

1. IP 地址的反向解析（PTR 记录）返回一个域名
2. 该域名的正向解析（A/AAAA 记录）能返回到原 IP 地址

这形成了一个闭环验证。许多接收方 MTA 将 FCrDNS 验证结果作为垃圾邮件评分的一个重要信号。如果一个连接 IP 完全没有 PTR 记录，或者 PTR 域名看起来像动态 IP 分配（如
`xxx.dynamic.example-isp.net`
），这通常会导致较高的垃圾评分。

```
# 反向解析：IP → 域名（PTR）
$ dig -x 203.0.113.25 +short
mail.example.com.

# 正向解析：域名 → IP（A），验证一致性
$ dig mail.example.com. A +short
203.0.113.25
# 两次查询结果一致 → FCrDNS 通过
```

### 8.2 HELO/EHLO 域名验证

RFC 5321 第 4.1.4 节规定：SMTP 客户端在 HELO/EHLO 命令中传递的域名是一个 FQDN（完全限定域名）或者 IP 地址字面量。现代反垃圾策略会检查：

* HELO 参数是否为合法 FQDN 格式（不能是裸 IP 字符串如
  `[192.168.1.1]`
  以外的形式）
* HELO 域名是否能够通过 DNS 解析到有效 IP
* HELO 域名与连接 IP 的 PTR 记录是否匹配或有关联
* HELO 域名是否包含已知的动态 IP 模式（如
  `*.dynamic.*`
  ）

### 8.3 SPF、DKIM、DMARC 与 SMTP 信封的关系

这三项验证技术的生效位置各不相同：

* **SPF**
  （RFC 7208）验证
  `MAIL FROM`
  域名（信封域），与头部
  `From:`
  无关。检查的是连接 IP 是否被发件人域名的 SPF 记录授权。
* **DKIM**
  （RFC 6376）验证邮件头部的数字签名。签名域（
  `d=`
  ）与信封无关。DKIM 可以跨转发链存活。
* **DMARC**
  （RFC 7489）要求 SPF（信封对齐）和/或 DKIM（签名对齐）与头部
  `From:`
  域对齐（alignment）。这是将信封层面与头部层面串联起来的桥梁。

## 9. Postfix SMTP 客户端行为配置

### 9.1 relayhost：指定出站中继

relayhost 是 Postfix SMTP 客户端最基础的出站配置。当 Postfix 自身不直接对互联网投递，而是将所有外发邮件转交到另一台中继服务器（如 ISP 的 SMTP 网关或第三方邮件中继服务）时使用：

```
# /etc/postfix/main.cf
relayhost = [smtp-relay.example.com]:587
smtp_sasl_auth_enable = yes
smtp_sasl_password_maps = hash:/etc/postfix/sasl_passwd
smtp_sasl_security_options = noanonymous
smtp_tls_security_level = encrypt
```

方括号
`[]`
告诉 Postfix 跳过 MX 查询，直接将给定的主机名作为 IP 解析目标。这在与中继服务通信时几乎总是需要的——MX 查询会返回中继服务自身的 MX 记录，而非你想连接的 SMTP 边缘服务器。

### 9.2 transport\_maps：按域路由

transport\_maps 提供比 relayhost 更精细的控制——按收件人域名将邮件路由到不同的中继服务器或使用不同的传输方式：

```
# /etc/postfix/transport
# 域            传输方式:目标
partner.com     relay:[mx.partner.com]:25
corp.local      smtp:[192.168.1.50]:25
bigfile.org     smtp:inbound.bigfile.org:587
*               smtp:[relay.isp.com]:587

# 生成哈希
$ postmap /etc/postfix/transport
```

在 main.cf 中引用：
`transport_maps = hash:/etc/postfix/transport`

### 9.3 smtp\_tls\_policy：TLS 策略

Postfix 提供分层的 TLS 策略控制。全局的
`smtp_tls_security_level`
（main.cf 级别）设置默认行为，而
`smtp_tls_policy_maps`
允许按目标域指定不同策略：

```
# /etc/postfix/tls_policy
# 域                    TLS 策略
partner-bank.com        encrypt protocols=TLSv1.2 ciphers=high
legacy-vendor.com       may
untrusted-host.org      none
.example.com            secure match=.example.com

# 生成哈希
$ postmap /etc/postfix/tls_policy

# main.cf
smtp_tls_policy_maps = hash:/etc/postfix/tls_policy
```

策略选项说明：
`none`
（不使用 TLS）、
`may`
（尝试 STARTTLS 但不要求，如果对方不支持则回退明文）、
`encrypt`
（必须加密，但不验证证书）、
`secure`
（必须加密且验证证书）、
`verify`
（必须加密且验证证书和主机名，最严格）。

### 9.4 队列管理与重试策略

RFC 5321 第 4.5.4 节定义了最小重试间隔和最终放弃时间的推荐值。Postfix 通过以下参数控制对应行为：

```
# Postfix main.cf 中的队列和重试参数
maximal_queue_lifetime = 5d
# 邮件在队列中的最大存活时间；过期后生成 bounce。RFC 5321 第 4.5.4 节推荐至少 4-5 天。

bounce_queue_lifetime = 5d
# bounce 消息本身的最大存活时间

minimal_backoff_time = 300s
# 最小重试间隔。RFC 5321 推荐初始重试至少间隔 30 分钟，但 Postfix 默认设为 300s。

maximal_backoff_time = 4000s
# 最大退避时间（指数退避的上限）

queue_run_delay = 300s
# 队列扫描间隔
```

```
# 查看当前队列状态
$ mailq
# 或
$ postqueue -p

# 强制刷新所有延迟队列（立即重试）
$ postqueue -f

# 刷新特定域的延迟队列
$ postqueue -s example.com

# 删除特定发件人的所有延迟邮件
$ mailq | tail -n +2 | awk 'BEGIN { RS = "" } /sender@spam\.com/ { print $1 }' \
  | tr -d '*!' | postsuper -d -
```

## 10. 排错工具箱与诊断方法

### 10.1 swaks：SMTP 瑞士军刀

swaks 是 SMTP 调试的单一最强大工具。它能独立测试从握手到数据传输的每一个阶段：

```
# 基础连接测试
$ swaks --to test@example.com --server mail.example.com --port 25

# 测试 TLS + AUTH
$ swaks --to test@example.com --server mail.example.com --port 587 \
  --tls --auth PLAIN --auth-user user@example.com --auth-password 'pass'

# 测试 EHLO 扩展列表
$ swaks --to test@example.com --server mail.example.com --ehlo-only

# 测试 SIZE 限制
$ swaks --to test@example.com --server mail.example.com \
  --from sender@example.org --data /path/to/large_message.eml \
  --header-X-Test yes

# 管道输出：发送邮件并查看全部 SMTP 协议对话
$ swaks --to test@example.com --server mail.example.com -q HELO 2>&1 | tee smtp.log
```

### 10.2 telnet / nc：裸协议调试

当 swaks 不在手边时，telnet 是最直接的替代方案：

```
# 基本 telnet 会话
$ telnet mail.example.com 25
EHLO test.local
MAIL FROM:
RCPT TO:
DATA
From: sender@example.org
To: rcpt@example.com
Subject: Test
.
QUIT
```

对于需要查看完整 TLS 握手过程的情况，使用
`openssl s_client`
：

```
# SMTP + STARTTLS
$ openssl s_client -starttls smtp -connect mail.example.com:587 -crlf -quiet

# SMTPS（465 端口，隐式 TLS）
$ openssl s_client -connect mail.example.com:465 -crlf -quiet
```

### 10.3 tcpdump：抓包分析

当问题无法在应用层复现时，需要抓包分析。SMTP 使用标准的 TCP 协议，tcpdump 可以直接抓取明文 SMTP 通信（在 STARTTLS 之前的部分）：

```
# 抓取到目标 SMTP 服务器的流量
$ tcpdump -i eth0 -s 0 -A 'host mail.example.com and port 25'

# 抓取并保存为 pcap 文件（供 Wireshark 分析）
$ tcpdump -i eth0 -s 0 -w smtp_capture.pcap 'tcp port 25 or tcp port 587'

# 在 Wireshark 中可以用过滤器 "smtp" 快速定位 SMTP 数据包
```

### 10.4 Postfix 日志诊断

Postfix 的 syslog 日志包含了诊断 SMTP 投递过程的全部信息。日志中每条记录有唯一的队列 ID，可以串联跟踪一封邮件从收到到最终投递（或 bounce）的完整生命周期。

```
# 跟踪特定邮件 ID 的完整投递路径
$ grep '7B3F1A0B2C' /var/log/maillog

# 典型日志解读：
# Jul  4 16:00:01 host postfix/smtpd[12345]: 7B3F1A0B2C: client=unknown[192.168.1.100]
#   → 从 IP 192.168.1.100 收到邮件
# Jul  4 16:00:02 host postfix/cleanup[12346]: 7B3F1A0B2C: message-id=
#   → cleanup 处理完成
# Jul  4 16:00:03 host postfix/qmgr[12347]: 7B3F1A0B2C: from=,
#   size=1234, nrcpt=1 (queue active)
#   → 进入活跃队列
# Jul  4 16:00:05 host postfix/smtp[12348]: 7B3F1A0B2C: to=,
#   relay=mail.example.com[203.0.113.25]:25, delay=4, delays=2/1/0.5/0.5, dsn=2.0.0,
#   status=sent (250 2.0.0 Ok: queued as ABC123)
#   → 成功投递到 mail.example.com，耗时 4 秒
```

关键延迟字段分解：
`delays=a/b/c/d`
分别对应队列排队时间 / 地址解析时间 / SMTP 连接建立时间 / SMTP 协议对话时间（均以秒计）。如果
`a`
值很大，说明队列拥塞；如果
`c`
值很大，说明网络或对方服务器有问题。

### 10.5 常见问题排查清单

10.5 常见问题排查清单

| 症状 | 常见原因 | 诊断命令 |
| --- | --- | --- |
| 邮件卡在队列中不发 | MTA 未运行、网络不可达、下一跳 MX 宕机 | `postfix status` 、 `mailq` 、 `telnet  25` |
| 收到 4xx 临时失败且不恢复 | 目标服务器 greylisting、IP 信誉低 | `grep 'status=deferred' /var/log/maillog` 、swaks 测试 |
| 收到 5xx 永久拒绝 | SPF/DKIM/DMARC 失败、黑名单、地址不存在 | 查看 bounce 内容中 `Diagnostic-Code` 字段 |
| SSL/TLS 握手失败 | 协议版本不匹配、证书过期、CA 不可信 | `openssl s_client -starttls smtp -connect` |
| 邮件被标记为垃圾邮件 | PTR 缺失、SPF 未配置、DKIM 未签名、内容得分高 | SpamAssassin 测试、 `dig -x` |
| AUTH 认证失败 | 密码错误、机制不支持、TLS 未启用 | swaks --auth 测试、查看服务器 AUTH 日志 |
| 网络连接超时 | 防火墙规则、出站端口 25 被封锁、GRE 隧道问题 | `tcpdump -i eth0 port 25` 、 `iptables -L` |

## 参考文献

1. **RFC 5321**
   — Simple Mail Transfer Protocol, J. Klensin, October 2008.（第 2.1 节：SMTP 模型；第 2.2 节：扩展机制；第 2.3.1 节：邮件对象与信封；第 3.1-3.3 节：会话流程；第 3.6 节：中继与路由；第 4.1 节：命令规范；第 4.2 节：响应码体系；第 4.5.4 节：重试策略；第 4.5.3.1 节：大小限制；第 5.1 节：MX 记录查找）
2. **RFC 5322**
   — Internet Message Format, P. Resnick, October 2008.（邮件头部格式标准，定义了 From:/To:/Subject:/Date: 等字段的语法和语义）
3. **RFC 2821**
   — Simple Mail Transfer Protocol（旧版）, J. Klensin, April 2001.（被 RFC 5321 取代；ESMTP 扩展框架的首次整合）
4. **RFC 3461**
   — SMTP Service Extension for Delivery Status Notifications (DSN), K. Moore, January 2003.（定义了 DSN 扩展和 NOTIFY / ENVID / ORCPT 参数）
5. **RFC 6531**
   — SMTP Extension for Internationalized Email (SMTPUTF8), J. Yao / W. Mao, February 2012.（国际化邮件地址的 SMTPUTF8 扩展）
6. **RFC 4954**
   — SMTP Service Extension for Authentication (AUTH), R. Siemborski / A. Melnikov, July 2007.（SMTP AUTH 命令和 SASL 机制绑定）
7. **RFC 3207**
   — SMTP Service Extension for Secure SMTP over Transport Layer Security (STARTTLS), P. Hoffman, February 2002.
8. **RFC 2920**
   — SMTP Service Extension for Command Pipelining (PIPELINING), N. Freed, September 2000.
9. **RFC 3030**
   — SMTP Service Extensions for Transmission of Large and Binary MIME Messages (CHUNKING / BDAT), G. Vaudreuil, December 2000.
10. **RFC 6152**
    — SMTP Service Extension for 8-bit MIME Transport (8BITMIME), J. Klensin / N. Freed / M. Rose / D. Crocker, March 2011.
11. **RFC 3463**
    — Enhanced Mail System Status Codes, G. Vaudreuil, January 2003.
12. **RFC 7208**
    — Sender Policy Framework (SPF) for Authorizing Use of Domains in Email, S. Kitterman, April 2014.
13. **RFC 6376**
    — DomainKeys Identified Mail (DKIM) Signatures, D. Crocker / T. Hansen / M. Kucherawy, September 2011.
14. **RFC 7489**
    — Domain-based Message Authentication, Reporting, and Conformance (DMARC), M. Kucherawy / E. Zwicky, March 2015.

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/smtp-protocol-deep-dive.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
