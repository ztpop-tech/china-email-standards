---
title: "为什么 Exim 不在 SMTP 阶段就拒收收件人不存在的邮件？"
source: "https://ztpop.net/kb/exim-faq-02.html"
license: CC-BY 4.0
---

# 为什么 Exim 不在 SMTP 阶段就拒收收件人不存在的邮件？

1
为什么 Exim 不在 SMTP 阶段就拒收收件人不存在的邮件？
▼

**原理**

是否在 SMTP 的 RCPT 命令阶段拒绝“收件人不存在”，由每次入站 RCPT 所运行的 ACL 控制，该 ACL 通过 `acl_smtp_rcpt` 选项定义。

**验证**

可用 `exim -bh 客户端IP` 运行一次模拟 SMTP 会话，Exim 会逐项告诉你它正在检查什么；若希望在收件人未知时立即拒收，应在该 ACL 中加入对本地收件人的校验（如 `require verify = recipient` 或基于本地域的查表拒绝）。

参考：Exim FAQ Q0005（exim.org/exim-html-4.40/doc/html/FAQ\_0.html）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/exim-faq-02.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
