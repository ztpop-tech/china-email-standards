---
title: "SPF 记录里的 "~all" 和 "-all" 有什么区别？Google 为什么推荐 "~all"？"
source: "https://ztpop.net/kb/google-faq-03.html"
license: CC-BY 4.0
---

# SPF 记录里的 "~all" 和 "-all" 有什么区别？Google 为什么推荐 "~all"？

1
SPF 记录里的 "~all" 和 "-all" 有什么区别？Google 为什么推荐 "~all"？
▼

**说明**

`~all`（软失败）告诉接收方：来自记录所列服务器之外的邮件应被标记为垃圾邮件；`-all`（硬失败）则要求接收方直接拒绝这类邮件。Google 推荐使用 `~all`，因为它在严格性与兼容性之间更平衡——即便配置出现疏漏，也不至于把合法邮件直接拒掉，只是放进垃圾箱由用户复核。

参考：Google Workspace 帮助中心《Set up SPF》· support.google.com/a/answer/173534

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/google-faq-03.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
