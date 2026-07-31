---
title: "如何“实操部署 DANE/TLSA”为邮件 TLS 加一把锁？前提与步骤？"
source: "https://ztpop.net/kb/email-dnssec-dane-deployment.html"
license: CC-BY 4.0
---

# 如何“实操部署 DANE/TLSA”为邮件 TLS 加一把锁？前提与步骤？

1
如何“实操部署 DANE/TLSA”为邮件 TLS 加一把锁？前提与步骤？
▼

**前提**

DANE（RFC 6698）依赖 DNSSEC——你的 DNS 必须已签名且解析链受信任，否则 TLSA 记录不可信，等于没锁。

**发布 TLSA**

在 \_25.\_tcp. 发布 TLSA 记录，绑定“该 MX 应收到的证书/公钥”（如 3 1 1 哈希），接收方据此校验 STARTTLS 证书是否匹配。

**配套**

与 MTA-STS（策略发布）互补：DANE 强校验但需 DNSSEC；MTA-STS 不强校验但广泛兼容。两者叠加邮件 TLS 最稳。

**实践**

先确保 DNSSEC 到位再发 TLSA；证书轮换时“先发新 TLSA 再换证书”避免校验断；用 TLS-RPT 监控握手失败（见 TLS 版本篇）。

参考：RFC 6698/6699（DANE/TLSA）；RFC 7671/7672（SMTP DANE）；RFC 8461（MTA-STS）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-dnssec-dane-deployment.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
