---
title: "SMTP 的 CHUNKING（RFC 3030，BDAT）如何“分块传输”大邮件？与 PIPELINING 有何关系？"
source: "https://ztpop.net/kb/smtp-chunking-extension.html"
license: CC-BY 4.0
---

# SMTP 的 CHUNKING（RFC 3030，BDAT）如何“分块传输”大邮件？与 PIPELINING 有何关系？

1
SMTP 的 CHUNKING（RFC 3030，BDAT）如何“分块传输”大邮件？与 PIPELINING 有何关系？
▼

**背景**

传统 DATA 要“先收完整信体再处理”，大附件占用内存/需先落地；CHUNKING 允许把信体“分块（chunk）”用 BDAT 命令逐块发，服务器流式处理。

**机制**

EHLO 显示 CHUNKING；发信方用 BDAT  [LAST] 分块推信体，末块标 LAST；不必等全信到齐即可边收边扫/边转发。

**与 BINARYMIME**

CHUNKING 常与 BINARYMIME 同用（同为 RFC 3030），支持 8 位/二进制内容不经改造；是“大邮件高效投递”的扩展组合。

**关系**

PIPELINING 是“命令批发的 RTT 优化”，CHUNKING 是“信体分块的内存/流式优化”，二者正交、可叠加。

参考：RFC 3030（SMTP CHUNKING + BINARYMIME）；RFC 2920（PIPELINING 对比）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/smtp-chunking-extension.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
