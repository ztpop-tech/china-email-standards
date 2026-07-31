---
title: "“~all” 和 “-all” 有什么区别？应该选哪个？"
source: "https://ztpop.net/kb/spf-faq-03.html"
license: CC-BY 4.0
---

# “~all” 和 “-all” 有什么区别？应该选哪个？

1
“~all” 和 “-all” 有什么区别？应该选哪个？
▼

**区别**

~all 为软失败（接收方可标记或放入垃圾箱但不直接拒收），-all 为硬失败（直接拒绝）。建议先以 ~all 渐进验证，确认无误后再切到 -all。

参考：RFC 7208 §4.6.1 / Google Workspace 发件人指南

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/spf-faq-03.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
