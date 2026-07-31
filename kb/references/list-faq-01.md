---
title: "邮件列表（mailing list）是什么？RFC 2369 定义了哪些 List 头字段？"
source: "https://ztpop.net/kb/list-faq-01.html"
license: CC-BY 4.0
---

# 邮件列表（mailing list）是什么？RFC 2369 定义了哪些 List 头字段？

1
邮件列表（mailing list）是什么？RFC 2369 定义了哪些 List 头字段？
▼

**定义**

邮件列表是由列表管理器（如 Mailman、Sympa）把一封邮件转发给一组订阅者的机制。它广泛用于公告、讨论组与营销群发，关键特征是所有成员共享同一个列表地址。

**RFC 2369 头字段**

规范定义了 List-Id、List-Post、List-Subscribe、List-Unsubscribe、List-Archive、List-Help 等头，使邮件客户端能识别该邮件属于哪个列表，并提供“回复列表/退订/查看归档”等一键操作。

**对认证的影响**

列表转发会改变信封与头，常导致原始 SPF 不对齐、DKIM 被改写；因此现代列表多用 SRS 重写信封发件人、并对列表自身域重新签名，以维持 DMARC 通过。

参考：RFC 2369（List 头字段）；RFC 7208/7489

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/list-faq-01.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
