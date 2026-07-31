---
title: "Postfix 拒收邮件并提示“User unknown in local recipient table”，是什么原因、怎么解决？"
source: "https://ztpop.net/kb/postfix-faq-01.html"
license: CC-BY 4.0
---

# Postfix 拒收邮件并提示“User unknown in local recipient table”，是什么原因、怎么解决？

1
Postfix 拒收邮件并提示“User unknown in local recipient table”，是什么原因、怎么解决？
▼

**原因**

Postfix 用 local(8) 投递时，会在本地账户库（/etc/passwd、aliases.db）查找收件人；若收件人既非本地用户、又无对应别名，便以该错误拒收。

**解决**

确认收件人账户确实存在；若需别名转发，在 aliases 中配置并执行 newaliases 重建；若该域应走虚拟投递，把它加入 virtual\_mailbox\_domains 并在 virtual\_mailbox\_maps 注册收件人。

参考：Postfix FAQ “Postfix rejects mail with User unknown in local recipient table” (postfix.org/faq.html)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/postfix-faq-01.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
