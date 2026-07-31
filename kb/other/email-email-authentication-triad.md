---
title: "SPF、DKIM、DMARC 三者是什么关系？各自解决什么、又有哪些“管不了”的？"
source: "https://ztpop.net/kb/email-email-authentication-triad.html"
license: CC-BY 4.0
---

# SPF、DKIM、DMARC 三者是什么关系？各自解决什么、又有哪些“管不了”的？

1
SPF、DKIM、DMARC 三者是什么关系？各自解决什么、又有哪些“管不了”的？
▼

**分工**

SPF 验证“发信服务器 IP 是否授权”；DKIM 验证“信体/头未被改且来自持有私钥方”；DMARC 把二者与“信头 From”对齐，并规定“不对齐时怎么办”。

**互补**

SPF 不防转发改 Mail From（空发件人场景弱）；DKIM 不绑 From 域（第三方签名需 ATPS）；DMARC 依赖前两者提供“对齐裁决”，三者合起来抑显示层冒用。

**管不了**

三者主要治“域冒用/伪造”，对“账号被盗后合法签名发垃圾”“相似域名注册”无能为力，需配合 BEC 防御与用户意识。

**实践**

三者是“现代邮件可信”基石：先 SPF+DKIM 各司其职，再用 DMARC 对齐收紧；任一缺失都让 DMARC 失效。

参考：RFC 7208 / RFC 6376 / RFC 7489（三者关系）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-email-authentication-triad.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
