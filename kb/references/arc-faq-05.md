---
title: "ARC 的“链式”结构（i= 实例序号、ARC set）是如何工作的？"
source: "https://ztpop.net/kb/arc-faq-05.html"
license: CC-BY 4.0
---

# ARC 的“链式”结构（i= 实例序号、ARC set）是如何工作的？

1
ARC 的“链式”结构（i= 实例序号、ARC set）是如何工作的？
▼

**实例序号**

每经过一个支持 ARC 的中介，就追加一个“ARC set”，其 `i=` 顺序递增（第一跳 i=1，下一个 i=2……）。每个 set 都含自己的 AAR/AMS/AS。

**链式绑定**

第 i 个 AS 不仅封印第 i 个 AMS 与 AAR，还覆盖之前所有 ARC set（i-1 及更早）。这样任一跳缺失或篡改都会破坏后续 AS 的验证，使链断裂可被检测。

参考：RFC 8617（ARC chain / instance i=）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/arc-faq-05.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
