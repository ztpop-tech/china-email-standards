---
title: "mailto 与 https 两种退订方式在实现上有何区别？"
source: "https://ztpop.net/kb/list-faq-04.html"
license: CC-BY 4.0
---

# mailto 与 https 两种退订方式在实现上有何区别？

1
mailto 与 https 两种退订方式在实现上有何区别？
▼

**mailto 退订**

List-Unsubscribe 值为 mailto: 地址，用户（或客户端代发）向其发送一封空邮件即视为退订请求。实现简单，但依赖邮件往返、易被网关改写，且用户体验弱。

**https 退订**

值为 https:// 链接，通常配合 RFC 8058 的 List-Unsubscribe-Post: List-Unsubscribe=One-Click 头，使客户端能直接 POST 完成退订。需服务端提供可用的退订端点并处理令牌校验。

**推荐组合**

最佳实践是两个都提供：mailto 作为兜底，https/POST 作为首选一键体验。确保两种方式最终都落到同一退订处理流程，避免“有链接但不生效”。

参考：RFC 2369；RFC 8058

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/list-faq-04.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
