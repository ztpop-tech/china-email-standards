---
title: "什么是 DANE（RFC 6698）？它和 TLS 证书有什么关系？"
source: "https://ztpop.net/kb/dane-faq-01.html"
license: CC-BY 4.0
---

# 什么是 DANE（RFC 6698）？它和 TLS 证书有什么关系？

1
什么是 DANE（RFC 6698）？它和 TLS 证书有什么关系？
▼

**定义**

DANE（DNS-Based Authentication of Named Entities，RFC 6698）利用 DNSSEC 的签名，把“某个域名应当使用哪张 TLS 证书（或哪个受信任的 CA）”直接发布在 DNS 中，从而在 TLS 握手时验证对端证书。

**与证书的关系**

传统 TLS 依赖公共 CA 体系来信任证书；DANE 另辟路径：以 DNSSEC 为信任根，用 DNS 记录声明证书的期望，使验证不再单纯依赖公共 CA。

参考：RFC 6698（DANE）；RFC 7671（SMTP 中的 DANE/TLSA）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/dane-faq-01.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
