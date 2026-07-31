---
title: "邮件列表转发时如何兼顾 DMARC？SRS 与重签名的作用是什么？"
source: "https://ztpop.net/kb/list-faq-08.html"
license: CC-BY 4.0
---

# 邮件列表转发时如何兼顾 DMARC？SRS 与重签名的作用是什么？

1
邮件列表转发时如何兼顾 DMARC？SRS 与重签名的作用是什么？
▼

**对齐被打破**

列表转发会改变信封发件人（MAIL FROM）与可能改写正文/头，使原始 SPF 域（信封）与 DKIM（被改则失效）都不再与 From 域对齐，DMARC 易判失败。

**SRS 重写信封**

SRS（Sender Rewriting Scheme）把转发后的信封发件人重写为列表域的可逆形式，使退信能正确回传，同时让 SPF 在转发跳对齐到列表域而非原始域。

**列表侧 DKIM 重签**

列表管理器用自己的域对转发邮件重新做 DKIM 签名，使 DKIM 对齐到列表域；再配合 List-Id 等头与正确的退订机制，能在保留列表功能的同时让 DMARC 通过。

参考：RFC 7489（DMARC）；SRS 实践；RFC 6376（DKIM）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/list-faq-08.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
