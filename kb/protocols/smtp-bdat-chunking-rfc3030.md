---
title: "SMTP 的 BDAT/CHUNKING（RFC 3030）解决了什么问题，和 DATA 有什么不同？"
source: "https://ztpop.net/kb/smtp-bdat-chunking-rfc3030.html"
license: CC-BY 4.0
---

# SMTP 的 BDAT/CHUNKING（RFC 3030）解决了什么问题，和 DATA 有什么不同？

1
SMTP 的 BDAT/CHUNKING（RFC 3030）解决了什么问题，和 DATA 有什么不同？
▼

**DATA 的痛点**

传统 DATA 把整封邮件作为文本流发送，正文里每行以「.」开头必须做点填充（dot-stuffing）转义，结尾以单独一行「.」表示结束。这种文本约定对含二进制内容（如 8BITMIME 未覆盖的二进制附件）既脆弱又低效。

**BDAT 的方式**

CHUNKING 扩展引入 BDAT 命令：客户端声明每块字节数，服务端按字节数接收，不再依赖「.」定界，也无需点填充。最后一块带 LAST 标记表示结束。这天然适合二进制与超长邮件，且能边收边校验。

**实践注意**

BDAT 常与 BINARYMIME、SIZE 一起协商；现代大型发送服务与部分网关支持它，但并非所有 MTA 都实现。使用 BDAT 时认证/计费可在 LAST 前完成，便于拒绝超大邮件而不必收完。发送方需先确认对端 EHLO 含 CHUNKING。

参考：RFC 3030《SMTP Service Extensions for Transmission of Large and Binary MIME Messages》、RFC 6152《8BITMIME》。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/smtp-bdat-chunking-rfc3030.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
