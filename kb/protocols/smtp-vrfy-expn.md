---
title: "SMTP 的 VRFY 与 EXPN 命令（RFC 5321 §3.5）是什么？现代服务器为何常禁用？"
source: "https://ztpop.net/kb/smtp-vrfy-expn.html"
license: CC-BY 4.0
---

# SMTP 的 VRFY 与 EXPN 命令（RFC 5321 §3.5）是什么？现代服务器为何常禁用？

1
SMTP 的 VRFY 与 EXPN 命令（RFC 5321 §3.5）是什么？现代服务器为何常禁用？
▼

**定义**

VRFY（verify）让客户端询问“这个用户名/地址是否有效”，服务器回 250 表示该收件人存在；EXPN（expand）询问“这个邮件列表/别名展开后有哪些成员”，返回成员列表。

**安全考量**

VRFY/EXPN 是攻击者枚举有效账号、探测组织结构的便利工具，易被用于账号 harvesting 与社会工程；因此现代公网 MTA 普遍禁用或返回模糊响应（如 252 不确认存在）。

**内部用途**

在受控的内网或可信任环境，VRFY 可用于目录校验、EXPN 可用于查看别名展开，仍有运维价值，但应限制在可信网络。

**替代**

收件人校验应走后续 SMTP 流程（RCPT TO 的真实响应）或目录服务（LDAP），而非暴露 VRFY 给公网。

参考：RFC 5321 §3.5（VRFY / EXPN 命令）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/smtp-vrfy-expn.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
