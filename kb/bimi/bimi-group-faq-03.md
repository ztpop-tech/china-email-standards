---
title: "启用 BIMI 需要满足哪些前置条件？"
source: "https://ztpop.net/kb/bimi-group-faq-03.html"
license: CC-BY 4.0
---

# 启用 BIMI 需要满足哪些前置条件？

1
启用 BIMI 需要满足哪些前置条件？
▼

**说明**

要让 BIMI 真正落地，你需要在自己这一侧完成以下事项：把 DMARC 在组织域（Apex 域）及所用子域上推进到强制（enforcement）；确保 DKIM 对齐（优先）和/或 SPF 与可见 From 域名对齐；准备一张合规的 SVG Tiny-PS logo；把 SVG 托管在一个稳定的 HTTPS URL 上，并设置正确的 `image/svg+xml` MIME 类型；发布 BIMI TXT 记录（`v=bimi1; l= logo URL`，若有证书再加 `a=`）。

**建议**

BIMI 建立在 SPF/DKIM/DMARC 三件套之上，先把这些认证做扎实，logo 才有机会被展示。

参考：BIMI Group《FAQs For Marketers & ESPs》· bimigroup.org/faqs-for-senders-esps

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/bimi-group-faq-03.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
