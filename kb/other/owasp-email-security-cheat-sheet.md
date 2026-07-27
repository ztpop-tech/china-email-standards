---
title: "OWASP 电子邮件安全速查表：开发与运营的落地清单"
source: "https://ztpop.net/kb/owasp-email-security-cheat-sheet.html"
license: CC-BY 4.0
---

# OWASP 电子邮件安全速查表：开发与运营的落地清单

## 概述

OWASP 的 Email Security Cheat Sheet 面向"写代码发邮件"与"运维邮件系统"的团队，给出可勾选的安全清单。它把 RFC 级的邮件安全原则翻译成工程动作，覆盖认证、传输、注入、退订、日志、密钥等维度，是邮件相关开发的安全基线。

## 认证与发信身份

* 对外发信必须配置并验证 SPF/DKIM/DMARC，DMARC 逐步到 `p=reject`。
* 应用发送用专用发信子域，不与主域混用；凭据存密钥库，禁止硬编码。
* SMTP 认证优先 STARTTLS/隐式 TLS + 应用专用密码或 OAuth2（RFC 7628）。

## 传输与注入防护

邮件头/正文拼接时必须防御**头部注入（header injection）**：用户输入中的 CRLF 会被恶意利用插入额外 `To:/Bcc:/Subject:`。应严格校验、转义，或用结构化库构造邮件。这与 Web 参数注入同源，是 OWASP Top 10 中注入类的邮件侧表现。

## 退订与合规

* 营销邮件必须含 RFC 8058 一键退订与可见退订链接。
* 尊重 List-Unsubscribe 与用户隐私设置（参考 Apple MPP）。
* 不购买名单、不向未 opt-in 用户发送。

## 日志与密钥管理

日志中禁止记录明文口令、完整邮件正文等敏感数据；DKIM 私钥按 RFC 6376/8301 用 ≥2048 位 RSA 并定期轮换；审计发信异常（突发量、陌生目的地）。与邮件账号防盗、密钥轮换管理直接呼应。

## 对信创邮件与开发的启示

政企在信创邮件系统上开发业务邮件（通知、账单、验证码）时，应以本速查表做安全评审清单；把头部注入防护、TLS 强制、DKIM 轮换、退订合规写入代码规范，避免"功能对了但安全漏了"。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/owasp-email-security-cheat-sheet.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
