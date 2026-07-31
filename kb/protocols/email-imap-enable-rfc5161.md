---
title: "IMAP 的 ENABLE 命令（RFC 5161）是做什么的？为什么某些扩展要“显式开启”？"
source: "https://ztpop.net/kb/email-imap-enable-rfc5161.html"
license: CC-BY 4.0
---

# IMAP 的 ENABLE 命令（RFC 5161）是做什么的？为什么某些扩展要“显式开启”？

1
IMAP 的 ENABLE 命令（RFC 5161）是做什么的？为什么某些扩展要“显式开启”？
▼

**背景**

部分 IMAP 扩展（如 CONDSTORE/QRESYNC、METADATA）默认不激活，即使服务器支持，也需客户端“显式开启”才生效。

**机制**

ENABLE <扩展名> 在认证后、选箱前发，告诉服务器“我要用这个扩展”；服务器确认后该扩展能力才对该连接可用（CAPABILITY 会反映）。

**价值**

避免“默认开启可能破坏老客户端”的扩展被强制；客户端按需启用（如启用 QRESYNC 做高效增量同步）。

**实践**

现代客户端用 ENABLE 开启增量同步/元数据等扩展；邮件系统应 advert 并正确响应 ENABLE，确认后才在该连接提供对应能力。

参考：RFC 5161（IMAP ENABLE 扩展）；RFC 4551/5162（CONDSTORE/QRESYNC 需 ENABLE）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-imap-enable-rfc5161.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
