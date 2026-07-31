---
title: "为什么 SendGrid 不再接受 Basic Auth，必须使用 API Key？"
source: "https://ztpop.net/kb/sendgrid-faq-03.html"
license: CC-BY 4.0
---

# 为什么 SendGrid 不再接受 Basic Auth，必须使用 API Key？

1
为什么 SendGrid 不再接受 Basic Auth，必须使用 API Key？
▼

**说明**

SendGrid 已停用基本认证（用户名/密码），所有请求必须在 Authorization 头中携带 Bearer 类型的 API Key；旧方式会失败。

参考：SendGrid Docs “Info: Basic Authentication is no longer accepted”

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/sendgrid-faq-03.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
