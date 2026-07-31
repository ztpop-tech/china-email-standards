---
title: "邮件路由环（Routing Loop）是什么？如何检测并避免无限转发？"
source: "https://ztpop.net/kb/email-routing-loop.html"
license: CC-BY 4.0
---

# 邮件路由环（Routing Loop）是什么？如何检测并避免无限转发？

1
邮件路由环（Routing Loop）是什么？如何检测并避免无限转发？
▼

**定义**

路由环指邮件在两个或多个服务器间被反复转发、永不到达终点（如 A 转发给 B、B 又转回 A），消耗资源且永不投递。

**成因**

别名/转发规则配置错误（a→b→a）、MX 指向自身、连接器环路、或两台服务器的“互相中继”误配，都会形成环。

**检测**

① Received 链中出现“同一主机/同一消息 ID 重复出现”；② 队列中邮件 age 暴涨、被反复重试；③ 日志里同一 msgid 在多机来回。现代 MTA 对重复 Received 或跳数上限（Hop Count，常 25–50）会强制退信。

**防护**

设最大跳数（Received 计数超限即退信）、理清别名/转发链、避免 MX 指向会再中继回自身的机器。

参考：RFC 5321 §4.5.4.1（Hop Count 限制）；MTA 转发配置实践

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-routing-loop.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
