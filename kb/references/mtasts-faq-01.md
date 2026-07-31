---
title: "什么是 MTA-STS（RFC 8461）？它解决什么邮件安全问题？"
source: "https://ztpop.net/kb/mtasts-faq-01.html"
license: CC-BY 4.0
---

# 什么是 MTA-STS（RFC 8461）？它解决什么邮件安全问题？

1
什么是 MTA-STS（RFC 8461）？它解决什么邮件安全问题？
▼

**定义**

MTA Strict Transport Security（MTA-STS，RFC 8461）由 Microsoft、Google、Yahoo 等邮件服务商共同推出，用于防御 SMTP 会话中的“降级攻击”与“中间人攻击（MITM）”，并弥补电子邮件长期缺乏“安全优先通信标准”的短板。

**解决的问题**

普通 SMTP 默认明文、且对端不支持 STARTTLS 时会静默降级到明文。攻击者可拦在路径上剥离 STARTTLS，使邮件以明文传输被窃听或篡改。MTA-STS 让发送方知道“我方支持并强制 TLS”，从而拒绝不安全投递。

参考：RFC 8461；Cloudflare “Configure MTA-STS”

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/mtasts-faq-01.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
