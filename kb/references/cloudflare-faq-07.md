---
title: "用 SMTP 方式发信如何认证？"
source: "https://ztpop.net/kb/cloudflare-faq-07.html"
license: CC-BY 4.0
---

# 用 SMTP 方式发信如何认证？

1
用 SMTP 方式发信如何认证？
▼

**SMTP**

连接到 smtps://smtp.mx.cloudflare.net:465，--user 设为 “api\_token:<API\_TOKEN>”，用 --upload-file 上传邮件原文（mail.txt）。

参考：Cloudflare Email Sending SMTP 样例

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/cloudflare-faq-07.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
