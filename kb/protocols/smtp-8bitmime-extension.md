---
title: "SMTP 的 8BITMIME 扩展（RFC 6152）解决了什么？为什么“8 位内容”需要它？"
source: "https://ztpop.net/kb/smtp-8bitmime-extension.html"
license: CC-BY 4.0
---

# SMTP 的 8BITMIME 扩展（RFC 6152）解决了什么？为什么“8 位内容”需要它？

1
SMTP 的 8BITMIME 扩展（RFC 6152）解决了什么？为什么“8 位内容”需要它？
▼

**背景**

原始 SMTP（RFC 821）规定信体按 7 位 ASCII 传输，含 8 位字节（如 UTF-8 正文、二进制）需先 Base64/QP 编码；RFC 6152 的 8BITMIME 允许“原样传输 8 位内容”。

**机制**

EHLO 显示 8BITMIME 能力，MAIL FROM 可带 BODY=8BITMIME 声明信体为 8 位；减少不必要的编码，降低体积、保留文本可读性。

**边界**

8BITMIME 仅声明“可传 8 位”，不保证中间不破坏；与 SMTPUTF8、BINARYMIME 不同——它仍是基于行的文本，不能传任意二进制。

**实践**

现代 MTA 普遍支持 8BITMIME，邮件系统可据此少做一层编码；但跨老旧中继仍需编码兜底以防损坏。

参考：RFC 6152（8BITMIME 扩展）；RFC 5321（SMTP 基础）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/smtp-8bitmime-extension.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
