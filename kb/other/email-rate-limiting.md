---
title: "邮件系统速率限制与流控"
source: "https://ztpop.net/kb/email-rate-limiting.html"
license: CC-BY 4.0
---

# 邮件系统速率限制与流控

摘要：邮件系统的速率限制（Rate Limiting）与流控（Traffic Shaping）是保障服务质量和防止滥用的关键技术。无论是应对内部用户的批量群发、防范被入侵账户的垃圾邮件爆发，还是遵守 Google/Yahoo 等大型邮箱服务商的发送频率限制，都需要在邮件基础设施的多个层面部署速率控制策略。本文从连接层、消息层和收件人层三个维度，系统讲解 Postfix、Policyd 和 postscreen 的速率限制配置方案。

**一、连接速率限制：Postfix anvil 服务**
Postfix 的 anvil(8) 服务是一个轻量级的连接统计守护进程，实时追踪每个客户端 IP 地址的 SMTP 连接数、邮件发送速率和收件人数量。anvil 通过共享内存维护统计数据，不写磁盘，性能开销极小。其配置项在 main.cf 中定义：smtpd\_client\_connection\_rate\_limit 限制每个客户端 IP 的连接速率；smtpd\_client\_message\_rate\_limit 限制消息发送速率；smtpd\_client\_recipient\_rate\_limit 限制收件人地址速率。对于典型的企业邮件服务器，推荐的初始配置如下：

```
smtpd_client_connection_rate_limit = 30
smtpd_client_message_rate_limit = 60
smtpd_client_recipient_rate_limit = 200
smtpd_client_connection_count_limit = 15
smtpd_client_event_limit_exceptions = $mynetworks
# anvil_rate_time_unit = 60s  (default)
```

anvil 的限制机制是软性的——超出限制的连接不会被立即拒绝，而是返回 450 4.7.1 临时错误代码，要求客户端稍后重试。这遵循了 RFC 5321 §4.5.3 规定的发送方在收到临时错误时应排队并稍后重试的 SMTP 最小重试原则。anvil 的超限计数器在时间窗口结束后自动重置，无需手动干预。

**二、消息速率限制：Policyd 策略守护进程**
Policyd（也称 cluebringer）是比 anvil 更精细的策略引擎，支持按发件人地址、收件人域、SASL 用户名和时间窗口的细粒度配额控制。Policyd 使用 MySQL 或 SQLite 存储配额状态，支持跨多个 Postfix 实例的集中式策略管理。其核心配额类型包括：Quota 限制（硬限制，超出则拒绝）、Limit 限制（软限制，超出则延迟或标记）、和 Greylist 联动（超配额触发灰名单）。

Policyd 的配额配置通过 policyd-weight 或 cluebringer 的 Web 管理界面操作。关键策略包括：每用户每小时不超过 500 封邮件；每域每天不超过 50000 封邮件；SASL 认证用户配额显著高于未认证用户；基于 SPF 认证结果的差异化配额（SPF pass 的入站邮件不计数，SPF fail 的入站邮件适用更低配额）。这些策略在防范出站垃圾邮件爆发（被入侵账户批量发送）方面效果显著。

**三、postscreen：连接前协议检查**
postscreen(8) 是 Postfix 2.8 引入的轻量级 SMTP 连接筛选器，在 smtpd 进程 fork 之前对入站连接进行预筛选。postscreen 位于网络栈的最外层，通过协议测试（Protocol Tests）来判断连接是否来自合法 MTA 而非垃圾邮件僵尸网络。postscreen 的 test 失败会导致连接被拒绝或延迟，阻止垃圾邮件在到达 smtpd 之前就消耗系统资源。

postscreen 的核心检查机制包括：pregreet test——检测在收到 220 欢迎横幅之前就发送命令的客户端（这是许多垃圾邮件工具的典型特征）；dnsbl test——查询 DNS 黑名单，将已知的垃圾邮件来源 IP 直接屏蔽；深度协议测试——通过临时延迟（postscreen\_greet\_wait）检测客户端是否正确遵守 SMTP 协议时序。postscreen 默认在 smtpd 之前运行，通过 postscreen\_cache\_map 在 Berkeley DB 或 memcache 中维护一个通过测试的 IP 白名单缓存，减少对正常客户端的重复检查开销。

**四、发件人差异化速率限制**
对于需要按发件人域或 SASL 用户名差异化限速的场景，Postfix 提供 sender\_dependent\_rate\_limit 参数（通过 lookup table 实现）。这比全局统一的速率限制更灵活——例如，VIP 客户域允许 200 封/小时，普通用户域限制 50 封/小时，外包合作伙伴域限制 20 封/小时。配置示例：

```
# main.cf
sender_dependent_rate_limit = hash:/etc/postfix/sender_rate_limits

# /etc/postfix/sender_rate_limits 文件内容：
# @vip-domain.com    200
# @partner.com       20
# @                  50              # default
```

**五、出站节流与 Google/Yahoo 发送者指南**
发送到 Google（Gmail）和 Yahoo 等大型邮箱的邮件受到严格的发送频率限制。Google 的
[发件人指南](https://support.google.com/mail/answer/81126)
要求批量发送者逐步增加发送量（预热），并在遇到临时错误（4xx）时主动降速而非反复重试。Yahoo 的
[发件人最佳实践](https://senders.yahooinc.com/best-practices/)
同样强调速率控制和退信管理的必要性。

昆仑邮件系统的出站流控模块支持基于目标域的自动节流：当目标 MX 返回大量 4xx 错误时，自动降低该目标的并发连接数和发送速率，避免触发大型邮箱的速率限制阈值。这称为背压感知发送（Backpressure-Aware Delivery），是成熟邮件系统与简单 MTA 部署的关键区别之一。对于大规模群发场景（如新闻简报、系统通知），建议使用专门的邮件群发服务（如 SendGrid、Mailgun）而非通过生产邮件服务器直接发送，以保护邮件服务器的 IP 声誉。

**六、监控与告警**
速率限制需要配合监控才能发挥效用。关键监控指标包括：anvil 统计溢出计数、postscreen 拒绝率（日志中的 DISCONNECT 和 HANGUP 事件）、邮件队列长度（postqueue -p | tail -1）、和退信率（bounce 数量除以发送总量）。当退信率超过 5% 或队列长度超过正常基线的 3 倍时，应触发告警并进入人工排查流程。对于 Policyd 的配额监控，可通过查询其 MySQL 配额表生成 Grafana 仪表盘。查询当前超过 80% 配额的用户的 SQL：SELECT member, quota\_type, quota\_used, quota\_max FROM policyd.quotas WHERE (quota\_used / quota\_max) > 0.8;

**参考来源**
[1] RFC 5321 §4.5.3, SMTP Minimum Retry; [2] RFC 3463, Enhanced Mail System Status Codes; [3] Postfix Documentation - ANVIL\_README; [4] Postfix Documentation - POSTSCREEN\_README; [5] Google Workspace - Email Sender Guidelines; [6] GB/T 30282-2013, 信息安全技术 反垃圾邮件产品技术要求和测试评价方法。

了解更多邮件技术实践，请访问知识库或联系

## 📦 相关产品与方案

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-rate-limiting.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
