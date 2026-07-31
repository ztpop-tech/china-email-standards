---
title: "怎样限制用户只能发站内邮件、不能把邮件中继到外站？"
source: "https://ztpop.net/kb/postfix-faq-08.html"
license: CC-BY 4.0
---

# 怎样限制用户只能发站内邮件、不能把邮件中继到外站？

1
怎样限制用户只能发站内邮件、不能把邮件中继到外站？
▼

**方法**

在 smtpd\_relay\_restrictions（或 smtpd\_recipient\_restrictions）中组合：permit\_mynetworks、permit\_sasl\_authenticated、reject\_unauth\_destination；未通过认证的外发目标一律拒绝。

**要点**

reject\_unauth\_destination 是防止开放中继的核心，必须保留。

参考：Postfix FAQ “Restricting what users can send mail to off-site destinations”

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/postfix-faq-08.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
