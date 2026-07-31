---
title: "DKIM 的 ADSP 与 ATPS（RFC 5617）是什么？为何 ADSP 已被废弃？"
source: "https://ztpop.net/kb/dkim-atps.html"
license: CC-BY 4.0
---

# DKIM 的 ADSP 与 ATPS（RFC 5617）是什么？为何 ADSP 已被废弃？

1
DKIM 的 ADSP 与 ATPS（RFC 5617）是什么？为何 ADSP 已被废弃？
▼

**ADSP**

ADSP（Author Domain Signing Practices，RFC 5617 已废弃）曾定义“作者域是否对所有邮件签名”的声明（DKIM=all/discouraged），让接收方判断未签名邮件是否伪造。但它假设所有合法邮件都签名，实践中大量合法转发/未签名邮件导致误伤，被 DMARC 取代。

**ATPS**

ATPS（Authorized Third-Party Signers，同 RFC 5617 附录）描述如何声明“哪些第三方被授权用本域 d= 签名”（解决 SaaS/外包发信用自己域签名却要代表客户域的问题），但同样因复杂与误伤未普及。

**现状**

RFC 5617 已被 DMARC 体系取代；DMARC 用“对齐+策略”更稳妥地解决伪造判定，不再依赖 ADSP 的全签名假设。

**实践**

新部署直接上 DMARC（p=none→quarantine→reject），不要依赖废弃的 ADSP；外包发信用“客户域 include 进 SPF + 满足 DMARC 对齐”即可。

参考：RFC 5617（ADSP/ATPS，已废弃）；由 RFC 7489 DMARC 取代

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/dkim-atps.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
