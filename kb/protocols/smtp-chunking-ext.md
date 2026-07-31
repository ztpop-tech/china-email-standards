---
title: "SMTP CHUNKING 扩展（RFC 3030）是什么？它为何能发超大邮件且避免“先传后拒”？"
source: "https://ztpop.net/kb/smtp-chunking-ext.html"
license: CC-BY 4.0
---

# SMTP CHUNKING 扩展（RFC 3030）是什么？它为何能发超大邮件且避免“先传后拒”？

1
SMTP CHUNKING 扩展（RFC 3030）是什么？它为何能发超大邮件且避免“先传后拒”？
▼

**定义**

CHUNKING（RFC 3030）是 SMTP 扩展：用 BDAT 命令替代传统 DATA，把邮件正文分若干“块（chunk）”发送，最后一块带 LAST 标记表示结束；不再需要“先传完整封信再等响应”。

**与 SIZE 区别**

SIZE 只是在 MAIL FROM 预申报大小、超限在传前拒；CHUNKING 更进一步——传输中即可被中断，且可配合 PRDR 逐收件人响应。

**价值**

发超大附件时无需一次性缓冲整封信，降低内存压力；分块也使传输更可控、可断点续传思路；是 EAI/大邮件场景的现代能力。

**注意**

CHUNKING 必须双方 EHLO 都声明；旧系统不支持时会回退到 DATA 模式。它与 BDAT、PRDR 是一个能力家族，区别于基于 DATA 的传统流程。

参考：RFC 3030（SMTP Service Extensions for Transmission of Large and Binary MIME Messages：CHUNKING/BDAT/BINARYMIME）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/smtp-chunking-ext.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
