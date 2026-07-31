---
title: "邮件（SMTP）场景下的 TLSA 记录是什么？应放在哪个名字下？"
source: "https://ztpop.net/kb/dane-faq-03.html"
license: CC-BY 4.0
---

# 邮件（SMTP）场景下的 TLSA 记录是什么？应放在哪个名字下？

1
邮件（SMTP）场景下的 TLSA 记录是什么？应放在哪个名字下？
▼

**位置**

SMTP 的 TLSA 记录名为 `_25._tcp.mail.你的域`（25 是 SMTP 端口，tcp 表示传输层），记录类型为 TLSA。

**字段**

TLSA 记录含四个字段：证书用法（certificate usage）、选择器（selector）、匹配类型（matching type）与证书关联数据（certificate association data，通常是证书或公钥的哈希/完整值）。

参考：RFC 7671（SMTP 的 DANE TLSA 记录）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/dane-faq-03.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
