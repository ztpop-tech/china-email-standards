---
title: "邮件“提交端口 587（Submission，RFC 6409）”与 25 端口发信有何不同？为何现代强制分开？"
source: "https://ztpop.net/kb/smtp-submission-port587.html"
license: CC-BY 4.0
---

# 邮件“提交端口 587（Submission，RFC 6409）”与 25 端口发信有何不同？为何现代强制分开？

1
邮件“提交端口 587（Submission，RFC 6409）”与 25 端口发信有何不同？为何现代强制分开？
▼

**区别**

25 端口是 MTA 之间“中继投递”用；587（Submission）是“终端用户向自己服务器提交待发邮件”用，必须 SASL 认证 + STARTTLS。

**为何分开**

防止普通用户直连外网 25 发垃圾、便于对“已认证用户”限流与审计；接收方也可据此区分“服务器间流量”与“用户提交流量”。

**配置**

邮件系统把 submission 服务（587，常 +465 隐式 TLS）独立部署，关闭其开放中继、强制认证；用户客户端“发件服务器”用 587/465 而非 25。

**实践**

现代 ISP/云厂商普遍封禁出站 25，强制走 587/465 提交；邮件系统须正确提供 submission 服务，否则用户无法外发。

参考：RFC 6409（邮件提交协议 Message Submission）；RFC 8314（SUBMISSION+TLS 端口）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/smtp-submission-port587.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
