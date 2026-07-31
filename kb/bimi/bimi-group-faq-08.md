---
title: "应该在组织域还是每个子域发布 BIMI？能否支持多域名/多 logo？"
source: "https://ztpop.net/kb/bimi-group-faq-08.html"
license: CC-BY 4.0
---

# 应该在组织域还是每个子域发布 BIMI？能否支持多域名/多 logo？

1
应该在组织域还是每个子域发布 BIMI？能否支持多域名/多 logo？
▼

**组织域 vs 子域**

默认 BIMI 记录应发布在组织域（Organizational Domain），并被子域继承；域管理员也可以在某个子域单独发布 BIMI 记录，服务商会优先采用该子域的记录（即使与组织域不同）。

**多域名 / 多 logo**

可以：每个域名和子域都能各自发布 BIMI。若同一域名下需要为不同邮件流使用不同 logo，可使用选择器（selector），并在自定义邮件头 `BIMI-Selector: v=BIMI1; s=newsletter` 中引用，同时在 DNS 中为对应选择器发布匹配记录（不同邮件平台对选择器的支持程度不一）。

参考：BIMI Group《FAQs For Marketers & ESPs》· bimigroup.org/faqs-for-senders-esps

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/bimi-group-faq-08.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
