---
title: "Yahoo 从 2024 年 2 月起对发送方强制执行哪些要求？"
source: "https://ztpop.net/kb/yahoo-faq-01.html"
license: CC-BY 4.0
---

# Yahoo 从 2024 年 2 月起对发送方强制执行哪些要求？

1
Yahoo 从 2024 年 2 月起对发送方强制执行哪些要求？
▼

**所有发送方（All Senders）**

自 2024 年 2 月起，Yahoo 开始逐步强制执行以下标准，未达标会影响投递：① 至少实施 SPF 或 DKIM 认证；② 将垃圾邮件投诉率保持在 0.3% 以下；③ 发送 IP 具备有效的正向与反向 DNS 记录；④ 遵守 RFC 5321 与 RFC 5322。

**批量发送方（Bulk Senders）额外要求**

除以上四条外，批量发送方还需：同时实施 SPF 与 DKIM；发布有效的 DMARC 策略（至少 p=none，且 DMARC 必须通过）；支持简易退订（含一键退订）；投诉率同样低于 0.3%。Yahoo 在 2024 上半年边监控合规边逐步铺开执行。

参考：Yahoo《Sender Best Practices》(senders.yahooinc.com/best-practices，2024-02 起强制执行)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/yahoo-faq-01.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
