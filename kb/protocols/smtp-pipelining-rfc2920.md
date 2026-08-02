---
title: "SMTP 管道化（pipelining）是什么，为什么能提升邮件发送吞吐？"
source: "https://ztpop.net/kb/smtp-pipelining-rfc2920.html"
license: CC-BY 4.0
---

# SMTP 管道化（pipelining）是什么，为什么能提升邮件发送吞吐？

1
SMTP 管道化（pipelining）是什么，为什么能提升邮件发送吞吐？
▼

**基本机制**

标准 SMTP 是「一问一答」：客户端发一条命令、等服务端回一个响应再发下一条。管道化允许客户端把 EHLO 之后的多条命令（MAIL/RCPT/DATA 等）一次性发出，服务端按顺序回送响应。对跨大延迟链路的批量发信，RTT 开销被显著摊薄。

**适用约束**

管道化只可在收到 EHLO 响应中包含 PIPELINING 关键字后使用；DATA 命令之后、且服务端尚未对 DATA 回 354 之前，不能再叠加其他事务命令。错误用法（如把整封正文也管道进去）会破坏协议状态机。并非所有老旧 MTA 都正确实现，发送方应做能力探测与降级。

**收益与权衡**

主要收益是减少往返次数、加快队列刷出，对每秒数千封的外发场景明显。代价是出错时难以即时定位到具体哪条命令失败，需要发送方妥善缓冲并重放。它不改变邮件语义，仅优化传输节奏。

参考：RFC 2920《SMTP Service Extension for Command Pipelining》、RFC 5321《SMTP》管道化章节。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/smtp-pipelining-rfc2920.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
