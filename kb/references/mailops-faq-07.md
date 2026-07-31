---
title: "什么是灰名单（greylisting）？它如何帮助反垃圾邮件？"
source: "https://ztpop.net/kb/mailops-faq-07.html"
license: CC-BY 4.0
---

# 什么是灰名单（greylisting）？它如何帮助反垃圾邮件？

1
什么是灰名单（greylisting）？它如何帮助反垃圾邮件？
▼

**原理**

灰名单在首次见到某（发件IP, 发件人, 收件人）三元组时，临时拒绝（4xx）并要求发送方稍后重试。合规的合法 MTA 会按 SMTP 规范重试，而多数垃圾群发工具为追求速度不会重试，从而被过滤。

**取舍**

优点是误杀低、抵御新兴垃圾源有效；代价是首封邮件会有数分钟延迟。可与 SPF/DKIM/DMARC、RBL 等组合，作为多层过滤的一环。

参考：RFC 6647（greylisting 实践）；各 MTA 文档

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/mailops-faq-07.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
