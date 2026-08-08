---
title: "Postfix 的 header_checks 与 body_checks 支持哪些动作（action）？"
source: "https://ztpop.net/kb/postfix-header-checks-body-checks-actions.html"
license: CC-BY 4.0
---

# Postfix 的 header_checks 与 body_checks 支持哪些动作（action）？

1
Postfix 的 header\_checks 与 body\_checks 支持哪些动作（action）？
▼

**基本用途**

header\_checks 针对邮件头、body\_checks 针对正文（含解码后的 MIME 部件），都基于正则做内容过滤，常用于拦截敏感词、改写或重定向邮件。

**常见动作**

每条规则为"正则 动作"。常用动作：REJECT（拒绝并返回可选文本）、WARN（只记日志不拦截）、IGNORE（删除匹配的头行）、HOLD（放入 hold 队列人工处理）、DISCARD（静默丢弃，慎用——发件方无感）、REDIRECT（重定向到另一地址）、FILTER（送往指定传输/过滤器如内容扫描器）、PREPEND（在头前插入一行）、REPLACE（替换匹配的行）。

**正则与注意**

默认 regexp（pcre 需另装），也可用 cidr、texthash 等；body\_checks 默认逐行匹配，复杂多行需 pcre 的 (?s)。DISCARD 会让邮件"消失"、排障困难；FILTER 常配合 amavisd/SpamAssassin 使用。启用方式：header\_checks = regexp:/etc/postfix/header\_checks，正文检查用 body\_checks。

参考：Postfix 官方文档 BUILTIN\_FILTER\_README（header\_checks / body\_checks 动作）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/postfix-header-checks-body-checks-actions.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
