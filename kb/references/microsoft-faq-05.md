---
title: "什么是租户允许/阻止列表（Tenant Allow/Block List）？"
source: "https://ztpop.net/kb/microsoft-faq-05.html"
license: CC-BY 4.0
---

# 什么是租户允许/阻止列表（Tenant Allow/Block List）？

1
什么是租户允许/阻止列表（Tenant Allow/Block List）？
▼

**说明**

租户允许/阻止列表是 Microsoft 365 中用于精细控制邮件流的内置列表，已大体取代旧版反垃圾策略里的“允许/阻止发件人域”列表。你可以在其中创建域名或邮箱的**阻止条目**（阻止向这些地址收发邮件），或将误判的好邮件通过 Microsoft Defender 门户的“提交”页上报 Microsoft，从而生成临时的允许条目（Allow emails with similar attributes）。

**注意**

自 2022 年 9 月起，组织接受域（accepted domains）内的允许发件人/域也必须通过邮件认证（SPF/DKIM/DMARC）检查，才能跳过垃圾过滤。

参考：Microsoft Learn《Anti-spam protection》· Tenant Allow/Block List learn.microsoft.com/microsoft-365/security/office-365-security/tenant-allow-block-list-email-spoof-configure

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/microsoft-faq-05.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
