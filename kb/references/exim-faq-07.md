---
title: "如何配置 Exim 仅在 SMTP 会话已加密（TLS）时才通告 SMTP 认证？"
source: "https://ztpop.net/kb/exim-faq-07.html"
license: CC-BY 4.0
---

# 如何配置 Exim 仅在 SMTP 会话已加密（TLS）时才通告 SMTP 认证？

1
如何配置 Exim 仅在 SMTP 会话已加密（TLS）时才通告 SMTP 认证？
▼

**配置**

使用如下设置即可：`auth_advertise_hosts = ${if eq{$tls_cipher}{}{}{*}}`。

**原理**

当会话未协商出 TLS 密码（`$tls_cipher` 为空）时，该展开结果为空，SMTP 认证不被通告；一旦 STARTTLS 成功、`$tls_cipher` 非空，则通告认证。这样可避免明文连接下暴露认证入口。

参考：Exim FAQ Q1702（exim.org/exim-html-4.40/doc/html/FAQ\_17.html）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/exim-faq-07.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
