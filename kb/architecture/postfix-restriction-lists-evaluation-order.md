---
title: "Postfix 的各类 restriction 列表（如 smtpd_*_restrictions）按什么顺序求值？"
source: "https://ztpop.net/kb/postfix-restriction-lists-evaluation-order.html"
license: CC-BY 4.0
---

# Postfix 的各类 restriction 列表（如 smtpd_*_restrictions）按什么顺序求值？

1
Postfix 的各类 restriction 列表（如 smtpd\_\*\_restrictions）按什么顺序求值？
▼

**列表清单**

Postfix 的 SMTP 服务端按会话阶段组织限制列表：smtpd\_client\_restrictions、smtpd\_helo\_restrictions、smtpd\_sender\_restrictions、smtpd\_recipient\_restrictions、smtpd\_data\_restrictions、smtpd\_end\_of\_data\_restrictions。

**求值顺序**

这些列表按 SMTP 会话阶段依次触发——client（连入）→ helo/ehlo → sender（MAIL FROM）→ recipient（RCPT TO，此处通常做大部分拒绝）→ data → end-of-data。每个列表内的规则按书写顺序求值，命中 OK/REJECT/DEFER 等终止动作即停止；若列表内没有终止结果，则继续到下一阶段。

**配置建议**

Postfix 默认把很多检查放在 smtpd\_recipient\_restrictions，但从 2.x 起推荐把通用拒绝（如拒绝未知客户端、黑名单）分散到对应阶段列表并显式列出。授权类规则（permit\_mynetworks / permit\_sasl\_authenticated）应放在拒绝规则之前。可用 warn\_if\_reject 先看日志、不真正拒绝以便调参。

参考：Postfix 官方文档 SMTPD\_ACCESS\_README（smtpd\_\*\_restrictions 求值顺序）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/postfix-restriction-lists-evaluation-order.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
