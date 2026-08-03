---
title: "DANE for SMTP 如何部署？"
source: "https://ztpop.net/kb/dane-smtp-deployment.html"
license: CC-BY 4.0
---

# DANE for SMTP 如何部署？

1
DANE for SMTP 如何部署？
▼

**前提：DNSSEC**

DANE 的安全性建立在 DNSSEC 之上。必须先对邮件域的区（zone）做 DNSSEC 签名，使 TLSA 记录可被验证、不可被篡改。没有 DNSSEC，DANE 毫无意义且易被投毒。这是与 MTA-STS 最大的区别：MTA-STS 依赖 HTTPS/CA，DANE 依赖 DNSSEC。

**发布 TLSA 记录**

为接收 MX 发布 `_25._tcp.mail.<domain>` 的 TLSA 记录，格式为 `<cert-usage> <selector> <matching-type> <cert-association-data>`。常用 `3 1 1 <SHA-256 of SubjectPublicKeyInfo>`（DANE-EE，直接绑定终端实体证书）或 `2 1 1`（绑定受信任 CA 签发）。发送方在 STARTTLS 握手后，用 TLSA 记录校验对端证书，即使证书由私有 CA 签发也能确认身份。

**部署与注意**

发送方 MTA（如 Postfix 设 `smtp_tls_security_level = dane`）会：若解析到有效 TLSA 则强制匹配；若无 TLSA 则退化为「可用 TLS 即可」（opportunistic）。因此 DANE 既防降级又兼容未部署域。注意证书轮换时需先发布新 TLSA 再换证，并保留旧记录重叠期，避免邮件中断；同时要监控 DNSSEC 链有效性。

参考：RFC 7672《SMTP Security via DANE》、RFC 6698《TLSA/DANE》、RFC 4033《DNSSEC 概述》。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/dane-smtp-deployment.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
