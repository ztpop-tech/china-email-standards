---
title: "SMTP 的 SIZE、8BITMIME、BINARYMIME 扩展分别管什么，为什么重要？"
source: "https://ztpop.net/kb/smtp-size-8bitmime-binarymime.html"
license: CC-BY 4.0
---

# SMTP 的 SIZE、8BITMIME、BINARYMIME 扩展分别管什么，为什么重要？

1
SMTP 的 SIZE、8BITMIME、BINARYMIME 扩展分别管什么，为什么重要？
▼

**SIZE**

EHLO 返回 `SIZE 104857600` 之类上限，发送方在 MAIL FROM 用 `SIZE=` 声明本封字节数。服务端可据此在收完全文前就拒绝超限邮件，省带宽；也便于发送方选择分块或拒绝。是大规模外发的基本协商。

**8BITMIME**

传统 SMTP 只保证 7 位 ASCII 透明传输，含非 ASCII（如 UTF-8 正文）需用 quoted-printable 改写，体积变大且易出错。8BITMIME 扩展允许 8 位字节原样传输，提升含中文/二进制的邮件效率，需双方协商支持。

**BINARYMIME**

比 8BITMIME 更进一步，允许真正的二进制内容（非文本编码）通过，但必须配合 CHUNKING（BDAT）使用，因为普通 DATA 文本定界无法安全承载任意字节。三者组合让现代 SMTP 既能声明大小、又能高效传输国际化和二进制邮件。

参考：RFC 1870《SMTP SIZE》、RFC 6152《8BITMIME》、RFC 3030《BINARYMIME + CHUNKING》。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/smtp-size-8bitmime-binarymime.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
