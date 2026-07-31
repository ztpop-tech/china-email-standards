---
title: "如何阅读邮件头中的 Received 链（Received chain）？"
source: "https://ztpop.net/kb/header-faq-01.html"
license: CC-BY 4.0
---

# 如何阅读邮件头中的 Received 链（Received chain）？

1
如何阅读邮件头中的 Received 链（Received chain）？
▼

**什么是 Received 链**

一封邮件每经过一个邮件服务器（MTA），接收方就会在邮件顶部\*\*前置\*\*一个 Received 头。因此邮件头里会出现多个 Received 头，越靠上（越新）的是离你最近的一跳，越靠下（越旧）的是最初发出的那一跳——链条自上而下是从收件端向发件端回溯。

**怎么读顺序**

从最上面的 Received 开始往下读：第一行通常是你公司/服务商的入站网关，最后一行是真正的发送源。分析钓鱼或 spoofing 时，重点看\*\*最底部\*\*的那一两个 Received——它们离原始发送者最近，伪造难度也最高。

**为何重要**

Received 链是追溯邮件真实路径、判断是否为伪造跳转的关键证据。配合 Authentication-Results、Received-SPF、Received-DKIM 等头，可以交叉验证“声称从哪里发”和“实际从哪里来”是否一致。

参考：RFC 5321（SMTP 传输与 Received 头约定）；邮件取证实务

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/header-faq-01.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
