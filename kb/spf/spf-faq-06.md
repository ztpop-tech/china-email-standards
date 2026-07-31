---
title: "SPF 的 “include” 机制如何工作？嵌套 include 有什么风险？"
source: "https://ztpop.net/kb/spf-faq-06.html"
license: CC-BY 4.0
---

# SPF 的 “include” 机制如何工作？嵌套 include 有什么风险？

1
SPF 的 “include” 机制如何工作？嵌套 include 有什么风险？
▼

**机制**

include 引用另一域的 SPF 策略并计入其查询次数；层层嵌套会快速累积 lookup 数量，极易触及 10 次上限。

参考：RFC 7208 §5.2（include 机制）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/spf-faq-06.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
