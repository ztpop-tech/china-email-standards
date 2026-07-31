---
title: "IP 被列入 RBL/黑名单后如何“申请除名（delist）”？除名前必须先做什么？"
source: "https://ztpop.net/kb/email-blacklist-delisting.html"
license: CC-BY 4.0
---

# IP 被列入 RBL/黑名单后如何“申请除名（delist）”？除名前必须先做什么？

1
IP 被列入 RBL/黑名单后如何“申请除名（delist）”？除名前必须先做什么？
▼

**先止血**

除名前必须“先停止垃圾来源”：查是开放中继、被盗账号、还是被黑网站，封堵根因；否则除名后会立刻再被拉，且更难解。

**申诉**

到对应 RBL（如 Spamhaus/SpamCop）的 delist 页面提交申诉，说明根因已除、给出证据；部分 RBL 自动过期，部分需人工审核。

**恢复**

除名后 IP 信誉需时间回暖（之前的退信/限流不会瞬间消失），配合 IP 预热（见“IP 预热”篇）渐进恢复发送量。

**预防**

监控自身 IP 是否上榜（定期查 RBL）、保持正向/反向 DNS 正确、限流与 FBL 投诉率可控，从源头避免上榜。

参考：RBL/DNSBL 除名流程（Spamhaus/SpamCop 等）；RFC 展 信誉恢复

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-blacklist-delisting.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
