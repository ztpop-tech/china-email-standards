---
title: "如何用 SPF 的 redirect 与子域委派（RFC 7208）管理多子域发信？"
source: "https://ztpop.net/kb/subdomain-spf-delegation.html"
license: CC-BY 4.0
---

# 如何用 SPF 的 redirect 与子域委派（RFC 7208）管理多子域发信？

1
如何用 SPF 的 redirect 与子域委派（RFC 7208）管理多子域发信？
▼

**redirect**

在子域 SPF 记录用 redirect=<父域> 直接复用父域策略，无需重复列出机制；如 mkt.example.com 的 SPF 为 “v=spf1 redirect=example.com”，继承 example.com 的全部机制。注意 redirect 后不应再有 mechanism（all 除外语义不同）。

**子域独立**

若子域发信源与父域不同，可写独立 SPF（include 父域 + 自身专属 IP/SaaS），避免父域策略膨胀。

**场景**

营销子域（mkt.）、事务邮件子域（tx.）、分支机构各自 SPF；用 redirect 统一基线，用 include 增补差异。

**注意**

仍是总计 10 次 DNS 查询上限（含 include 递归）；过度嵌套仍会 permerror。子域策略应纳入整体 DMARC 对齐评估（From 用哪个域发）。

参考：RFC 7208 §6.1（redirect 修饰符）；§4（机制）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/subdomain-spf-delegation.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
