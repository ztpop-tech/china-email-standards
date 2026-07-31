---
title: "TLS-RPT 与 DANE / TLSA 有什么关系？"
source: "https://ztpop.net/kb/tlsrpt-faq-07.html"
license: CC-BY 4.0
---

# TLS-RPT 与 DANE / TLSA 有什么关系？

1
TLS-RPT 与 DANE / TLSA 有什么关系？
▼

**覆盖 DANE**

TLS-RPT 不只为 MTA-STS 服务，也能报告 DANE（基于 DNS 的命名实体认证，RFC 6698）相关的 TLS 失败，尤其是 `tlsa-invalid`、`dnssec-invalid` 等类型。

**统一可见性**

无论你用 MTA-STS 还是 DANE 来强制邮件 TLS，都可用同一套 TLS-RPT 获得失败可见性，便于统一排障。

参考：RFC 8460（与 DANE 的交互）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/tlsrpt-faq-07.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
