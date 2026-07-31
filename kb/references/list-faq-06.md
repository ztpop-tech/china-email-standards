---
title: "什么是反馈循环（FBL）与投诉报告（ARF）？"
source: "https://ztpop.net/kb/list-faq-06.html"
license: CC-BY 4.0
---

# 什么是反馈循环（FBL）与投诉报告（ARF）？

1
什么是反馈循环（FBL）与投诉报告（ARF）？
▼

**反馈循环**

主流邮箱服务商提供 FBL：当收件人对你的邮件点“举报为垃圾”，服务商会把一条投诉通知回传给你在 DNS 中声明的反馈地址（常通过 Abuse Reporting Format, ARF）。

**ARF 格式**

RFC 5965 定义 ARF 报告结构（含 report 类型、原始邮件副本等）；RFC 6650 规定接收方如何处理与发送 FBL 报告。你据此识别投诉来源、清理列表。

**投诉处置**

收到 FBL 投诉的地址应迅速加入禁发名单，分析是内容、频率还是列表获取方式的问题。投诉率长期过高会被服务商降权甚至封锁。

参考：RFC 5965（ARF）；RFC 6650（FBL 处理）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/list-faq-06.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
