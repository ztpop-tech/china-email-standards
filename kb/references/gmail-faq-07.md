---
title: "Gmail 对邮件格式与基础设施（From、PTR、显示名）有什么要求？"
source: "https://ztpop.net/kb/gmail-faq-07.html"
license: CC-BY 4.0
---

# Gmail 对邮件格式与基础设施（From、PTR、显示名）有什么要求？

1
Gmail 对邮件格式与基础设施（From、PTR、显示名）有什么要求？
▼

**格式**

HTML 邮件应遵循 HTML 标准；`From:` 头只能包含一个邮箱地址；避免过大的邮件头；每封邮件须包含合法的 `Message-ID`；邮件头与内容应准确、不误导，不要用 emoji 或非标准字符模仿图形元素，也不要用 HTML/CSS 隐藏内容。

**基础设施**

发送 IP 必须与 PTR 记录中主机名对应的 IP 一致（反向 DNS），且该主机名也须有 A/AAAA 记录解析回同一 IP（正向 DNS）；发件人显示名应仅用于标识发件人，不得包含主题或正文内容，也不得具有欺骗性。

参考：Google 帮助中心《Email sender guidelines》· support.google.com/mail/answer/81126

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/gmail-faq-07.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
