---
title: "SMTP PIPELINING 扩展（RFC 2920）是什么？它如何降低邮件发送延迟？"
source: "https://ztpop.net/kb/smtp-pipelining.html"
license: CC-BY 4.0
---

# SMTP PIPELINING 扩展（RFC 2920）是什么？它如何降低邮件发送延迟？

1
SMTP PIPELINING 扩展（RFC 2920）是什么？它如何降低邮件发送延迟？
▼

**定义**

PIPELINING（RFC 2920）允许客户端在等待服务器对前一条命令的响应之前，连续发送多条命令（如 EHLO 之后一口气发 MAIL/RCPT/DATA），减少网络往返（RTT）次数。

**机制**

客户端批量发出命令，再按序读取响应；服务器按 FIFO 处理并逐一回复。DATA 之后正文仍需等响应。需双方 EHLO 都声明 PIPELINING。

**价值**

对高延迟链路（跨洲、卫星）尤其明显，把多次 RTT 压缩到接近一次，提升吞吐与批量投递效率；现代 MTA 普遍支持。

**注意**

PIPELINING 不得用于 EHLO 之前；若中途某命令出错（如 RCPT 被拒），客户端应正确解析每条响应再决定后续，避免状态错乱。

参考：RFC 2920（SMTP Service Extension for Command Pipelining）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/smtp-pipelining.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
