---
title: "灰名单（greylisting）是什么？为什么能拦垃圾邮件？如何配置？"
source: "https://ztpop.net/kb/greylisting-basics.html"
license: CC-BY 4.0
---

# 灰名单（greylisting）是什么？为什么能拦垃圾邮件？如何配置？

1
灰名单（greylisting）是什么？为什么能拦垃圾邮件？如何配置？
▼

**原理**

greylisting（RFC 6647）在首次见到陌生（IP, 发件人, 收件人）三元组时，以临时拒绝（SMTP 450/4xx）要求对方稍后重试。合法 MTA 会按 RFC 5321 重试，而多数僵尸/群发器不重试或快速放弃，从而被拦。

**实现**

Postfix 可配 postgrey（check\_policy\_service inet:127.0.0.1:10023）；策略服务记录三元组，首次拒绝、短时（如 5 分钟）后放行并缓存一段时间，后续同三元组直接通过。

**代价**

合法首次邮件会延迟数分钟；需维护白名单（可信大服务商 IP、已知伙伴）以免误伤。RFC 6647 提醒注意重试行为与已投递后续邮件的直接放行。

**定位**

灰名单非银弹，现代高级垃圾也会重试；应作为多层防御的一层，配合 SPF/DKIM/DMARC 与内容过滤。

参考：RFC 6647（灰名单）；RFC 5321（SMTP 重试）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/greylisting-basics.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
