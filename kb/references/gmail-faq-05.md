---
title: "大批量发件人为何必须支持一键退订（List-Unsubscribe）？如何设置？"
source: "https://ztpop.net/kb/gmail-faq-05.html"
license: CC-BY 4.0
---

# 大批量发件人为何必须支持一键退订（List-Unsubscribe）？如何设置？

1
大批量发件人为何必须支持一键退订（List-Unsubscribe）？如何设置？
▼

**要求**

每日发送超过 5,000 封邮件时，你的营销类与订阅类邮件必须支持**一键退订**。

**设置**

在发出邮件中包含以下两个头：`List-Unsubscribe-Post: List-Unsubscribe=One-Click` 与 `List-Unsubscribe: <https://example.com/unsubscribe/example>`。用户点击一键退订后，你会收到一个 POST 请求完成退订。这两条头不应被其他退订方式取代。

参考：Google 帮助中心《Email sender guidelines》· support.google.com/mail/answer/81126（RFC 2369 / RFC 8058）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/gmail-faq-05.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
