---
title: "LMTP（RFC 2033）是什么？它与 SMTP 在最终投递上有何不同？"
source: "https://ztpop.net/kb/lmtp-intro.html"
license: CC-BY 4.0
---

# LMTP（RFC 2033）是什么？它与 SMTP 在最终投递上有何不同？

1
LMTP（RFC 2033）是什么？它与 SMTP 在最终投递上有何不同？
▼

**定义**

LMTP（Local Mail Transfer Protocol，RFC 2033）基于 SMTP 语法，但用于“最终投递代理（MDA）与邮件存储”之间交付；把邮件从 MTA 交给本地邮箱（如 Cyrus、Dovecot）。

**与 SMTP 区别**

SMTP 用 2xx 多行确认整批成功；LMTP 对每个 RCPT 单独返回成功/失败（因本地投递可能因单邮箱满而部分失败），不支持队列重试语义，且不能跨网络做中继。

**价值**

MDA 可精确知道“哪个收件人成功存入”，对已成功的不重投；适合 MTA→MDA→ mailbox 的最后一跳，常配合 Sieve 过滤。

**实践**

邮件系统内部（前端 MTA 与后端存储）常用 LMTP 交付；对外收发仍用 SMTP/ESMTP。

参考：RFC 2033（LMTP 本地邮件传输协议）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/lmtp-intro.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
