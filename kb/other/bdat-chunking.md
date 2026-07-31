---
title: "BDAT/CHUNKING 是什么？为什么大附件邮件要用它替代 DATA 命令？"
source: "https://ztpop.net/kb/bdat-chunking.html"
license: CC-BY 4.0
---

# BDAT/CHUNKING 是什么？为什么大附件邮件要用它替代 DATA 命令？

1
BDAT/CHUNKING 是什么？为什么大附件邮件要用它替代 DATA 命令？
▼

**背景**

传统 SMTP 用 DATA 命令以 7-bit 传输，二进制附件需 Base64 编码（膨胀约 33%）且需先把整封邮件读入内存。RFC 3030 引入 CHUNKING（BDAT）扩展，允许分块、二进制、流式传输。

**BDAT**

RFC 3030 的 BDAT 命令按字节分块发送正文（BDAT  [LAST]），无需 7-bit 约束与转义，二进制可原样传输；末块标 LAST。降低 CPU/内存开销，支持超大附件。

**CHUNKING**

CHUNKING 是伴随扩展，允许将一条消息分成多块 BDAT 发送；配合 BINARYMIME 可传 8 位 MIME。需双方 EHLO 都声明 CHUNKING/BDAT 才可用，否则回退到 DATA。

**价值**

大附件/批量邮件网关、云邮件系统常用 BDAT 提升吞吐与可靠性；配合 SIZE 扩展可做流控。客户端到 MTA 多为 DATA，MTA 间中继更常见 BDAT。

参考：RFC 3030（SMTP 服务扩展：CHUNKING/BDAT/BINARYMIME）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/bdat-chunking.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
