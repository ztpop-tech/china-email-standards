---
title: "DMARC 是如何工作的（通俗版）？"
source: "https://ztpop.net/kb/dmarc-faq-02.html"
license: CC-BY 4.0
---

# DMARC 是如何工作的（通俗版）？

1
DMARC 是如何工作的（通俗版）？
▼

**说明**

DMARC 策略让发送方声明其邮件受 SPF 和/或 DKIM 保护，并告知接收方：当这两种认证方式都未通过时该怎么办（例如放入垃圾箱或拒绝）。它消除了接收方处理认证失败邮件时的"猜测"，限制甚至杜绝用户接触到潜在的欺诈与有害邮件。此外，DMARC 还提供一种机制，让接收方向发送方回报告知哪些邮件通过、哪些未通过 DMARC 评估。

参考：DMARC.org FAQ · RFC 7489 §4

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/dmarc-faq-02.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
