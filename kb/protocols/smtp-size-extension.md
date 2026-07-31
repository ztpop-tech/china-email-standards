---
title: "SMTP 的 SIZE 扩展（RFC 1870）如何提前协商“最大可收信体”？为什么能省带宽？"
source: "https://ztpop.net/kb/smtp-size-extension.html"
license: CC-BY 4.0
---

# SMTP 的 SIZE 扩展（RFC 1870）如何提前协商“最大可收信体”？为什么能省带宽？

1
SMTP 的 SIZE 扩展（RFC 1870）如何提前协商“最大可收信体”？为什么能省带宽？
▼

**机制**

EHLO 返回 SIZE 声明本服务器“可接受的最大信体字节数”；发信方 MAIL FROM 可带 SIZE= 预估本次信体大小。

**早拒**

若预估 SIZE 超过对方上限，发信方可在“传输前”就放弃/报错，避免把几百 MB 传完才被拒（浪费带宽与时延）。

**价值**

对大附件邮件尤其有用——先协商再传，失败早、成本低；也便于收方按 SIZE 做配额与限流决策。

**实践**

现代 MTA 普遍支持 SIZE；邮件系统可据 SIZE 上限做“超大体截断/拒绝”策略，配合 Message Size Limit 防止单信撑爆队列。

参考：RFC 1870（SMTP Service Extension for Message Size）；RFC 5321

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/smtp-size-extension.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
