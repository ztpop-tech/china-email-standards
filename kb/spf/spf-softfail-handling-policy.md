---
title: "SPF 软失败（~all）应如何处理与策略选择？"
source: "https://ztpop.net/kb/spf-softfail-handling-policy.html"
license: CC-BY 4.0
---

# SPF 软失败（~all）应如何处理与策略选择？

1
SPF 软失败（~all）应如何处理与策略选择？
▼

**~all 与 -all 的区别**

SPF 限定词决定未匹配发件 IP 的处置：`-all`（hardfail）表示明确未授权；`~all`（softfail）表示「应视为可疑但不绝对拒绝」；另有 `?all`（neutral）与 `+all`（pass，几乎不用）。很多发件域出于谨慎先用 `~all` 再逐步收紧到 `-all`。

**接收方处理策略**

对 `softfail`，RFC 7208 建议**不应直接拒收**，而应打标（如加 `X-Spam` 头或提升垃圾分）或放入隔离区。若把 ~all 当硬拒，会误杀那些经合法转发、但信封发件域 SPF 未覆盖的邮件。

**与 DMARC 协同**

最终处置应以 DMARC 为主：当 DKIM 或 SPF 任一通过且**对齐**时 DMARC 仍可 pass。因此即便 SPF 为 softfail，只要 DKIM 对齐，邮件仍应正常投递。接收方策略应在 DMARC 层统一，而非单看 SPF 结果。

示例记录：`v=spf1 ip4:203.0.113.0/24 include:_spf.x.com ~all`。

参考：RFC 7208《Sender Policy Framework (SPF) for Authorizing Use of Domains in Email》4.6.2 节限定词语义、RFC 7489 DMARC。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/spf-softfail-handling-policy.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
