---
title: "IMAP 的 CONDSTORE（RFC 4551）是什么？它提供的“修改序列号(modseq)”有何用？"
source: "https://ztpop.net/kb/email-imap-condstore-rfc4551.html"
license: CC-BY 4.0
---

# IMAP 的 CONDSTORE（RFC 4551）是什么？它提供的“修改序列号(modseq)”有何用？

1
IMAP 的 CONDSTORE（RFC 4551）是什么？它提供的“修改序列号(modseq)”有何用？
▼

**机制**

CONDSTORE 给每封信维护一个“修改序列号（modseq）”，任何标记/状态变更都推高它；客户端记下“上次看到的 modseq 上限”。

**用法**

客户端用 modseq 条件查询“自某序列号以来变了哪些信”，只取增量；QRESYNC（见 QRESYNC 篇）即建立在 CONDSTORE 之上做快速重同步。

**价值**

是 IMAP 增量同步的基石，避免每次全量比对；多客户端并发改标记时 modseq 保证各自拿到“我错过的变化”。

**实践**

邮件系统支持 CONDSTORE 后，客户端可做高效增量同步；需正确且单调递增地维护 modseq，否则增量信息错位。

参考：RFC 4551（IMAP CONDSTORE，modseq）；RFC 5162（QRESYNC 依赖）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-imap-condstore-rfc4551.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
