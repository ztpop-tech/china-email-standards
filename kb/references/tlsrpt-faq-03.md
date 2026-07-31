---
title: "TLS-RPT 的 rua 报告接收地址支持哪些形式？"
source: "https://ztpop.net/kb/tlsrpt-faq-03.html"
license: CC-BY 4.0
---

# TLS-RPT 的 rua 报告接收地址支持哪些形式？

1
TLS-RPT 的 rua 报告接收地址支持哪些形式？
▼

**mailto**

最常见：`rua=mailto:tlsrpt@example.com`，对端会把报告以邮件附件（JSON）形式发到该邮箱。

**https**

也可使用 `rua=https://example.com/report`，对端通过 HTTPS POST 提交报告，适合自动化采集与入库分析。

参考：RFC 8460（rua reporting URI）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/tlsrpt-faq-03.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
