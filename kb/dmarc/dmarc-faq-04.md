---
title: "DMARC 的 "p=none" 会影响我的邮件正常送达吗？"
source: "https://ztpop.net/kb/dmarc-faq-04.html"
license: CC-BY 4.0
---

# DMARC 的 "p=none" 会影响我的邮件正常送达吗？

1
DMARC 的 "p=none" 会影响我的邮件正常送达吗？
▼

**说明**

不会。p=none 表示域名所有者并不要求接收方在 DMARC 校验失败时采取任何行动。该策略让域名所有者即使尚未部署 SPF/DKIM，也能收到以其域名发出的邮件报告，从而判断域名是否被钓鱼者滥用；邮件处理方式不会发生任何改变，但你将获得对域名下邮件的可见性。

**建议**

若尚未部署 SPF 或 DKIM，建议先单独发布 p=none 策略（因其具备报告能力），一次只改一个参数。待通过报告摸清邮件流后再逐步升级到 p=quarantine 或 p=reject。注意：即使发布 p=none，接收方仍可能基于自有信誉/内容扫描等机制对可疑邮件采取行动，只是你现在能拿到相应统计。

参考：DMARC.org FAQ · RFC 7489 §6.2

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/dmarc-faq-04.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
