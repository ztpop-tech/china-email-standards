---
title: "MIME multipart（RFC 2046）是什么？multipart/alternative、mixed、related 有何区别？"
source: "https://ztpop.net/kb/mime-multipart.html"
license: CC-BY 4.0
---

# MIME multipart（RFC 2046）是什么？multipart/alternative、mixed、related 有何区别？

1
MIME multipart（RFC 2046）是什么？multipart/alternative、mixed、related 有何区别？
▼

**定义**

multipart 是一种 Content-Type（RFC 2046），正文由多个部分用 boundary 分隔，每部分有独立 Content-Type；常用于一封邮件含多块内容。

**alternative**

同一内容的多种表示（如纯文本 + HTML），客户端选它能显示的最佳版本；收件方看到一份内容而非两份，用于兼容纯文本与富文本客户端。

**mixed**

不同内容的顺序组合（如正文 + 附件），客户端依次展现；最常用，普通“带附件的邮件”即 multipart/mixed。

**related**

各部分互相关联（如 HTML 正文中内嵌图片，图片作为 related 子部分被 cid: 引用）；用于图文混排邮件。multipart 可嵌套（mixed 内含 alternative 内含 related），boundary 必须唯一。

参考：RFC 2046（MIME 媒体类型：multipart）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/mime-multipart.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
