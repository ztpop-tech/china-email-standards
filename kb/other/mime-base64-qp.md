---
title: "Base64 与 Quoted-Printable（QP）编码（RFC 2045/2047）有什么区别？何时用哪个？"
source: "https://ztpop.net/kb/mime-base64-qp.html"
license: CC-BY 4.0
---

# Base64 与 Quoted-Printable（QP）编码（RFC 2045/2047）有什么区别？何时用哪个？

1
Base64 与 Quoted-Printable（QP）编码（RFC 2045/2047）有什么区别？何时用哪个？
▼

**Base64**

Base64（RFC 2045）把任意二进制数据按 3 字节→4 字符编码为 7-bit ASCII 安全字符集，膨胀约 33%。适合二进制附件（图片、文档）或整体非文本数据的传输。

**QP**

Quoted-Printable（RFC 2045）把可打印 ASCII 原样保留，仅对不可打印字节与“=”用 =XX 转义；几乎不膨胀文本，适合“大部分是英文、少量特殊字符”的内容。

**信头非 ASCII**

信头中的非 ASCII（如中文主题、显示名）用 RFC 2047 的 encoded-word（=?charset?B/QP?...?=）编码，正文区则用 body 的 Content-Transfer-Encoding。二者解决层面不同。

**选择**

二进制/大量非文本→Base64；文本为主、偶有特殊字符→QP；信头非 ASCII→RFC 2047。二者都解决“7-bit 安全传输”，但目标数据不同。

参考：RFC 2045（Base64/QP）；RFC 2047（信头非 ASCII 编码）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/mime-base64-qp.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
