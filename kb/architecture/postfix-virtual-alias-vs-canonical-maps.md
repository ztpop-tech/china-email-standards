---
title: "Postfix 的 virtual_alias_maps 与 canonical_maps 有什么不同，分别何时用？"
source: "https://ztpop.net/kb/postfix-virtual-alias-vs-canonical-maps.html"
license: CC-BY 4.0
---

# Postfix 的 virtual_alias_maps 与 canonical_maps 有什么不同，分别何时用？

1
Postfix 的 virtual\_alias\_maps 与 canonical\_maps 有什么不同，分别何时用？
▼

**virtual alias**

virtual\_alias\_maps 用于把（本地或虚拟域的）收件地址映射到最终投递地址，可一对多（一份邮件复制给多个收件人）。常用于虚拟域托管、别名、邮件组。仅在"接收方"侧、对最终投递地址生效，不影响信封 sender，也不会改变外发信的 From。

**canonical**

canonical\_maps 对信封 sender 与 recipient 都做规范化/改写，发生在邮件进入队列、SMTP 客户端送出之前。常用于统一内部主机名/域名为对外规范域，或在邮件离开本系统时改写发件人。可分别用 sender\_canonical\_maps / recipient\_canonical\_maps 单独控制方向。

**关键区别与顺序**

virtual alias 只改"收件人/投递"且可多对一/一对多；canonical 可改信封 sender、发生在更早阶段、用于规范化。改写顺序上 canonical 先于 virtual/alias 类映射。

**选用建议**

只想做收件别名/邮件组用 virtual\_alias\_maps；要对外统一发件域或规范化信封用 canonical。

参考：Postfix 官方文档 ADDRESS\_REWRITING\_README / VIRTUAL\_README

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/postfix-virtual-alias-vs-canonical-maps.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
