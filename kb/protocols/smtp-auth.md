---
title: "SMTP AUTH（RFC 4954）是什么？发件认证（SASL）如何在邮件提交中防止冒用？"
source: "https://ztpop.net/kb/smtp-auth.html"
license: CC-BY 4.0
---

# SMTP AUTH（RFC 4954）是什么？发件认证（SASL）如何在邮件提交中防止冒用？

1
SMTP AUTH（RFC 4954）是什么？发件认证（SASL）如何在邮件提交中防止冒用？
▼

**定义**

SMTP AUTH（RFC 4954，原 2554）是 SMTP 服务扩展，允许客户端在提交邮件前用 SASL 机制向服务器证明身份。它主要用于邮件提交（submission，端口 587）与中继控制，防止开放中继被滥发垃圾。

**机制**

客户端 EHLO 看到 AUTH 后，可选 PLAIN/LOGIN/CRAM-MD5/OAUTHBEARER 等 SASL 机制完成认证；认证应在 TLS 之上进行（避免凭据明文暴露）。通过后服务器才允许该连接代表认证用户发信。

**防冒用**

没有 AUTH 的开放中继会被任意第三方用来伪造发件人大量群发；启用 AUTH 后，只有持有凭据的授权用户能经此中继，结合 SPF/DKIM/DMARC 可约束“谁能用本域发信”，降低冒用与信誉损害。

**与发信认证区别**

SMTP AUTH 验证“提交邮件的人”身份（授权提交），而 SPF/DKIM/DMARC 验证“邮件宣称的域”与传输路径的一致性（防伪造）。两者互补：AUTH 管入口、域认证管身份可信度。

参考：RFC 4954（SMTP Service Extension for Authentication）；SASL（RFC 4422）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/smtp-auth.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
