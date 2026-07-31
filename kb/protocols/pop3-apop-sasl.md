---
title: "POP3 的 APOP 与 SASL 认证（RFC 1939/5034）如何实现“不明文传密码”？"
source: "https://ztpop.net/kb/pop3-apop-sasl.html"
license: CC-BY 4.0
---

# POP3 的 APOP 与 SASL 认证（RFC 1939/5034）如何实现“不明文传密码”？

1
POP3 的 APOP 与 SASL 认证（RFC 1939/5034）如何实现“不明文传密码”？
▼

**APOP**

POP3 APOP 命令用“挑战-响应”：服务器在欢迎横幅给时间戳挑战串，客户端用 MD5(挑战+密码) 响应，密码不以明文传输（RFC 1939 §7.1，MD5 已偏弱）。

**SASL**

现代 POP3 通过 SASL（RFC 5034，配合 STARTTLS）支持 PLAIN/LOGIN/CRAM-MD5/SCRAM 等机制，先 STARTTLS 加密通道再认证，密码在 TLS 内安全传输，推荐。

**风险**

无 TLS 的明文 USER/PASS 会被嗅探；必须“先 STLS(STARTTLS) 再认证”。APOP 因 MD5 弱化仅作兼容，不应作为唯一防护。

**实践**

邮件系统应禁用明文 POP3 端口上的无 TLS 认证，强制 STLS 后 SASL；客户端配置“总是用 SSL/TLS”或 STARTTLS。

参考：RFC 1939 §7.1（APOP）；RFC 5034（POP3 SASL）；RFC 2595（POP3 STARTTLS）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/pop3-apop-sasl.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
