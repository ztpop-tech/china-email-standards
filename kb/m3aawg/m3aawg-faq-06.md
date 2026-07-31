---
title: "什么是 ARC（Authenticated Received Chain）？中转方为何要部署它？"
source: "https://ztpop.net/kb/m3aawg-faq-06.html"
license: CC-BY 4.0
---

# 什么是 ARC（Authenticated Received Chain）？中转方为何要部署它？

1
什么是 ARC（Authenticated Received Chain）？中转方为何要部署它？
▼

**ARC 是什么**

ARC 为邮件提供一条“经过认证的监管链”，记录邮件每一跳的处理实体以及各跳的认证评估结果（RFC 8617）。它无需改动邮件内容，即可抵御因邮件经过中转方而在后续跳点产生的认证失败。

**中转方为何要部署**

转发服务、邮件列表等中转方（Mediators/Relays/Gateways）可能改动邮件，导致最终接收方的 SPF/DKIM/DMARC 校验失败。M3AAWG 呼吁中转方：尽量减少在途改动、对难免的改动采取措施降低失败风险（如邮件列表改写 From 头），并**部署 ARC**、生成 DMARC 报告，且在 ARC-Authentication-Results 头中记录 SPF/DKIM/DMARC 校验结果。

参考：M3AAWG《Email Authentication Recommended Best Practices》(2020-09)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/m3aawg-faq-06.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
