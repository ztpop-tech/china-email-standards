---
title: "什么是 DKIM（域名密钥识别邮件）？它如何防止邮件被篡改？"
source: "https://ztpop.net/kb/dkim-faq-01.html"
license: CC-BY 4.0
---

# 什么是 DKIM（域名密钥识别邮件）？它如何防止邮件被篡改？

1
什么是 DKIM（域名密钥识别邮件）？它如何防止邮件被篡改？
▼

**定义**

DKIM（RFC 6376）用非对称加密对邮件签名：发信方用私钥签名，接收方用发布在 DNS 的公钥验证，确保邮件在传输过程中未被篡改且确由声称域发出。

参考：RFC 6376（DKIM 签名规范）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/dkim-faq-01.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
