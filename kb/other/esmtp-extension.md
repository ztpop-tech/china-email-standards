---
title: "ESMTP 与 EHLO（RFC 1869）是什么？为什么现代邮件都基于它？"
source: "https://ztpop.net/kb/esmtp-extension.html"
license: CC-BY 4.0
---

# ESMTP 与 EHLO（RFC 1869）是什么？为什么现代邮件都基于它？

1
ESMTP 与 EHLO（RFC 1869）是什么？为什么现代邮件都基于它？
▼

**定义**

ESMTP（Extended SMTP，RFC 1869）是 SMTP 的扩展框架：客户端连上后用 EHLO 代替 HELO，服务器返回一系列“服务扩展”行（如 250-STARTTLS、250-SIZE、250-8BITMIME），声明自己支持哪些扩展。

**作用**

EHLO 让双方“协商能力”——只有对端声明支持的扩展才可使用，避免盲目发命令被拒。它是 STARTTLS、SIZE、PIPELINING、AUTH 等所有现代 SMTP 扩展的承载机制。

**与 HELO 区别**

HELO 是原始 SMTP（RFC 821）命令，不支持扩展；EHLO 返回多行扩展清单。若服务器不识 EHLO（罕见老旧系统），客户端回退 HELO 走纯文本 7-bit 传输。

**价值**

没有 ESMTP/EHLO 就没有 TLS 加密、大附件、认证等现代邮件安全能力；它是当前互联网邮件的事实基础。

参考：RFC 1869（SMTP Service Extensions）；RFC 5321 §4.1.1.1（EHLO/HELO）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/esmtp-extension.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
