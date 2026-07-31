---
title: "MTA 邮件队列（Queue）是什么？如何管理与排查积压？"
source: "https://ztpop.net/kb/mta-queue-management.html"
license: CC-BY 4.0
---

# MTA 邮件队列（Queue）是什么？如何管理与排查积压？

1
MTA 邮件队列（Queue）是什么？如何管理与排查积压？
▼

**定义**

队列是 MTA 暂存“尚未成功投递”邮件的地方：邮件先入队（active/deferred），投递成功即出队，失败按策略重试。Postfix 有 incoming/active/deferred/bounce/hold 等队列。

**积压信号**

队列长度持续增长、deferred 暴增、磁盘上涨，通常是下游拒收、网络中断、DNS 失灵或目标域限流；需从日志（maillog）定位根因而非盲目清队。

**管理命令**

Postfix 用 mailq/postqueue -p 看队列、postsuper -d 删单件、postqueue -f 强制刷新；Exchange 用 Queue Viewer。切勿直接删整个队列，会丢信。

**运维**

定期监控队列深度与 age，设告警；对长期 deferred 做退信（bounce）清理，防止僵尸邮件无限重试占资源。

参考：Postfix QUEUE\_README；RFC 5321 §4.3/§4.5（队列与重试）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/mta-queue-management.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
