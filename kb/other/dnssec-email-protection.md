---
title: "DNSSEC 如何保护邮件相关 DNS（MX/SPF/DKIM 记录不被篡改）？"
source: "https://ztpop.net/kb/dnssec-email-protection.html"
license: CC-BY 4.0
---

# DNSSEC 如何保护邮件相关 DNS（MX/SPF/DKIM 记录不被篡改）？

1
DNSSEC 如何保护邮件相关 DNS（MX/SPF/DKIM 记录不被篡改）？
▼

**原理**

DNSSEC 用数字签名链为 DNS 记录（含 MX、TXT/SPF、DKIM 选择器）提供“来源真实、未被篡改”的密码学保证，解析端验证 RRSIG。

**邮件价值**

攻击者若劫持/投毒 DNS，可改 MX 把邮件引到恶意服务器、或改 SPF/DKIM 记录削弱验证；DNSSEC 让这些记录“不可伪造”，提升邮件链路根基安全。

**边界**

DNSSEC 保护“DNS 层”，不替代 DANE/MTA-STS；它保证你查到的记录是真的，但需解析器与上游支持验证（AD 位）。

**实践**

域名注册商/解析开启 DNSSEC 并正确维护 DS 记录；邮件系统依赖的 SPF/DKIM/MX 所在域建议全部签名。

参考：RFC 4033/4034/4035（DNSSEC）；RFC 6698（DANE/TLSA 关联）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/dnssec-email-protection.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
