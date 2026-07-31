---
title: "通过 REST API 发送邮件的请求格式是什么？"
source: "https://ztpop.net/kb/cloudflare-faq-06.html"
license: CC-BY 4.0
---

# 通过 REST API 发送邮件的请求格式是什么？

1
通过 REST API 发送邮件的请求格式是什么？
▼

**请求**

POST https://api.cloudflare.com/client/v4/accounts/{account\_id}/email/sending/send，带 Authorization: Bearer <token> 与 JSON 体（to/from/subject/html/text）。

参考：Cloudflare Email Sending REST API 样例

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/cloudflare-faq-06.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
