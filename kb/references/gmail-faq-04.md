---
title: "大批量发件人为何必须设置 DMARC？DMARC 记录如何工作？"
source: "https://ztpop.net/kb/gmail-faq-04.html"
license: CC-BY 4.0
---

# 大批量发件人为何必须设置 DMARC？DMARC 记录如何工作？

1
大批量发件人为何必须设置 DMARC？DMARC 记录如何工作？
▼

**说明**

DMARC 告诉接收服务器：对未通过 SPF/DKIM 的邮件该怎么处理。大批量发件人必须发布 DMARC 记录。要通过 DMARC 认证，邮件须经 SPF 或 DKIM（或两者）认证，且认证域名须与邮件 `From:` 头中的域名一致。Google 建议将 DMARC 策略设为 `quarantine` 或 `reject` 以获得最佳投递，并建议开启 DMARC 报告以监控发信。

参考：Google 帮助中心《Email sender guidelines》· support.google.com/mail/answer/81126

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/gmail-faq-04.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
