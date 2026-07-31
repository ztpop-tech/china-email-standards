---
title: "SendGrid 建议把服务器 host 指向哪里？为什么不要硬编码 IP？"
source: "https://ztpop.net/kb/sendgrid-faq-04.html"
license: CC-BY 4.0
---

# SendGrid 建议把服务器 host 指向哪里？为什么不要硬编码 IP？

1
SendGrid 建议把服务器 host 指向哪里？为什么不要硬编码 IP？
▼

**建议**

应将 host 设为 https://api.sendgrid.com/v3/，不要直接写 SendGrid 的 IP 地址——其 IP 可能不定期变更，硬编码会在无预警时导致集成中断。

参考：SendGrid Docs “Setting Server Host”

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/sendgrid-faq-04.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
