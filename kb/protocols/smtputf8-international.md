---
title: "SMTPUTF8 国际化邮件是什么？为什么邮件地址和标题能包含中文/emoji？"
source: "https://ztpop.net/kb/smtputf8-international.html"
license: CC-BY 4.0
---

# SMTPUTF8 国际化邮件是什么？为什么邮件地址和标题能包含中文/emoji？

1
SMTPUTF8 国际化邮件是什么？为什么邮件地址和标题能包含中文/emoji？
▼

**背景**

传统 SMTP 仅支持 ASCII；国际化邮件系列 RFC 6531（SMTPUTF8 扩展）、6532（国际化信头）、6533（UTF-8 正文）允许信头与信封使用 UTF-8，使中文/日文/emoji 等非 ASCII 地址与主题可直接传输。

**SMTPUTF8**

RFC 6531 在 MAIL FROM/RCPT TO 增加 SMTPUTF8 关键字，以 UTF-8 编码信封地址；需双方 EHLO 都声明支持才能端到端传输国际化地址，否则需 Punycode/降级处理。

**信头与正文**

RFC 6532 允许 Subject、显示名等信头用 UTF-8（替代 MIME encoded-word）；RFC 6533 规定 UTF-8 正文。兼容旧系统时用 encoded-word 转义或回退到 ASCII 别名。

**实践**

主流邮箱已支持；发信系统若用户含非 ASCII 地址，应在 SMTP 协商时启用 SMTPUTF8，并保证 DNS/MX 与认证（SPF/DKIM/DMARC）对非 ASCII 域同样生效，避免投递失败。

参考：RFC 6531（SMTPUTF8）；RFC 6532（国际化信头）；RFC 6533（UTF-8 正文）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/smtputf8-international.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
