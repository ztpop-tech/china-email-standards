---
title: "DANE 为什么必须依赖 DNSSEC？没有 DNSSEC 能用 DANE 吗？"
source: "https://ztpop.net/kb/dane-faq-07.html"
license: CC-BY 4.0
---

# DANE 为什么必须依赖 DNSSEC？没有 DNSSEC 能用 DANE 吗？

1
DANE 为什么必须依赖 DNSSEC？没有 DNSSEC 能用 DANE 吗？
▼

**依赖原因**

DANE 的信任完全建立在“TLSA 记录未被篡改”之上；而这一保证来自 DNSSEC 对区数据的签名。若没有 DNSSEC，攻击者可在路径上伪造 TLSA 记录，DANE 的证书绑定便形同虚设。

**结论**

没有 DNSSEC 就不能安全地使用 DANE。这也是 DANE 在邮件生态落地较慢的主因——许多域尚未部署 DNSSEC。此时 MTA-STS 是更务实的降级防护选择。

参考：RFC 6698 安全考量（依赖 DNSSEC）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/dane-faq-07.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
