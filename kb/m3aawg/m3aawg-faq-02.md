---
title: "SPF 记录应以 ~all 还是 -all 结尾？什么情况下才用 -all？"
source: "https://ztpop.net/kb/m3aawg-faq-02.html"
license: CC-BY 4.0
---

# SPF 记录应以 ~all 还是 -all 结尾？什么情况下才用 -all？

1
SPF 记录应以 ~all 还是 -all 结尾？什么情况下才用 -all？
▼

**正常发送域用 ~all**

对真正发送邮件的域名，M3AAWG 建议 SPF 记录以 `~all`（软失败）结尾，且只授权必要的 IP、使用尽量小的网段；同时应遵循 RFC 7208 的 DNS 查询次数限制，保证记录有效。

**不发送邮件的域用 -all**

对于不发送邮件的域名（例如闲置/停放域名），应按 M3AAWG《保护停放域名最佳实践》发布 `v=spf1 -all`，明确声明“不允许任何主机代发”，以防被冒名发送。

参考：M3AAWG《Email Authentication Recommended Best Practices》(2020-09) 及《Protecting Parked Domains BCP》

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/m3aawg-faq-02.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
