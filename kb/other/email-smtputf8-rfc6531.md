---
title: "国际化邮件（SMTPUTF8，RFC 6531/6532）是什么？为什么“中文/多语言地址与头”需要它？"
source: "https://ztpop.net/kb/email-smtputf8-rfc6531.html"
license: CC-BY 4.0
---

# 国际化邮件（SMTPUTF8，RFC 6531/6532）是什么？为什么“中文/多语言地址与头”需要它？

1
国际化邮件（SMTPUTF8，RFC 6531/6532）是什么？为什么“中文/多语言地址与头”需要它？
▼

**问题**

传统邮件地址与信头只能 ASCII；含非 ASCII（如 中文用户名、国际化域名、UTF-8 主题）需先编码（Punycode/RFC 2047），易出错且不直观。

**机制**

SMTPUTF8 扩展（EHLO 声明）允许信封地址与信头“原生 UTF-8”（如 用户@例子.中国）；RFC 6532 让信头字段直接 UTF-8。

**依赖**

需发送链全程支持（MTA、邮箱、客户端）；任一环不支持会回退编码或拒收；与 8BITMIME/BINARYMIME 配合。

**实践**

面向中文/多语言用户的系统应支持 SMTPUTF8/EAI，提升地址与主题可读性；但需注意对端兼容性，对不支持方仍走编码兜底。

参考：RFC 6531（SMTPUTF8）；RFC 6532（UTF-8 信头）；RFC 3490/5890（IDNA 域名）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-smtputf8-rfc6531.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
