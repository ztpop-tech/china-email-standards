---
title: "SMTP STARTTLS 是什么？为什么明文 25 端口必须升级为加密连接？"
source: "https://ztpop.net/kb/smtp-starttls.html"
license: CC-BY 4.0
---

# SMTP STARTTLS 是什么？为什么明文 25 端口必须升级为加密连接？

1
SMTP STARTTLS 是什么？为什么明文 25 端口必须升级为加密连接？
▼

**定义**

STARTTLS（RFC 3207）是一条 SMTP 服务扩展：客户端在明文会话中先发 EHLO，若服务器在响应里列出 STARTTLS，客户端即可发 STARTTLS 命令，把现有明文连接“升级”为 TLS 加密连接，之后才进行 MAIL/RCPT/DATA。它让同一端口既能明文又能加密，是邮件传输加密的事实标准。

**为何重要**

传统 SMTP 25 端口全程明文，邮件在多个中继跳之间可被窃听或篡改；STARTTLS 在不更换端口的前提下为传输加密封装，保护邮件内容、信头与认证凭据不被中间人读取。现代 MTA 之间普遍要求 STARTTLS。

**Opportunistic 与 Enforced**

机会型（opportunistic）STARTTLS：服务器支持就加密、不支持就退回明文（不保证安全，可能遭 STRIPTLS 降级攻击）；强制型（enforced）则在协商失败时拒绝投递。RFC 3207 本身定义机制，策略强度由运维决定。

**风险与加固**

纯机会型易被主动攻击者为中间人剥离（STRIPTLS），导致降级到明文；应结合 MTA-STS（策略强制）、DANE（基于 DNSSEC 的 TLSA 校验）、REQUIRETLS（端到端强加密）与 TLS-RPT（监控）形成完整防护链。

参考：RFC 3207（SMTP Service Extension for Secure SMTP over TLS）；MTA-STS（RFC 8461）、DANE（RFC 7672）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/smtp-starttls.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
