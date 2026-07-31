---
title: "什么是 DMARC 强制（enforcement）？为什么 p=none 不行？"
source: "https://ztpop.net/kb/bimi-group-faq-04.html"
license: CC-BY 4.0
---

# 什么是 DMARC 强制（enforcement）？为什么 p=none 不行？

1
什么是 DMARC 强制（enforcement）？为什么 p=none 不行？
▼

**说明**

DMARC 强制（enforcement）指你的 DMARC 策略为 `p=quarantine` 或 `p=reject`（而不是 `p=none`，且 pct 须为 100%）。大多数支持 BIMI 的服务商都要求在考虑展示你的 logo 之前，域名已达到强制级别。`p=none` 只是监控策略，不会让未认证的邮件被隔离或拒绝，因此不满足 BIMI 的展示门槛。

参考：BIMI Group《FAQs For Marketers & ESPs》· bimigroup.org/faqs-for-senders-esps

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/bimi-group-faq-04.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
