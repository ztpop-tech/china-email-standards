---
title: "邮件里的“一键退订”为什么需要 List-Unsubscribe-Post（RFC 8058）？它解决了什么坑？"
source: "https://ztpop.net/kb/list-unsubscribe-post.html"
license: CC-BY 4.0
---

# 邮件里的“一键退订”为什么需要 List-Unsubscribe-Post（RFC 8058）？它解决了什么坑？

1
邮件里的“一键退订”为什么需要 List-Unsubscribe-Post（RFC 8058）？它解决了什么坑？
▼

**背景**

List-Unsubscribe（RFC 2369）提供 mailto:/https: 退订地址，但“点一下就退订”易误触或滥用；RFC 8058 增加 List-Unsubscribe-Post: List-Unsubscribe=One-Click 头，要求客户端“一键”时同时发 POST 确认。

**机制**

邮件含 List-Unsubscribe-Post: List-Unsubscribe=One-Click 与 List-Unsubscribe: ；用户点退订按钮，客户端向该 URL 发 POST（带 List-Unsubscribe=One-Click 体），服务端确认退订。

**价值**

Yahoo/Google 2024 发件人新规要求大批量发件人必须提供“一键退订”且可用；RFC 8058 让退订“明确、可确认、低误触”，同时防伪造退订请求滥用。

**实践**

营销/列表邮件必须同时带 List-Unsubscribe 与 List-Unsubscribe-Post；网关/ESP 需实现对应 POST 端点，否则影响主流邮箱送达率。

参考：RFC 8058（One-Click List-Unsubscribe）；RFC 2369 / Yahoo-Google 2024 新规

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/list-unsubscribe-post.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
