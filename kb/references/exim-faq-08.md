---
title: "如何在 Exim 中显式拒收一组指定域名（并给出自定义错误）？"
source: "https://ztpop.net/kb/exim-faq-08.html"
license: CC-BY 4.0
---

# 如何在 Exim 中显式拒收一组指定域名（并给出自定义错误）？

1
如何在 Exim 中显式拒收一组指定域名（并给出自定义错误）？
▼

**配置**

在配置第一段定义命名域列表：`domainlist reject_domains = list:of:domains:to:reject`。然后在 ACL 中拒绝这些域的 SMTP 收件人，并可附自定义报错。

**命令行提交**

若也要拒绝非 SMTP（命令行提交）的此类域邮件，可加一个 redirect 路由器：`reject_domains: driver=redirect domains=+reject_domains allow_fail data=:fail: The domain $domain is no longer supported`。

参考：Exim FAQ Q0202（exim.org/exim-html-4.40/doc/html/FAQ\_2.html）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/exim-faq-08.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
