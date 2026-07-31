---
title: "用 Workers 绑定发送邮件该怎么写？"
source: "https://ztpop.net/kb/cloudflare-faq-05.html"
license: CC-BY 4.0
---

# 用 Workers 绑定发送邮件该怎么写？

1
用 Workers 绑定发送邮件该怎么写？
▼

**绑定**

在 wrangler 配置 send\_email 绑定（name: EMAIL），代码中调用 env.EMAIL.send({to,from,subject,html,text}) 即可发送。

参考：Cloudflare Email Sending Workers API 样例

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/cloudflare-faq-05.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
