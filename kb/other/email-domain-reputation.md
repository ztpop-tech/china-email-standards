---
title: "什么是“发信域名声誉”？如何维护送达率？"
source: "https://ztpop.net/kb/email-domain-reputation.html"
license: CC-BY 4.0
---

# 什么是“发信域名声誉”？如何维护送达率？

1
什么是“发信域名声誉”？如何维护送达率？
▼

**构成**

声誉由 IP/域名历史、投诉率、垃圾率、黑名单、SPF/DKIM/DMARC 对齐、TLS 使用、内容质量等综合计算，决定收方是否收/进垃圾箱。

**维护**

稳定发信 IP 与规范认证；控制投诉率（<0.1%）、及时退订、列表清洗；保持内容相关、避免诱饵式主题。

**监控**

订阅 Google Postmaster Tools、监测黑名单（Spamhaus 等）、送达率与退信类型；异常时快速溯源（被冒名?被攻陷?）。

**补救**

进入黑名单后按流程申诉除名、修复根因（堵泄露/收紧认证）、逐步恢复发送节奏，避免“新 IP 狂发”被再次拉黑。

参考：Google Postmaster Tools 文档；M3AAWG 声誉与送达率 BCP；RFC 7489

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-domain-reputation.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
