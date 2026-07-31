---
title: "DKIM 的“规范化（c14n，RFC 6376）”是什么？simple 与 relaxed 有何区别、为何重要？"
source: "https://ztpop.net/kb/dkim-canonicalization.html"
license: CC-BY 4.0
---

# DKIM 的“规范化（c14n，RFC 6376）”是什么？simple 与 relaxed 有何区别、为何重要？

1
DKIM 的“规范化（c14n，RFC 6376）”是什么？simple 与 relaxed 有何区别、为何重要？
▼

**作用**

签名前要先“规范化”头与信体——把无关空白/换行统一，使签名不因中转微小改动而失效；头与信体各有规范化算法。

**simple**

最严格：几乎原样保留（仅去游离空白），中转任何改动都会验签失败；能检测头被改，但易因合法改写（如换行）断签。

**relaxed**

宽容：折叠空白、小写化头名、去引号空白等；容忍多数合法中继改写，验签更稳；是实际部署的推荐默认。

**组合**

c= 头/信体 各选，常见 relaxed/relaxed 或 relaxed/simple；选错或中转过度改写（改正文）仍会断签，需结合 DMARC 判对齐。

参考：RFC 6376 §3.4（DKIM 规范化）；RFC 6376 §6.1（c= 参数）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/dkim-canonicalization.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
