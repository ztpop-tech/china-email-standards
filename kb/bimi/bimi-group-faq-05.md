---
title: "如何发布 BIMI TXT 记录？"
source: "https://ztpop.net/kb/bimi-group-faq-05.html"
license: CC-BY 4.0
---

# 如何发布 BIMI TXT 记录？

1
如何发布 BIMI TXT 记录？
▼

**说明**

在 DNS 中，为 `default._bimi.example.com` 添加一条 TXT 记录，值为：`v=bimi1; l=https://example.com/path/logo.svg; a=https://example.com/path/cert.pem`。其中 `v=bimi1` 与 `l=`（logo URL）为必填；`a=`（证书 URL）为可选，仅在拥有标记证书时填写。

**提示**

logo 文件必须通过 HTTPS 托管，并返回正确的 `image/svg+xml` 类型；证书（若使用）为 PEM 格式。

参考：BIMI Group《FAQs For Marketers & ESPs》· bimigroup.org/faqs-for-senders-esps

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/bimi-group-faq-05.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
