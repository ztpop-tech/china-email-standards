---
title: "我的邮件进了垃圾箱，是 DMARC 的问题吗？"
source: "https://ztpop.net/kb/dmarc-faq-08.html"
license: CC-BY 4.0
---

# 我的邮件进了垃圾箱，是 DMARC 的问题吗？

1
我的邮件进了垃圾箱，是 DMARC 的问题吗？
▼

**说明**

一般来说 DMARC 不处理收件箱放置（inbox placement）。若正确实施 DMARC，它不会改变你的邮件是否被视为垃圾邮件。但若错误配置邮件流导致 DMARC 校验失败，则可能增加被判定为垃圾邮件的概率。简言之，DMARC 不是邮件过滤器，而是作用于"未认证邮件"的策略工具；p=reject 的目标是让接收方拒绝非你方基础设施发出的邮件，而非帮你判断你发出的邮件是否垃圾。

**建议**

强烈建议从 p=none 开始监控，再升级到 quarantine/reject。技术人员可检查 Authentication-Results 头：若看到 spf=pass、dkim=pass、dmarc=pass，则说明认证通过，进垃圾箱与 DMARC 无关，应排查内容/信誉等其他因素。

参考：DMARC.org FAQ · RFC 7489

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/dmarc-faq-08.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
