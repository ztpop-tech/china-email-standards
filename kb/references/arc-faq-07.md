---
title: "接收方如何在 DMARC 验证失败时，借助 ARC 仍然放行合法邮件？"
source: "https://ztpop.net/kb/arc-faq-07.html"
license: CC-BY 4.0
---

# 接收方如何在 DMARC 验证失败时，借助 ARC 仍然放行合法邮件？

1
接收方如何在 DMARC 验证失败时，借助 ARC 仍然放行合法邮件？
▼

**决策逻辑**

当末跳 DMARC 失败（常见于转发/列表场景），接收方检查 ARC：若整条链 `cv=pass`，且链中某个“受信任中介”的 AAR 显示该邮件早前已通过 SPF/DKIM/DMARC，则可推断失败仅由合法修改引起，予以放行。

**前提**

这依赖接收方对“哪些 ARC 签名方可信”的策略配置（类似对 DKIM 域的信任）。ARC 不自动信任任意签名方。

参考：RFC 8617（receiver handling of ARC）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/arc-faq-07.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
