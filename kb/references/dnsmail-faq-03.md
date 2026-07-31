---
title: "为什么 MX / NS 的目标不能是 CNAME 记录？"
source: "https://ztpop.net/kb/dnsmail-faq-03.html"
license: CC-BY 4.0
---

# 为什么 MX / NS 的目标不能是 CNAME 记录？

1
为什么 MX / NS 的目标不能是 CNAME 记录？
▼

**RFC 约束**

按 DNS 与 SMTP 规范，NS（权威服务器）与 MX（邮件交换）记录的目标不能是 CNAME，必须是真实的主机名（或地址记录）。这是因为 CNAME 表示该名是“别名”，而 NS/MX 需要确定性的最终主机，别名会引入解析歧义与额外查询。

**实际风险**

若 MX 指向 CNAME，部分严格实现会拒绝或产生非预期行为；且 CNAME 链断裂时邮件路由会出错。正确做法是让 MX 指向一个拥有 A/AAAA 的主机名，如 mail.example.com。

**例外与边界**

域名的“裸域（example.com）”常通过 CNAME 到 CDN，但邮件应由子域 mail.example.com 的 MX 承载，二者互不冲突；关键是 MX 的值本身不是 CNAME。

参考：RFC 1034/1035（CNAME 语义）；RFC 5321（MX 目标限制）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/dnsmail-faq-03.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
