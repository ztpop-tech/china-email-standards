---
title: "我需要接收 DMARC 失败报告（ruf=）吗？"
source: "https://ztpop.net/kb/dmarc-faq-06.html"
license: CC-BY 4.0
---

# 我需要接收 DMARC 失败报告（ruf=）吗？

1
我需要接收 DMARC 失败报告（ruf=）吗？
▼

**说明**

在充分读懂并接受"将收到大量邮件"之前，不需要。失败报告对取证分析很有用（可发现自身发信软件的 bug 或某些钓鱼/冒名攻击），但每当接收方因你的 DMARC 策略拒绝一封邮件，就会立即发送一份失败报告，甚至邮件被接收但某项认证未通过对齐时也会发送。失败报告可能是被拒邮件的完整副本（ARF 格式）。任何伪造你域名的邮件也会被拒，而你要求收一份副本——其数量可能数倍于你的合法邮件。

**建议**

建议先在监控模式（p=none）仅收聚合报告，读懂报告、预估失败报告量级后，再将 ruf= 指向与 rua= 不同的邮箱。注意并非所有接收方都发送失败报告，是否实施由接收方自行决定。

参考：DMARC.org FAQ · RFC 7489 §7.3（RUF）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/dmarc-faq-06.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
