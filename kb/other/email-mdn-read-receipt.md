---
title: "邮件“已读回执（MDN，RFC 3798）”如何工作？它和退信(DSN)有何区别？"
source: "https://ztpop.net/kb/email-mdn-read-receipt.html"
license: CC-BY 4.0
---

# 邮件“已读回执（MDN，RFC 3798）”如何工作？它和退信(DSN)有何区别？

1
邮件“已读回执（MDN，RFC 3798）”如何工作？它和退信(DSN)有何区别？
▼

**定义**

MDN（Message Disposition Notification）是“收件人已读/已删”的回执：收件客户端显示/打开信时，按 Disposition-Notification-To 头向发件人发回执。

**与 DSN 区别**

DSN 是“投递状态”（到没到服务器），MDN 是“用户处置”（读没读/删没删）；DSN 由 MTA 发，MDN 由收件人客户端发，且需用户/客户端同意才发。

**隐私**

MDN 可泄露“何时读了信”，很多客户端默认“询问是否发送”，或直接不发；发送方不能强制。

**实践**

邮件系统可支持 MDN 请求与发送，但应尊重隐私默认（不静默回报）；勿把 MDN 当“必达”的追踪手段，它常被禁用。

参考：RFC 3798（MDN）；RFC 3461/3464（DSN 对比）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-mdn-read-receipt.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
