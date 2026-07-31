---
title: "外发邮件持续超时或连接丢失（timeout / lost connection），怎么处理？"
source: "https://ztpop.net/kb/postfix-faq-05.html"
license: CC-BY 4.0
---

# 外发邮件持续超时或连接丢失（timeout / lost connection），怎么处理？

1
外发邮件持续超时或连接丢失（timeout / lost connection），怎么处理？
▼

**原因**

通常是对端不可达、网络中断，或 SMTP 超时阈值设置过短导致连接被断。

**解决**

先确认 DNS 能解析对端 MX 且网络可达；适当调大 smtp\_helo\_timeout、smtp\_timeout 等参数；仍失败则联系对端管理员。

参考：Postfix FAQ “Mail fails consistently with timeout or lost connection”

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/postfix-faq-05.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
