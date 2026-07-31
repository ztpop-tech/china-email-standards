---
title: "什么是 TLS-RPT（RFC 8460）？它解决什么邮件安全问题？"
source: "https://ztpop.net/kb/tlsrpt-faq-01.html"
license: CC-BY 4.0
---

# 什么是 TLS-RPT（RFC 8460）？它解决什么邮件安全问题？

1
什么是 TLS-RPT（RFC 8460）？它解决什么邮件安全问题？
▼

**定义**

TLS-RPT（SMTP TLS Reporting，RFC 8460）是一套向“发送域”上报 TLS 连接失败的标准机制，让域名所有者能看见自己邮件在外发时遇到的 TLS 问题。

**解决的问题**

MTA-STS/DANE 会在 TLS 失败时直接阻断投递，但发送方往往“只知道邮件没发出去”，看不到原因。TLS-RPT 把每次失败（证书不匹配、对端不支持 STARTTLS、降级攻击迹象等）汇总成报告回传，使配置错误与主动攻击都可被察觉。

参考：RFC 8460（SMTP TLS Reporting）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/tlsrpt-faq-01.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
