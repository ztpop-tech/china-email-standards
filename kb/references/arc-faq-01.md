---
title: "什么是 ARC（Authenticated Received Chain）？它解决什么邮件认证问题？"
source: "https://ztpop.net/kb/arc-faq-01.html"
license: CC-BY 4.0
---

# 什么是 ARC（Authenticated Received Chain）？它解决什么邮件认证问题？

1
什么是 ARC（Authenticated Received Chain）？它解决什么邮件认证问题？
▼

**定义**

ARC（Authenticated Received Chain，RFC 8617）是一套邮件头机制，用于在邮件经邮件列表、转发服务等“中介”转发时，跨多跳保留原有的身份认证结果。

**解决的问题**

邮件列表、自动转发等合法中介会修改邮件（改标题、加页脚、重封装），导致 SPF/DKIM 对齐被破坏，进而使原本合法的邮件被 DMARC 误判为失败而丢弃。ARC 让接收方知道“这封邮件在更早的可信跳上确实通过过认证”，从而避免因合法修改而误杀。

参考：RFC 8617（Authenticated Received Chain）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/arc-faq-01.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
