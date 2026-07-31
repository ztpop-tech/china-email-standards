---
title: "什么是“IP 预热（Warming）”？新发信 IP 如何逐步建立送达信誉？"
source: "https://ztpop.net/kb/email-reputation-ip-warming.html"
license: CC-BY 4.0
---

# 什么是“IP 预热（Warming）”？新发信 IP 如何逐步建立送达信誉？

1
什么是“IP 预热（Warming）”？新发信 IP 如何逐步建立送达信誉？
▼

**问题**

全新/长期闲置的发信 IP 突然大量外发会被主流邮箱当可疑直接进垃圾箱；需“循序渐进”让接收方建立信任。

**方法**

从低量起步（如首日几百封），逐步按日提升发送量；优先发“高互动”用户（内部/活跃订阅者）；保持 SPF/DKIM/DMARC 对齐、内容合规、退订可用。

**配合**

订阅目标服务商的 FBL 与 Postmaster 工具（如 Google/Yahoo Postmaster），监控投诉率/退信率；按接收方分域节流，避免单域骤增触发限流。

**实践**

换 IP/上云发送务必预热数周；信誉是“积累慢、毁掉快”，一旦被标垃圾需更长恢复；与速率限制、反馈回路联动管理。

参考：投递信誉与预热实践（Google/Yahoo Postmaster）；RFC 8058 / FBL

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-reputation-ip-warming.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
