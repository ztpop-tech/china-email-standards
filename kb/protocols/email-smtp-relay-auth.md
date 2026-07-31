---
title: "“认证中继（Authenticated Relay）”与“邮件提交(587)”有何异同？企业内网如何授权可信中继？"
source: "https://ztpop.net/kb/email-smtp-relay-auth.html"
license: CC-BY 4.0
---

# “认证中继（Authenticated Relay）”与“邮件提交(587)”有何异同？企业内网如何授权可信中继？

1
“认证中继（Authenticated Relay）”与“邮件提交(587)”有何异同？企业内网如何授权可信中继？
▼

**同**

二者都要求 SASL 认证 + TLS 后才允许“代发外部邮件”，目的都是“只让合法用户/系统发外网”，防开放中继。

**异**

Submission（587）面向“终端用户提交待发信”；Authenticated Relay 常指“内部应用/服务器经认证后通过中枢 MTA 中继”，可能走 25/587 取决于架构。

**授权**

中枢 MTA 仅对“已认证身份”或“mynetworks 内受信网段”开放中继；应用用专属账号/密码或 IP 白名单，配合限流与审计。

**实践**

内网应用发信应走“认证中继或 submission”，禁用匿名 25 中继；账号口令与 IP 白名单结合，并监控异常发信量。

参考：RFC 4954（SMTP AUTH）；RFC 6409（Submission）；中继授权实践

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-smtp-relay-auth.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
