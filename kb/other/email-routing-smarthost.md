---
title: "什么是“智能主机（Smarthost）”中继？企业为何用 Smarthost 统一出网？"
source: "https://ztpop.net/kb/email-routing-smarthost.html"
license: CC-BY 4.0
---

# 什么是“智能主机（Smarthost）”中继？企业为何用 Smarthost 统一出网？

1
什么是“智能主机（Smarthost）”中继？企业为何用 Smarthost 统一出网？
▼

**定义**

Smarthost 是“代所有内部主机向外发信”的指定中继 MTA；内部服务器不直连外网，而是把邮件交给 Smarthost 统一投递。

**价值**

① 统一出口 IP 与信誉管理（所有出信来自同一干净 IP，便于 SPF/DKIM 对齐）；② 集中策略（防开放中继、限流、扫描、审计）；③ 内网主机无需公网 25 端口；④ 灾备排队。

**配置**

内部 MTA 的 relayhost 指向 Smarthost（如 Postfix: relayhost=）；Smarthost 须对内部网授权中继、对外部严格认证，自身不能成开放中继。

**风险**

Smarthost 是单点，需高可用/多实例；若被攻破即成垃圾源，须强认证 + 监控。

参考：SMTP 中继 / Smarthost 运维实践；RFC 5321（中继模型）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-routing-smarthost.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
