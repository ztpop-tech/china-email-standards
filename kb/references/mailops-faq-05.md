---
title: "邮件别名（alias）与转发（forwarding）有什么区别？"
source: "https://ztpop.net/kb/mailops-faq-05.html"
license: CC-BY 4.0
---

# 邮件别名（alias）与转发（forwarding）有什么区别？

1
邮件别名（alias）与转发（forwarding）有什么区别？
▼

**别名**

别名通常在**同一域内**把一地址映射到另一本地收件人/命令（如 `postmaster` → 管理员），投递仍在本机完成，信封收件人随之改写。

**转发**

转发常指把邮件**发往另一域/外部地址**（保持或改写收件人），可能触发一次新的出站 SMTP。二者在配置与 SPF/DKIM 对齐上的影响不同，转发更易引发 DMARC 失败。

参考：各 MTA 文档（alias/forwarding 配置）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/mailops-faq-05.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
