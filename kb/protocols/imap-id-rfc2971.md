---
title: "IMAP 的 ID 命令（RFC 2971）是什么？客户端自报身份有何用、又有何隐私顾虑？"
source: "https://ztpop.net/kb/imap-id-rfc2971.html"
license: CC-BY 4.0
---

# IMAP 的 ID 命令（RFC 2971）是什么？客户端自报身份有何用、又有何隐私顾虑？

1
IMAP 的 ID 命令（RFC 2971）是什么？客户端自报身份有何用、又有何隐私顾虑？
▼

**机制**

ID 命令让客户端向服务器自报一组“键值”身份（name、version、os、vendor 等），服务器据以识别“哪个客户端版本”在连。

**用途**

服务端可做“按客户端版本”的兼容/排查、统计活跃客户端分布、对已知 bug 客户端 workaround；运维排错时很有用。

**隐私**

上报 OS/版本可能泄露用户环境；RFC 2971 允许服务器“不要求”且客户端可发空 ID；敏感场景应默认可关。

**实践**

邮件系统可读取并记录客户端 ID 辅助支持；但应尊重隐私，不强制、不把 ID 用于追踪用户，客户端应允许用户关闭上报。

参考：RFC 2971（IMAP4 ID 扩展）；隐私考量

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/imap-id-rfc2971.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
