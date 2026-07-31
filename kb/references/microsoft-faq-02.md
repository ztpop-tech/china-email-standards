---
title: "什么是 SCL（垃圾邮件置信度级别）？各级别代表什么？"
source: "https://ztpop.net/kb/microsoft-faq-02.html"
license: CC-BY 4.0
---

# 什么是 SCL（垃圾邮件置信度级别）？各级别代表什么？

1
什么是 SCL（垃圾邮件置信度级别）？各级别代表什么？
▼

**说明**

SCL（Spam Confidence Level，垃圾邮件置信度级别）是 Microsoft 365 给邮件打的“垃圾置信度”分值。**Spam** 对应 SCL 5–6；**High confidence spam** 对应 SCL 7–9。你无法完全关闭垃圾过滤，但可以用 Exchange 邮件流规则（传输规则）绕过大部分入站垃圾过滤——不过对 SecOps 邮箱或钓鱼模拟邮件不应使用邮件流规则绕过。反垃圾邮件头会说明一封邮件为何被标记、或为何跳过了垃圾过滤。

参考：Microsoft Learn《Anti-spam protection》· SCL 说明 learn.microsoft.com/microsoft-365/security/office-365-security/anti-spam-spam-confidence-level-scl-about

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/microsoft-faq-02.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
