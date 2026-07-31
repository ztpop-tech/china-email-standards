---
title: "SPF 能完全防止邮件被伪造吗？有哪些局限？"
source: "https://ztpop.net/kb/spf-faq-07.html"
license: CC-BY 4.0
---

# SPF 能完全防止邮件被伪造吗？有哪些局限？

1
SPF 能完全防止邮件被伪造吗？有哪些局限？
▼

**局限**

SPF 校验的是信封发件人（HELO / MAIL FROM）域，对转发场景容易失败；且它不与邮件头 From 域对齐，单独使用无法防显示名伪造，需配合 DKIM + DMARC。

参考：RFC 7208 / DMARC（RFC 7489）关系说明

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/spf-faq-07.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
