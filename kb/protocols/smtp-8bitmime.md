---
title: "8BITMIME 扩展（RFC 6152）是什么？它与 SMTPUTF8 有何区别？"
source: "https://ztpop.net/kb/smtp-8bitmime.html"
license: CC-BY 4.0
---

# 8BITMIME 扩展（RFC 6152）是什么？它与 SMTPUTF8 有何区别？

1
8BITMIME 扩展（RFC 6152）是什么？它与 SMTPUTF8 有何区别？
▼

**定义**

8BITMIME（RFC 6152）允许 SMTP 传输“8 位干净”的内容——即数据含 8 位字节但仍是文本（如带重音的 Latin-1），不再强制 7-bit。它在 EHLO 声明 8BITMIME。

**与 SMTPUTF8 区别**

8BITMIME 仅放宽“内容以 8 位文本传输”的限制，信封地址仍是 ASCII；SMTPUTF8（RFC 6531）进一步允许 UTF-8 信封地址与信头，支持非 ASCII 邮箱。二者层次不同：前者管内容编码，后者管地址国际化。

**价值**

含 8 位字符的文本邮件无需 Base64/QP 转义即可传输，降低编码开销；但纯二进制仍不可用（需 BINARYMIME/BDAT）。

**注意**

若对端不支持 8BITMIME，客户端应回退到 quoted-printable/base64 编码（7-bit 安全）再发，避免传输损坏与乱码。

参考：RFC 6152（8BITMIME）；与 SMTPUTF8（RFC 6531）区分

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/smtp-8bitmime.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
