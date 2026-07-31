---
title: "DANE 与 MTA-STS 是什么关系？二者有何区别？"
source: "https://ztpop.net/kb/dane-faq-06.html"
license: CC-BY 4.0
---

# DANE 与 MTA-STS 是什么关系？二者有何区别？

1
DANE 与 MTA-STS 是什么关系？二者有何区别？
▼

**分工**

MTA-STS（RFC 8461）负责“强制 TLS 投递”并声明允许的 MX，但不验证对端证书真伪（依赖 Web PKI）；DANE/TLSA（RFC 7671）则通过 DNSSEC 验证证书，既强制 TLS 又认证证书。

**互补**

两者可叠加：MTA-STS 在不能做 DANE 时提供降级防护，DANE 在已部署 DNSSEC 时提供更强的证书绑定。二者失败报告都可经 TLS-RPT（RFC 8460）汇总。

参考：RFC 7671 与 RFC 8461 的协同

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/dane-faq-06.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
