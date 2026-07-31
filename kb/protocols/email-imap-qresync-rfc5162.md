---
title: "IMAP 的 QRESYNC（RFC 5162）如何做“快速重同步”？为什么手机端特别需要它？"
source: "https://ztpop.net/kb/email-imap-qresync-rfc5162.html"
license: CC-BY 4.0
---

# IMAP 的 QRESYNC（RFC 5162）如何做“快速重同步”？为什么手机端特别需要它？

1
IMAP 的 QRESYNC（RFC 5162）如何做“快速重同步”？为什么手机端特别需要它？
▼

**问题**

客户端离线后重连，传统要“拉全部 UID + 逐封比状态”才能知道“哪些新到/删了/标记变”，量大数据费。

**机制**

QRESYNC（基于 CONDSTORE 的 RFC 4551）让客户端带上“上次已知 UIDVALIDITY + 最高 UID + 修改序列号”，服务器只回“变化部分”（新增 UID、删除、状态变更），而非全量。

**价值**

极大减少重同步流量与时延，对“慢网/大邮箱/手机”体验关键；需先 ENABLE QRESYNC。

**实践**

移动客户端应启用 QRESYNC/CONDSTORE 做增量同步；邮件系统须支持并正确维护 UIDVALIDITY 与 modseq，否则增量信息错乱。

参考：RFC 5162（IMAP QRESYNC）；RFC 4551（CONDSTORE，modseq 基础）；RFC 5161（ENABLE）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-imap-qresync-rfc5162.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
