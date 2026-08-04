---
title: "RFC 6409 邮件提交协议（MSA）：为什么发信要走 587 而非 25"
source: "https://ztpop.net/kb/rfc6409-message-submission.html"
license: CC-BY 4.0
---

# RFC 6409 邮件提交协议（MSA）：为什么发信要走 587 而非 25

## 概述

RFC 6409 定义了"邮件提交"（Message Submission）协议，用于终端用户（MUA）把邮件交给自己的邮件服务商。它与 RFC 5321 的"传输"角色刻意分开：提交走 587 端口且必须认证，传输走 25 端口且面向服务器间路由。这种分离是当代邮件安全最重要的架构决策之一。

## 为什么要把"提交"与"传输"分开

如果所有人都能直接向任意 MTA 的 25 端口投信，运营商就无法施加身份、策略与配额控制，开放中继灾难会重演。把"用户发信"收敛到 MSA（587），带来三个确定性收益：

* **强制身份**：只有认证用户才能提交，便于追溯与限速；
* **策略前置**：服务商在 MSA 即可做内容扫描、DKIM 签名、垃圾邮件评分；
* **路由简化**：MTA 之间的 25 端口只需处理已提交、已签名的邮件，不必再操心"这是谁发的"。

## 提交流程

1. MUA 连接 MSA 的 587 端口；
2. `EHLO` 后协商 `STARTTLS`，将连接升级为加密；
3. 协商 `AUTH`，用户凭口令/OAuth/证书完成认证；
4. 认证通过后，用 `MAIL FROM`/`RCPT TO`/`DATA` 提交邮件；
5. MSA 在转发前为邮件打上 DKIM 签名，再以 SMTP 传给下一跳 MTA。

## AUTH 机制

RFC 6409 引用 RFC 4954（SMTP AUTH）。常见机制：`PLAIN`/`LOGIN` 明文口令（必须包裹在 TLS 内）、`CRAM-MD5`（质询-响应，不直传口令）、以及现代的 `XOAUTH2`（OAuth 令牌）。关键是：**任何凭据类 AUTH 都必须在 STARTTLS 之后进行**，否则口令会被全程明文嗅探。

## 与 RFC 5321 的边界

587 端口与 25 端口跑的是同一套 SMTP 命令，区别在"用途与策略"：587 面向已认证用户、强制 TLS、允许重写信头（如补全 From、追加 Message-ID）；25 面向中继、通常不允许改写发件域。现代邮件服务商（含昆仑邮件系统）默认关闭 25 端口的用户提交，只开放 587 的认证提交。

## 安全收益落到实战

对政企信创邮件，MSA 是"第一道身份闸门"：开启强制 MFA（见 CISA MFA 指引）、对异常提交速率告警、对被盗账号（SMTP 劫持）实时锁定，都能在 MSA 段完成。把发信认证收敛到 587，是降低账号被盗外发垃圾邮件、避免 IP 被列入 DNSBL 的最有效手段。

### 相关主题

* [RFC 5321 SMTP 协议](/kb/rfc5321-smtp-protocol.html)：邮件在服务器间的传输模型
* [RFC 8314 隐式 TLS](/kb/rfc8314-implicit-tls-submission.html)：用 465 取代明文 110/143 端口
* [RFC 7293 RRVS](/kb/rfc7293-rrvs-require-recipient-valid-since.html)：拦截僵尸账号投递
* [RFC 5598 互联网邮件架构](/kb/rfc5598-internet-email-architecture.html)：四段式组件视图
* [CISA MFA 实施指引](/kb/cisa-mfa-implementation-guide.html)：抗钓鱼 MFA 与高风险账号保护

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/rfc6409-message-submission.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
