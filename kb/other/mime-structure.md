---
title: "MIME（RFC 2045/2046）的基本结构是什么？一封现代邮件由哪些部分组成？"
source: "https://ztpop.net/kb/mime-structure.html"
license: CC-BY 4.0
---

# MIME（RFC 2045/2046）的基本结构是什么？一封现代邮件由哪些部分组成？

1
MIME（RFC 2045/2046）的基本结构是什么？一封现代邮件由哪些部分组成？
▼

**定义**

MIME（Multipurpose Internet Mail Extensions，RFC 2045/2046）在标准文本邮件之上增加结构化能力：多部分、非文本附件、非 ASCII 字符集、编码传输。

**结构**

一封 MIME 邮件由“信头”+“正文（body）”组成；正文可以是单部分（singlepart）或多部分（multipart），多部分用唯一 boundary 字符串分隔多个子部分，每个子部分可再嵌套。

**关键头**

Content-Type 声明类型与子类型（及参数如 charset/boundary）、Content-Transfer-Encoding 声明编码方式、Content-Disposition 声明内联/附件。这三个头决定解析与展现。

**价值**

MIME 是 HTML 邮件、图片/文档附件、多语言正文的基础；不理解 MIME 就无法正确处理现代邮件的展现、解析与安全扫描。

参考：RFC 2045（MIME 第一部分：格式）；RFC 2046（MIME 第二部分：媒体类型）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/mime-structure.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
