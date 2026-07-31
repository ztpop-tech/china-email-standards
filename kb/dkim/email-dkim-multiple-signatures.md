---
title: "一封信可以有“多个 DKIM 签名”吗？多签名有什么用、要注意什么？"
source: "https://ztpop.net/kb/email-dkim-multiple-signatures.html"
license: CC-BY 4.0
---

# 一封信可以有“多个 DKIM 签名”吗？多签名有什么用、要注意什么？

1
一封信可以有“多个 DKIM 签名”吗？多签名有什么用、要注意什么？
▼

**可以**

DKIM-Signature 头可出现多次，每枚对应不同域/选择器/算法；接收方可任选一枚验过即算“该域已签”。

**用途**

① 过渡期 RSA+Ed25519 双签（见 Ed25519 篇）；② 转发场景保留原始发件人签名、新增转发方签名；③ 委托发送时企业域+ESP 域各签一枚。

**注意**

多签增大信头体积（接近 SMTP 行/信头限制需留意）；DMARC 只需“一枚与 From 对齐且验过”即满足，不必全过；验签失败的那枚不影响其它。

**实践**

部署双签/转发叠加签名时要控体积与 TTL；监控“至少一枚有效对齐”，避免为追求全过而过度复杂。

参考：RFC 6376 §5（多个 DKIM-Signature 头）；RFC 7489（DMARC 仅需一枚对齐）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-dkim-multiple-signatures.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
