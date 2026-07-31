---
title: "TLS-RPT 报告是什么格式、通常包含哪些内容？"
source: "https://ztpop.net/kb/tlsrpt-faq-04.html"
license: CC-BY 4.0
---

# TLS-RPT 报告是什么格式、通常包含哪些内容？

1
TLS-RPT 报告是什么格式、通常包含哪些内容？
▼

**格式**

报告为 JSON 文档，属于“聚合报告”。核心结构含：`policy`（本次生效的是 MTA-STS 还是 DANE/TLS 策略及详情）、`summary`（成功与会话失败的总数）、`failure-details`（逐条失败明细数组）。

**用途**

通过 summary 可看失败占比，通过 failure-details 可定位是证书问题、MX 不匹配还是对端不支持 STARTTLS，从而精准修复。

参考：RFC 8460（report schema）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/tlsrpt-faq-04.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
