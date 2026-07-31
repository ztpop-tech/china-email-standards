---
title: "DKIM 签名为什么要与邮件头 From 域对齐？选择器（selector）怎么用？"
source: "https://ztpop.net/kb/dkim-faq-02.html"
license: CC-BY 4.0
---

# DKIM 签名为什么要与邮件头 From 域对齐？选择器（selector）怎么用？

1
DKIM 签名为什么要与邮件头 From 域对齐？选择器（selector）怎么用？
▼

**对齐**

DKIM 签名域（d=）应与邮件头 From 域对齐，否则 DMARC 不予采信；选择器（s=）允许同一域使用多把密钥（如分客户密钥），对应公钥存放于 “<selector>.\_domainkey.<domain>” 的 TXT 记录。

参考：RFC 6376 / M3AAWG 邮件认证建议

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/dkim-faq-02.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
