---
title: "调用 SendGrid 发信 API 必须包含哪些组成部分？"
source: "https://ztpop.net/kb/sendgrid-faq-05.html"
license: CC-BY 4.0
---

# 调用 SendGrid 发信 API 必须包含哪些组成部分？

1
调用 SendGrid 发信 API 必须包含哪些组成部分？
▼

**组成**

① host 固定为 https://api.sendgrid.com/v3/；② Authorization 头携带 API Key；③ 提交数据时（POST/PUT）请求体须为 JSON 格式。

参考：SendGrid Docs “Build your API call”

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/sendgrid-faq-05.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
