---
title: "SMTP CHECKPOINT 扩展（RFC 3885）是什么？它如何支持断点续传式投递？"
source: "https://ztpop.net/kb/smtp-checkpoint.html"
license: CC-BY 4.0
---

# SMTP CHECKPOINT 扩展（RFC 3885）是什么？它如何支持断点续传式投递？

1
SMTP CHECKPOINT 扩展（RFC 3885）是什么？它如何支持断点续传式投递？
▼

**定义**

CHECKPOINT（RFC 3885）是 SMTP 扩展，允许在 DATA 传输过程中插入检查点（CHK 命令），接收方确认已收到的部分，发送方可在连接中断后从最后检查点续传，而非从头重发整封大邮件。

**机制**

发送方在流式发送正文时周期发 CHK，接收方回 250 确认已落盘字节偏移；断线重连后从偏移续传（需双方支持且能持久化部分接收状态）。

**价值**

对超大邮件（如大附件）在不稳定链路上避免“传一半断开、重头再来”的浪费；降低大邮件投递失败率与带宽损耗。

**注意**

CHECKPOINT 需双方 MTA 都支持并持久化部分状态；并非所有服务器实现，属可选优化扩展。

参考：RFC 3885（SMTP 服务扩展 CHECKPOINT）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/smtp-checkpoint.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
