---
title: "虚拟域邮件报“mail loops back to myself”怎么排查？"
source: "https://ztpop.net/kb/postfix-faq-03.html"
license: CC-BY 4.0
---

# 虚拟域邮件报“mail loops back to myself”怎么排查？

1
虚拟域邮件报“mail loops back to myself”怎么排查？
▼

**原因**

Postfix 认为该域由自己负责（出现在 mydestination 或某虚拟配置），但 DNS 的 MX 又指向本机，形成投递回路被拒绝。

**解决**

将虚拟域从 mydestination 中移除，只保留在 virtual\_mailbox\_domains；如确有单独后端，用 transport\_maps 把该域指到真实下一跳，避免自我循环。

参考：Postfix FAQ “Mail for unknown users in virtual domains fails with mail loops back to myself”

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/postfix-faq-03.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
