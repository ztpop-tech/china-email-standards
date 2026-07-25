---
title: "发件人重写方案 SRS — SPF 转发断链的解决路径：原理、postsrsd 配置与 DMARC 对齐 · ztpop 邮件技术知识库"
source: "https://ztpop.net/kb/srs-sender-rewriting.html"
license: CC-BY 4.0
---

# 发件人重写方案 SRS — SPF 转发断链的解决路径：原理、postsrsd 配置与 DMARC 对齐 · ztpop 邮件技术知识库

发件人重写方案 SRS — SPF 转发断链的解决路径：原理、postsrsd 配置与 DMARC 对齐

## 摘要

SRS（Sender Rewriting Scheme）是一种邮件转发场景中的 envelope-from 地址改写技术，核心目标是修复 SPF（RFC 7208）在邮件转发路径上被"断链"的固有问题。当一个邮件域部署了 SPF
`-all`
策略，而邮件经过第三方转发服务（如大学校友邮箱、自托管邮件列表、邮件网关）到达最终接收方时，接收方 MTA 的 SPF 验证会检查转发服务器的 IP 而非原始发件人的授权 IP，导致 SPF 失败（
`fail`
）。SRS 通过在转发 MTA 端将 envelope-from 地址改写为转发域的一个编码地址——该编码地址内嵌原始发件人信息和加密哈希——使转发域成为 SPF 检查的新目标域，从而恢复 SPF 验证链的连续性。本文从 SPF 转发断链的 RFC 7208 §4.6.1 的规范描述出发，详解 SRS 的编码/解码算法、Postfix postsrsd 的配置操作，并剖析 SRS 与 DMARC 对齐的三种互动场景：SPF-only pass（信封转发保留）、DKIM passthrough（签名不变）和 SRS-driven alignment（信封改写驱动的新对齐）。

## 1. SPF 转发断链问题的根源（RFC 7208 §4.6.1）

### 1.1 转发场景下的 SPF 验证链断裂

考虑以下路径：
`user@gmail.com`
→
`user@example.com`
（设置了自动转发到
`user@company.org`
）。当 example.com 的 MTA 收到来自 gmail.com 的邮件后，将其转发到 company.org：

```
# 原始邮件路径（简化）
Return-Path: 
From: user@gmail.com
To: user@example.com

# example.com MTA 转发到 company.org 时的 SMTP 命令
MAIL FROM:         ← 信封发件人未改变
RCPT TO:
# 此时 example.com MTA 的 IP 是 198.51.100.1
```

company.org 的 MTA 执行 SPF 验证时，检查的是
`user@gmail.com`
（Return-Path 域）的 SPF 记录，但连接 IP 是
`198.51.100.1`
（example.com 的转发 MTA IP），而非 gmail.com 授权的发件 IP。gmail.com 的 SPF 记录中显然不会包含 example.com 的 IP，因此 SPF 结果为
`fail`
。RFC 7208 §4.6.1 将此定义为 SPF 的已知局限性：SPF 验证连接 IP 与 MAIL FROM 域授权 IP 的匹配关系，但在转发路径中，连接 IP 属于转发方而非原始发件方。

### 1.2 该问题的实际影响范围

考虑三类典型场景的面貌：(1) 大学提供
`@alumni.university.edu`
邮箱的终身转发服务——校友将邮件转发到
`@gmail.com`
，Gmail 的 SPF 检查因转发服务器的 IP 不在原始发件人所在域的 SPF 记录中而失败；(2) 企业邮件列表（如
`engineering@company.com`
）——列表服务器将订阅者发送的邮件重发给所有成员，SPF 在最终接收方检查列表服务器 IP 而非订阅者原始 IP；(3) 邮件安全网关——网关接收并扫描邮件后转发到内部邮件服务器，内部服务器的 SPF 检查会看到网关 IP 而非外部发件人 IP。场景 (3) 可以用
`permit_mynetworks`
绕过 SPF 检查，但场景 (1) 和 (2) 涉及不可控的外部接收方。

## 2. SRS 算法原理

### 2.1 信封改写 vs 信头改写

SRS 的关键设计选择：它只改写 SMTP 信封的
`MAIL FROM`
（即
`Return-Path`
）地址，不触及 RFC 5322 消息头的
`From:`
字段。这确保用户在邮件客户端中看到的 From 地址不变，但 SMTP 级别的 SPF 验证目标从原始发件域转移到转发域。SRS 编码后的地址形式：

```
SRS0=HHHH=TT=original-domain=original-local=original-domain
```

其中
`SRS0`
是版本前缀（第一版），
`HHHH`
是 HMAC-SHA1 哈希（取前 4 字符），
`TT`
是 Unix 时间戳的低 16 位编码（Base64 的 2 字符），
`original-domain`
是原始发件域，
`original-local`
是原始发件人的本地部分，后缀域是转发域。一个完整的 SRS 地址示例：

```
SRS0=AbCd=3D=example.com=john=forwarder.net
```

当邮件被退回（bounce）时，退回通知会发送到
`SRS0=AbCd=3D=example.com=john@forwarder.net`
，forwarder.net 的 MTA 解码该地址，提取原始
`john@example.com`
，将 bounce 投递回原始发件人。哈希字段用于验证地址确实由 forwarder.net 生成（防伪造——攻击者无法在没有密钥的情况下生成有效的 SRS 地址来利用转发域作为退信放大目标）。

### 2.2 SRS1 与多跳转发

当邮件经过两次转发时（如 gmail.com → example.com → forwarder.net → final.org），SRS 采用版本号递进来区分不同的转发跳：第一跳将原始地址编码为 SRS0，第二跳将 SRS0 编码为 SRS1。退信时，SRS1 目的地（forwarder.net）解码回 SRS0，再投递到 example.com，由 example.com 最终解码回原始地址。递进版本号确保每跳转发 MTA 只负责解码自己编码的层。

## 3. Postfix postsrsd 配置实战

### 3.1 安装与基础配置

postsrsd 是 Postfix SRS 的守护进程实现，作为 Postfix 的 before-queue milter 运行。它在邮件入队前改写 envelope-from。安装（Debian/Ubuntu）：

```
# apt install postsrsd
# 生成密钥文件（至少 16 字符随机字符串）
# echo "MySecretSRSKey2026!!" > /etc/postsrsd.secret
# chmod 600 /etc/postsrsd.secret
# chown postsrsd:postsrsd /etc/postsrsd.secret
```

Postfix 配置（
`/etc/postfix/main.cf`
）：

```
# 启用 postsrsd 作为 milter
sender_canonical_maps = tcp:127.0.0.1:10001
sender_canonical_classes = envelope_sender
recipient_canonical_maps = tcp:127.0.0.1:10002
recipient_canonical_classes = envelope_recipient
```

`sender_canonical_maps`
用于外发方向——当 Postfix 向外部域发送邮件时（即作为转发方），查询 postsrsd 是否应改写 envelope-from。postsrsd 在 /etc/default/postsrsd 中的核心参数：

```
SRS_DOMAIN=forwarder.net         # 转发域名，SRS 地址的 @ 后缀
SRS_SECRET=/etc/postsrsd.secret   # HMAC-SHA1 密钥文件路径
SRS_FORWARD_PORT=10001            # sender_canonical 监听端口
SRS_REVERSE_PORT=10002            # recipient_canonical 监听端口（退信解码）
```

### 3.2 SRS 排除规则：只改写需要转发的邮件

在典型的邮件服务器上，并非所有出站邮件都需要 SRS 改写——仅当邮件从外部发件人进入、经过本地域转发到外部收件人时才需要改写。本地用户直接提交的邮件（已通过 SMTP AUTH 认证）不应被 SRS 改写。postsrsd 通过
`SRS_EXCLUDE_DOMAINS`
配置参数实现排除：

```
# /etc/default/postsrsd
SRS_EXCLUDE_DOMAINS=.example.com,.example.net,localhost,.local
```

这个配置告知 postsrsd：当 envelope-from 的发件域是 example.com 或 example.net 的子域时，不进行 SRS 改写。更精确的排除可以在 Postfix 层面实现（通过不同的 smtpd 实例）：

```
# /etc/postfix/master.cf
# 端口 25 的入站 smtpd（不需要 SRS，因为入站邮件由本地投递）
smtp      inet  n       -       y       -       -       smtpd

# 端口 10026 的"内容过滤后重新注入"实例（需要 SRS）
127.0.0.1:10026 inet n  -       y       -       -       smtpd
  -o sender_canonical_maps=tcp:127.0.0.1:10001
  -o recipient_canonical_maps=tcp:127.0.0.1:10002
```

### 3.3 验证 SRS 工作状态

通过查看 Postfix 日志确认 SRS 改写是否生效：

```
$ grep "sender_canonical" /var/log/mail.log
postfix/cleanup[12345]: sender_canonical_maps: 
  user@gmail.com -> SRS0=XXXX=3D=gmail.com=user@forwarder.net
```

使用
`swaks`
发送测试邮件：

```
$ swaks --to test@company.org --from user@gmail.com \
       --server mail.forwarder.net --port 25
# 在 company.org 端检查 Return-Path 是否以 SRS0= 开头
```

## 4. SRS 与 DMARC 对齐的三种互动场景

### 4.1 场景 A：SPF-only pass（DKIM 签名被转发破坏）

如果原始发件域（gmail.com）只依赖 SPF 进行 DMARC 对齐（DKIM 未签名或签名在转发过程中因邮件体修改而失效），SRS 改写后 DMARC 评估将基于转发域（forwarder.net）进行。此时，(1) forwarder.net 必须发布自己的 DMARC 记录（至少
`p=none`
）；(2) SRS 改写后的 Return-Path 域名（forwarder.net）必须与 Header From（仍为 gmail.com）对齐——但由于
`aspf=r`
（relaxed 模式）只要求组织域匹配，gmail.com 和 forwarder.net 的组织域不同，SPF 对齐必然失败。

这意味着 SRS 本身解决了 SPF 的
`fail`
问题（变为
`pass`
for forwarder.net），但无法解决 DMARC 的 SPF 对齐问题——转发域无法与原始发件域对齐。在这一场景下，需要 DKIM 签名来提供 DMARC 对齐（见场景 B）。

### 4.2 场景 B：DKIM passthrough（最佳情况）

如果原始发件人对邮件进行了 DKIM 签名（
`d=gmail.com, s=20230601`
），且转发 MTA 在转发过程中未修改邮件头部和正文（即邮件列表软件在信头追加
`List-*`
头不算破坏），DKIM 签名在最终接收方仍可通过验证。DKIM 的
`d=`
域直接等于 Header From 域（
`gmail.com`
），DKIM 对齐通过，DMARC 通过。此场景下 SRS 的作用退化为单纯的退信路径保障——它确保 bounce 能正确路由回原始发件人，但不参与 DMARC 的身份验证决策。

### 4.3 场景 C：SRS-driven SPF 对齐（需要 DKIM 转发签名）

当转发 MTA 修改了邮件内容（如追加免责声明 footer、扫描附件后重新打包），原始 DKIM 签名必然失效。此时转发 MTA 需要对邮件进行重新 DKIM 签名，使用自己的域（forwarder.net）和选择器。如果转发 MTA 不修改 Header From（保持 gmail.com），新的 DKIM 签名域（forwarder.net）与 Header From 域（gmail.com）不匹配，DKIM 对齐失败。SPF 对齐也失败（因为 SRS 改写的 Return-Path 域是 forwarder.net）。DMARC 失败。

RFC 7489 对此场景没有原生解决方案。实践中，对于已知的转发关系，最终接收方可以通过白名单绕过 DMARC 检查。昆仑邮件系统在企业邮箱网关中采用了"转发信任链"模型：网关维护一个包含所有已知转发合作伙伴域名的信任列表，当检测到 DMARC 失败但邮件来自信任的转发伙伴域时，将邮件标记为"降低信任但在允许范围内"，同时向发件域管理员发送 DMARC failure 报告（ruf）供其审核。

## 5. SRS 的安全边界与替代方案

### 5.1 SRS 的退信放大风险

SRS 的一个固有风险是退信放大（backscatter）：攻击者可以向一个部署了 SRS 的转发服务器发送大量以不存在的收件人为目标的邮件，这些邮件的 envelope-from 被 SRS 编码为转发域的地址。当退信发生时，退信会发送回转发服务器（而非伪造的原始发件人），转发服务器需要解码 SRS 地址并将退信投递给原始发件人。如果原始发件地址也是伪造的，退信会继续在没有 SRS 保护的路径上传播。

缓解措施：(1) 转发 MTA 应在接受邮件时对发件域进行基本的 SPF/DKIM 验证后再进行 SRS 改写（即"经验证的转发"而非"盲目转发"）；(2) 限制每个 SRS 编码地址的有效期（postsrsd 默认使用 SHA1 哈希中的时间戳，有效期可通过
`SRS_HASH_LENGTH`
等参数配置）；(3) 对退信目标域实施速率限制。

### 5.2 替代方案：ARC（RFC 8617）

ARC（Authenticated Received Chain, RFC 8617, July 2019）是解决转发场景中邮件认证链断裂的更完整方案。与 SRS 只处理 envelope-from 不同，ARC 在邮件头中追加三类头部——
`ARC-Authentication-Results`
（转发前原始认证结果）、
`ARC-Message-Signature`
（邮件内容签名）和
`ARC-Seal`
（前面 ARC 头的链式签名）——使最终接收方可以核查整个转发链的认证状态。ARC 与 SRS 不冲突——SRS 处理信封层的 SPF 兼容，ARC 处理邮件头的认证链可审计性，两者在复杂转发场景中可以协同部署。

### 参考文献

1. RFC 7208 — Sender Policy Framework (SPF) for Authorizing Use of Domains in Email (IETF, April 2014). Section 4.6.1 Forwarding, Section 2.3 MAIL FROM Identity, Section 8 Security Considerations.
2. RFC 7489 — Domain-based Message Authentication, Reporting, and Conformance (DMARC) (IETF, March 2015). Section 3.1.1 SPF-Authenticated Identifiers, Section 6.3 aspf Tag (alignment mode).
3. RFC 6376 — DomainKeys Identified Mail (DKIM) Signatures (IETF, September 2011). Section 3.5 The d= Tag, Section 5 DKIM Verification.
4. RFC 8617 — Authenticated Received Chain (ARC) Protocol (IETF, July 2019). Section 4 ARC Set Components, Section 5 ARC Validation.
5. RFC 5321 — Simple Mail Transfer Protocol (IETF, October 2008). Section 4.1.1.2 MAIL Command (Return-Path semantics).
6. postsrsd — Postfix Sender Rewriting Scheme daemon.
   <https://github.com/roehling/postsrsd>
   . Configuration and operational guide.
7. Original SRS Specification —
   <https://www.openspf.org/SRS>
   . SRS0/SRS1 encoding format and HMAC hash algorithm.
8. NIST SP 800-177 Rev.1 — Trustworthy Email (NIST, February 2019). Section 4.5 Email Forwarding and Mailing Lists.
9. GB/T 37002-2018 — 信息安全技术 电子邮件系统安全技术要求. 第 6.2.5 节 邮件来源真实性（转发场景的安全性考量）.
10. Postfix Sender Canonical Maps —
    <https://www.postfix.org/postconf.5.html#sender_canonical_maps>

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/srs-sender-rewriting.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
