---
title: "什么是“邮件头注入（Email Header Injection）”？Web 表单发信场景如何被利用、如何防护？"
source: "https://ztpop.net/kb/email-header-injection.html"
license: CC-BY 4.0
---

# 什么是“邮件头注入（Email Header Injection）”？Web 表单发信场景如何被利用、如何防护？

1
什么是“邮件头注入（Email Header Injection）”？Web 表单发信场景如何被利用、如何防护？
▼

**原理**

当 Web 应用用用户输入（姓名/主题/收件人）拼接邮件头却未过滤 CRLF（\r\n）时，攻击者可插入换行注入额外头（如额外 Bcc:/Subject:），把你的邮件系统变成发垃圾/钓鱼的跳板。

**利用**

在“姓名”字段输入“张三\r\nBcc: victim@x.com”，应用若直接拼接，信就被偷偷抄送；更可注入整段正文或改收件人批量发送——属应用层漏洞（CWE-93）。

**防护**

① 对所有进入邮件头的用户输入做 CRLF 过滤（拒绝含 \r\n 的输入）；② 用成熟邮件库而非手工拼字符串构造邮件；③ 对用户输入做白名单/长度限制；④ 网关对“异常多收件人/异常头”告警。

**关联**

这是应用层 CRLF 注入，不同于 SMTP 协议攻击，但后果是邮件系统被滥用，属邮件安全运维必查项，与网关反垃圾策略互补。

参考：CWE-93（CRLF 注入）；OWASP 邮件头注入防护；RFC 5322（头字段语法）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-header-injection.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
