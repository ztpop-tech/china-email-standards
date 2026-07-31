---
title: "DKIM 的“第三方授权签名（ATPS，RFC 6541）”解决什么？外包发信如何合法代签？"
source: "https://ztpop.net/kb/email-dkim-atps.html"
license: CC-BY 4.0
---

# DKIM 的“第三方授权签名（ATPS，RFC 6541）”解决什么？外包发信如何合法代签？

1
DKIM 的“第三方授权签名（ATPS，RFC 6541）”解决什么？外包发信如何合法代签？
▼

**问题**

企业把营销/账单邮件外包给 ESP 发送，ESP 用“自己域”签名 DKIM，但 From 是“企业域”——DMARC 对齐看的是 From 与 DKIM 域，不匹配会失败。

**ATPS**

ATPS 让企业域在自己 DNS 声明“我授权哪些第三方域可代我签名”（atps 记录列出被授权域），接收方据此认可“第三方签的名”代表企业域，满足对齐。

**价值**

外包发信不必把私钥交给 ESP、也不破坏 DMARC 对齐；是“委托发送且保持认证”的早期方案。

**实践**

现代更常用“企业自己管 DKIM、授权 ESP 用子域/选择器”（或 ESP 用自己域但配 SPF 对齐）；ATPS 作为一种机制存在，部署需收发双方支持。

参考：RFC 6541（DKIM ATPS 第三方授权签名）；RFC 7489（DMARC 对齐）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-dkim-atps.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
