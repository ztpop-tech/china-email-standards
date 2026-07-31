---
title: "什么是 Milter？为何 Postfix / Sendmail 的 Milter 框架能让外部程序在邮件传输过程中实时拦截、改写？"
source: "https://ztpop.net/kb/milter-filter-framework.html"
license: CC-BY 4.0
---

# 什么是 Milter？为何 Postfix / Sendmail 的 Milter 框架能让外部程序在邮件传输过程中实时拦截、改写？

1
什么是 Milter？为何 Postfix / Sendmail 的 Milter 框架能让外部程序在邮件传输过程中实时拦截、改写？
▼

**定义**

Milter（Mail Filter）是 Sendmail 定义的邮件过滤 API / 协议，Postfix 等也实现兼容；它允许“外部过滤程序”在 SMTP 会话的关键阶段挂接：connect、helo、mail from、rcpt to、header、body、eom。

**阶段介入**

Milter 可在“收 envelope 阶段”就拒绝（如 RCPT 时据策略拒收），在“收到头/正文时”改写（加头、注入 Disclaimer），在“eom（消息结束）”整体判定放行 / 丢弃 / 改写。

**价值**

相比在 MTA 之后另起进程扫描，Milter 在会话内同步决策，能“连接级拒收”省资源，也支持“边收边扫边改”，是杀毒、SPF/DKIM/DMARC 校验、归档、Disclaimer 的通用接入点。

**实践**

OpenDKIM、OpenDMARC、ClamAV（milter 模式）、PolicyD 等均以 Milter 接入；多个 Milter 按配置顺序串行执行，需注意性能与超时配置。

参考：Sendmail Milter API 文档；Postfix Milter 支持；OpenDKIM / OpenDMARC 实践

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/milter-filter-framework.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
