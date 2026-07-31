---
title: "Gmail 对每天发送超过 5000 封的批量发件人有什么认证要求？"
source: "https://ztpop.net/kb/google-faq-08.html"
license: CC-BY 4.0
---

# Gmail 对每天发送超过 5000 封的批量发件人有什么认证要求？

1
Gmail 对每天发送超过 5000 封的批量发件人有什么认证要求？
▼

**说明**

所有发往个人 Gmail 账号的发送方都必须配置邮件认证（SPF 或 DKIM）；而每日发送量超过 5000 封的批量发件人，则必须同时配置 SPF、DKIM 和 DMARC 三项认证。这是 Google《Email sender guidelines》对大批量发件人的硬性要求，未满足可能导致邮件被拒或大量进垃圾箱。

参考：Google Workspace 帮助中心《Set up SPF》· support.google.com/a/answer/173534 · Gmail 发件人指南 support.google.com/mail/answer/81126

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/google-faq-08.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
