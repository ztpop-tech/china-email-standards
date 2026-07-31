---
title: "如何“发布 DMARC 记录”并选对策略(p=none/quarantine/reject)？"
source: "https://ztpop.net/kb/email-dmarc-record-howto.html"
license: CC-BY 4.0
---

# 如何“发布 DMARC 记录”并选对策略(p=none/quarantine/reject)？

1
如何“发布 DMARC 记录”并选对策略(p=none/quarantine/reject)？
▼

**结构**

在 \_dmarc.<域> 的 TXT：v=DMARC1; p=<策略>; rua=<聚合报告地址>; ruf=<取证报告地址>; adkim=/aspf=<对齐模式>; pct=<生效比例>。

**策略演进**

p=none（只报告不处置，先观察）→ p=quarantine（可疑进垃圾/隔离）→ p=reject（直接拒）；pct 可先设 50 逐步提升覆盖。

**对齐**

adkim/aspf 设 strict(严格)或 relaxed(宽松)决定“From 与 SPF/DKIM 域多严才算对齐”；多数用 relaxed 兼容转发。

**实践**

先 none 收集数周报告（见 RUA 分析篇）确认合法源全对齐，再逐步 quarantine→reject；配合 SPF/DKIM 才有意义。

参考：RFC 7489（DMARC 记录与策略）；部署演进实践

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-dmarc-record-howto.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
