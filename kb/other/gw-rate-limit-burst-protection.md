---
title: "邮件网关的速率限制怎么设？如何防住突发爆发流量？"
source: "https://ztpop.net/kb/gw-rate-limit-burst-protection.html"
license: CC-BY 4.0
---

# 邮件网关的速率限制怎么设？如何防住突发爆发流量？

**四类限额管的不是同一件事**

Postfix 的 anvil(8) 服务按客户端统计四类指标，对应四个参数：并发连接数 `smtpd_client_connection_count_limit`、单位时间新建连接数 `smtpd_client_connection_rate_limit`、单位时间投递消息数 `smtpd_client_message_rate_limit`、单位时间收件人数 `smtpd_client_recipient_rate_limit`，统计窗口由 `anvil_rate_time_unit`（默认 60 秒）界定。

四者拦截的滥用形态不同：并发数防资源耗尽，连接速率防扫描式探测，消息速率防批量投递，收件人速率防目录收割（对同一连接内枚举大量收件人的行为最有效）。只配其中一个基本等于没配。

**基线取值要从实测分布来，而不是拍脑袋**

先在不限流的状态下采集一个完整业务周期的分布：按客户端 IP 统计每分钟连接数、消息数、收件人数的 P95 与 P99。把限额设在 P99 之上留出余量（常见做法是 P99 的 2 到 3 倍），保证正常业务永远碰不到，只有异常量级才触发。

注意 anvil 的统计是按客户端 IP 的。若入站前面有负载均衡且未做透明代理，所有连接会归并到同一个源 IP，限额会瞬间失效或误伤全网——这种拓扑下必须先解决真实源 IP 透传，否则不要启用客户端级限流。

**必须排除的对象**

内部中继主机、监控探针、自有应用服务器不应受入站限流约束。Postfix 用 `smtpd_client_event_limit_exceptions` 指定豁免网段（默认已包含 `mynetworks`）。已认证的提交连接如果需要更高配额，用 master.cf 的 submission 服务单独覆盖参数，而不是抬高全局阈值。

反过来，对已知的高风险来源不要只调低阈值，而应在更前置的环节（连接级过滤或访问表）直接处置——限流的目的是保护自身容量，不是做内容判定。

**被限流时对端会看到什么**

触发限额后 Postfix 返回 4xx 临时错误（由 `smtpd_client_*_limit` 相关的错误码控制），合规发送方会按 RFC 5321 的重试要求稍后重投，因此对正常业务表现为延迟而非丢失。这也是限流优于直接封禁的原因：判定错了代价可控。

务必不要把这类保护配成 5xx 永久拒绝，那会把误判直接变成丢信。

**突发爆发的处置顺序**

遇到入站量突增，按「先止血、后定性」执行：第一步确认是否单一源 IP 或网段贡献了大部分连接，是则临时收紧该源的连接与消息速率；第二步看收件人分布——收件人高度分散且大量指向不存在地址，是目录收割，应同时收紧收件人速率并确保无效收件人被立即拒绝而非进队列；第三步看是否为自有系统故障导致的自循环（同一发件人反复投递同一主题），这类要在源头停任务，限流只能拖延。

回退同样要有判据：临时限额必须带时间戳与到期时间，事件结束后回到基线值并复盘是否需要调整 P99 基准，避免临时值沉淀成永久配置。

参考：[Postfix anvil(8) 手册页](https://www.postfix.org/anvil.8.html) ｜ [Postfix postconf(5) 配置参数手册](https://www.postfix.org/postconf.5.html) ｜ [RFC 5321 Simple Mail Transfer Protocol](https://www.rfc-editor.org/rfc/rfc5321.html)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/gw-rate-limit-burst-protection.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
