---
title: "Sieve 邮件过滤语言（RFC 5228）是什么？为什么服务端过滤比客户端规则更可靠？"
source: "https://ztpop.net/kb/email-sieve-filter.html"
license: CC-BY 4.0
---

# Sieve 邮件过滤语言（RFC 5228）是什么？为什么服务端过滤比客户端规则更可靠？

1
Sieve 邮件过滤语言（RFC 5228）是什么？为什么服务端过滤比客户端规则更可靠？
▼

**定义**

Sieve 是专为“邮件过滤”设计的可移植脚本语言（if/elsif/keep/discard/redirect/fileinto 等），运行在服务端，按规则自动分类/转发/标记邮件。

**价值**

① 不依赖客户端在线（服务端规则对每封信生效）；② 跨客户端一致（Web/手机/桌面看到同一分类）；③ 标准可移植（换支持 Sieve 的系统规则可迁移）。

**场景**

自动归档、按发件人/主题分拣到文件夹、拒收、自动回复、与 Vacation/校验联动；Cyrus/Dovecot/多数邮件系统支持。

**实践**

企业提供 Sieve 管理能力让用户自助设规则；注意沙箱限制（防无限循环、限制外部访问），避免规则被滥用。

参考：RFC 5228（Sieve 邮件过滤语言）；RFC 5230/5231/5232/5233（扩展）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-sieve-filter.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
