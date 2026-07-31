---
title: "Content-Type 与 Content-Transfer-Encoding（RFC 2045）如何决定邮件如何被解析与展现？"
source: "https://ztpop.net/kb/mime-content-type.html"
license: CC-BY 4.0
---

# Content-Type 与 Content-Transfer-Encoding（RFC 2045）如何决定邮件如何被解析与展现？

1
Content-Type 与 Content-Transfer-Encoding（RFC 2045）如何决定邮件如何被解析与展现？
▼

**Content-Type**

Content-Type（RFC 2045）声明主体的媒体类型 type/subtype（如 text/plain、text/html、image/png、application/pdf）与参数（charset 字符集、boundary 多部分边界、name 文件名）。它告诉客户端“这是什么、怎么渲染”。

**CTE**

Content-Transfer-Encoding 声明主体在传输层如何编码为 7-bit 安全（7bit、8bit、binary、base64、quoted-printable）。它与“内容是什么”无关，只关乎“如何安全传输”。

**Disposition**

Content-Disposition 为 inline（内联显示）或 attachment（附件，可带 filename），影响客户端是展示还是提供下载；与 Content-Type 配合决定用户体验。

**实践**

正确设置 charset（如 UTF-8）避免乱码；附件用 base64 + attachment；错误组合（如 text/html 却用 7bit 含 8 位字节）会导致解析异常，是乱码与泄密的来源之一。

参考：RFC 2045（MIME 头字段：Content-Type / CTE / Disposition）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/mime-content-type.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
