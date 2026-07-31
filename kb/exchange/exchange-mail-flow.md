---
title: "Exchange 邮件流（Mail Flow）由哪些角色组成？内外投递如何路由？"
source: "https://ztpop.net/kb/exchange-mail-flow.html"
license: CC-BY 4.0
---

# Exchange 邮件流（Mail Flow）由哪些角色组成？内外投递如何路由？

1
Exchange 邮件流（Mail Flow）由哪些角色组成？内外投递如何路由？
▼

**核心角色**

Exchange 现代架构（2013+）由 Mailbox server（含传输服务：前端 Front End Transport、枢纽 Hub Transport、邮箱 Mailbox Transport）负责路由；边缘传输（Edge Transport，可选 DMZ 角色）承担入站/出站边界安全。

**入站**

外部邮件经 MX→边缘/前端→Hub 按收件人数据库（AD 拓扑）路由→目标邮箱；出站反之，Hub 经发送连接器（Send Connector）发往外部。

**连接器**

接收连接器（Receive Connector）控制“谁可以连、用什么端口/认证”，发送连接器决定“发往哪、走什么智能主机/TLS”；是 Exchange 邮件流的开关总闸。

**运维要点**

邮件流故障先查队列（Queue Viewer）、连接器权限与 TLS、连接器作用域（scope）；与防 spam/DLP 设备串联时注意端口与会话顺序。

参考：Microsoft Exchange Server 邮件流文档；RFC 5321（SMTP 传输）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/exchange-mail-flow.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
