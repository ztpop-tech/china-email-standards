---
title: "什么是 SPF（发件方策略框架）？它如何防止我的邮件被当成垃圾邮件？"
source: "https://ztpop.net/kb/google-faq-01.html"
license: CC-BY 4.0
---

# 什么是 SPF（发件方策略框架）？它如何防止我的邮件被当成垃圾邮件？

1
什么是 SPF（发件方策略框架）？它如何防止我的邮件被当成垃圾邮件？
▼

**说明**

SPF（Sender Policy Framework，发件方策略框架）通过为你的域名添加一条 DNS TXT 记录，列出所有被授权代该域名发送邮件的服务器。接收方收到邮件时，会查询该 SPF 记录，验证邮件是否确实来自授权服务器。这有助于防止你的外发邮件被接收方标记为垃圾邮件，也降低他人冒用你域名发信的成功率。

参考：Google Workspace 帮助中心《Set up SPF》· support.google.com/a/answer/173534

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/google-faq-01.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
