---
title: "ARC-Authentication-Results（AAR）字段起什么作用？"
source: "https://ztpop.net/kb/arc-faq-03.html"
license: CC-BY 4.0
---

# ARC-Authentication-Results（AAR）字段起什么作用？

1
ARC-Authentication-Results（AAR）字段起什么作用？
▼

**作用**

AAR 是 Authentication-Results 头的“快照”：每一跳 ARC 签名方把自己对这封邮件的 SPF/DKIM/DMARC 等认证结论，原样记入 AAR，随邮件一起传递。

**意义**

当邮件最终到达接收方、且 DMARC 因转发而失败时，接收方可回看沿途各 AAR，发现“在某一可信中介处本邮件 DMARC 是通过的”，从而有依据放行。

参考：RFC 8617（ARC-Authentication-Results 头）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/arc-faq-03.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
