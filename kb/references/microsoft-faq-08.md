---
title: "Microsoft 365 的防欺骗（anti-spoofing）保护是什么？"
source: "https://ztpop.net/kb/microsoft-faq-08.html"
license: CC-BY 4.0
---

# Microsoft 365 的防欺骗（anti-spoofing）保护是什么？

1
Microsoft 365 的防欺骗（anti-spoofing）保护是什么？
▼

**说明**

防欺骗保护用于检测并拦截冒用你域名、或冒用你域用户的欺骗邮件。它结合 SPF、DKIM、DMARC，以及对“复合认证”（composite authentication）结果的评估，识别那些未通过认证却伪装成你组织的邮件。防欺骗并非独立开关，而是建立在你域名的邮件认证基础设施之上。

**建议**

为域名正确配置并发布 SPF、DKIM、DMARC，防欺骗保护才能有效工作；否则攻击者仍可借未认证的发信路径冒用你的品牌。

参考：Microsoft Learn《Email authentication and anti-spoofing》· learn.microsoft.com/exchange/email-authentication-anti-spoofing

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/microsoft-faq-08.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
