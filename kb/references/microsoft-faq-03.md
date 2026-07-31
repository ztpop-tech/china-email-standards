---
title: "Microsoft 365 的 DKIM 如何工作（选择器与 CNAME）？"
source: "https://ztpop.net/kb/microsoft-faq-03.html"
license: CC-BY 4.0
---

# Microsoft 365 的 DKIM 如何工作（选择器与 CNAME）？

1
Microsoft 365 的 DKIM 如何工作（选择器与 CNAME）？
▼

**说明**

Microsoft 365 会为你的域名提供 DKIM 签名。你需要在 DNS 中为两个 DKIM 选择器（selector）发布 CNAME 记录，指向 Microsoft 的签名密钥；邮件从 Microsoft 365 发出时由对应私钥签名，接收方用 DNS 中的公钥验证签名。启用 DKIM 是满足 DMARC 对齐（alignment）的前提条件之一。

**建议**

在 Microsoft 365 中启用 DKIM 后，记得同时确认 SPF 已正确配置、DMARC 记录已发布，三者配合才能让你的邮件通过 DMARC 认证、降低被冒名与进垃圾箱的概率。

参考：Microsoft Learn《Email authentication and anti-spoofing》· learn.microsoft.com/exchange/email-authentication-anti-spoofing

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/microsoft-faq-03.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
