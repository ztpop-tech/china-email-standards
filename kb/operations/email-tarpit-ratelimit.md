---
title: "什么是“Tarpit（粘滞/问候延迟）”？它如何用“慢”来惩罚垃圾发送者？"
source: "https://ztpop.net/kb/email-tarpit-ratelimit.html"
license: CC-BY 4.0
---

# 什么是“Tarpit（粘滞/问候延迟）”？它如何用“慢”来惩罚垃圾发送者？

1
什么是“Tarpit（粘滞/问候延迟）”？它如何用“慢”来惩罚垃圾发送者？
▼

**原理**

Tarpit 在 SMTP 会话早期（如 HELO 后、或每读一行）人为延迟响应或极慢读数据，使一次连接耗时从秒级拉长到分钟级，大幅提高滥用者的“时间成本”。

**目标**

僵尸/群发程序追求“快、多”；拖慢后其单位时间内发送量骤降，而正常用户几乎无感（正常会话很快完成）。本质是“以慢制滥”。

**实现**

Postfix postscreen 的 greeting delay（问候延迟）、慢读（slowness）检测；部分防火墙/网关的“粘滞”模式。

**风险**

过度延迟会误伤正常大批量发信方与重试逻辑；建议仅对“可疑源/行为”启用，配合 RBL 与信誉分层。

参考：Postfix postscreen（greet delay / slowness）；反滥用延迟实践

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-tarpit-ratelimit.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
