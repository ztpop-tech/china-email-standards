---
title: "TLS-RPT 与 MTA-STS 是什么关系？"
source: "https://ztpop.net/kb/tlsrpt-faq-06.html"
license: CC-BY 4.0
---

# TLS-RPT 与 MTA-STS 是什么关系？

1
TLS-RPT 与 MTA-STS 是什么关系？
▼

**互补**

MTA-STS 负责“强制 TLS 投递”，TLS-RPT 负责“报告 TLS 失败”。两者通过各自 DNS 记录（`_mta-sts` 与 `_smtp._tls`）配合。

**为何要一起**

仅启用 MTA-STS（尤其 enforce）时，策略配错或对端证书异常会导致邮件被静默阻断，却无从排查。开启 TLS-RPT 后，对端会把失败明细回传，你才能发现并纠正问题，再放心切到 enforce。

参考：RFC 8460 与 RFC 8461 的协同

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/tlsrpt-faq-06.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
