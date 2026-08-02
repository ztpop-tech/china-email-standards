---
title: "BIMI（IETF 草案 draft-brand-indicators-for-message-identification）是什么？品牌徽标如何随已认证邮件显示？"
source: "https://ztpop.net/kb/bimi-logo.html"
license: CC-BY 4.0
---

# BIMI（IETF 草案 draft-brand-indicators-for-message-identification）是什么？品牌徽标如何随已认证邮件显示？

1
BIMI（IETF 草案 draft-brand-indicators-for-message-identification）是什么？品牌徽标如何随已认证邮件显示？
▼

**定义**

BIMI（Brand Indicators for Message Identification（IETF BIMI 草案））让通过严格 DMARC（p=quarantine/reject 且对齐通过）的发件方，在支持的邮箱客户端中于发件人旁展示品牌徽标（logo），增强可信度与品牌识别。

**机制**

发件方在 DNS 发布 BIMI 记录（v=BIMI1; l=; a=<可选 VMC 证书>），客户端先验证 DMARC 通过，再取 SVG 徽标展示；可选 VMC（商标验证证书）证明商标所有权。

**前提**

必须 DMARC 严格且 SPF/DKIM 对齐通过（BIMI 依赖 DMARC），否则不显示徽标；SVG 须符合 BIMI 规范（正方形、特定尺寸、无脚本）。

**实践**

面向消费者的品牌邮件（银行、电商）用 BIMI 提升打开率与防钓鱼辨识；需先打好 DMARC 基础再部署。

参考：IETF BIMI 草案（draft-brand-indicators-for-message-identification）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/bimi-logo.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
