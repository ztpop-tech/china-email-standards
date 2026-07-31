---
title: "一封邮件的“标准头字段（RFC 5322）”都各管什么？常看的有哪几个？"
source: "https://ztpop.net/kb/email-rfc5322-header-overview.html"
license: CC-BY 4.0
---

# 一封邮件的“标准头字段（RFC 5322）”都各管什么？常看的有哪几个？

1
一封邮件的“标准头字段（RFC 5322）”都各管什么？常看的有哪几个？
▼

**身份头**

From（发件人）、To/Cc/Bcc（收件人）、Subject（主题）、Date（日期）、Message-ID（唯一ID）、In-Reply-To/References（线索，见线程篇）。

**路由头**

Received（每跳追加，溯源）、Return-Path（信封退信地址）、DKIM-Signature、Authentication-Results、ARC-Seal（认证链）。

**控制头**

List-Id/List-Unsubscribe（列表与退订，见退订篇）、Auto-Submitted（自动信标识）、Content-Type（MIME 类型与编码）。

**实践**

排查/合规/取证都从读头开始；网关与客户端据此做路由、认证、过滤、归档；理解字段语义是邮件运维基本功。

参考：RFC 5322（信头字段语义）；RFC 2369/8058（列表/退订头）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-rfc5322-header-overview.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
