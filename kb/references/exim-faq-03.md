---
title: "Exim 日志出现“no immediate delivery: too many messages received in one SMTP connection”是什么意思？"
source: "https://ztpop.net/kb/exim-faq-03.html"
license: CC-BY 4.0
---

# Exim 日志出现“no immediate delivery: too many messages received in one SMTP connection”是什么意思？

1
Exim 日志出现“no immediate delivery: too many messages received in one SMTP connection”是什么意思？
▼

**含义**

一个 SMTP 客户端可在单条连接里发送任意数量邮件。Exim 服务器起初每收到一封就立即起投递进程；但为避免在大量邮件涌入（典型如宕机恢复后）时启动过多进程，它会在同一连接收到一定数量邮件后停止“即时投递”，改为进队列。

**阈值**

该阈值由 `smtp_accept_queue_per_connection` 控制，默认值为 10。大系统应调大；若是拨号主机、希望单条连接收完所有邮件，可将其设为 0 完全禁用该限制。

参考：Exim FAQ Q0009（exim.org/exim-html-4.40/doc/html/FAQ\_0.html）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/exim-faq-03.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
