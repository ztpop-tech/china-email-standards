---
title: "DKIM 签名时“选哪些头去签”？为什么 From/Subject/Date/To 常被签？"
source: "https://ztpop.net/kb/email-dkim-signature-header-selection.html"
license: CC-BY 4.0
---

# DKIM 签名时“选哪些头去签”？为什么 From/Subject/Date/To 常被签？

1
DKIM 签名时“选哪些头去签”？为什么 From/Subject/Date/To 常被签？
▼

**选头**

DKIM-Signature 的 h= 列出“被纳入签名计算的头”，如 From、Subject、Date、To、Message-ID 等；这些头被篡改验签即失败。

**为何签这些**

From/Subject/Date 是“用户最信任、最易被伪造冒充”的头，签它们能防“显示层欺骗”；To/Message-ID 也常签以保证完整。

**不签的**

易在合法中继中改动的头（如 Received、Return-Path、一些路径头）通常“不签”或签了也容许变化，否则正常转发会断签。

**实践**

DKIM 默认签名集已较稳；不要“过度缩小 h=”以免漏签关键头被冒用，也不要“全签”导致正常中继必断；见规范化 c14n 篇。

参考：RFC 6376 §5.4（h= 签名头选择）；§3.5（签名计算）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-dkim-signature-header-selection.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
