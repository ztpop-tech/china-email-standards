---
title: "SMTP PRDR 扩展（RFC 3461）是什么？它如何配合 CHUNKING 做“逐收件人”响应？"
source: "https://ztpop.net/kb/smtp-prdr.html"
license: CC-BY 4.0
---

# SMTP PRDR 扩展（RFC 3461）是什么？它如何配合 CHUNKING 做“逐收件人”响应？

1
SMTP PRDR 扩展（RFC 3461）是什么？它如何配合 CHUNKING 做“逐收件人”响应？
▼

**定义**

PRDR（Per-Recipient Data Response，RFC 3461）是一个 SMTP 扩展：配合 CHUNKING 使用时，服务器在 BDAT 结束（LAST）后，不是只回一个总响应，而是为每个 RCPT TO 收件人单独回一行响应，标明该收件人是否被接受。

**机制**

客户端先声明 CHUNKING 与 PRDR，分块发邮件（BDAT），最后 BDAT LAST；服务器逐收件人回 “250 OK RCPT ”/“550 拒收 ”，客户端据此精确知道谁成功谁失败。

**价值**

对“一封发往多个收件人、但部分被拒”的场景（如群发中某些地址超限/不存在），能精确区分结果，避免整封重投或误判；提升批量投递的可观测性。

**依赖**

PRDR 必须建立在 CHUNKING（RFC 3030）之上，不能用在 DATA 命令模式；二者均为“无 SIZE 上限、分块传输”的现代能力。

参考：RFC 3461（SMTP DSN，PRDR 作为扩展）；RFC 3030（CHUNKING）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/smtp-prdr.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
