---
title: "邮件头里的 Received 链条有什么用？如何用它溯源？"
source: "https://ztpop.net/kb/mailops-faq-06.html"
license: CC-BY 4.0
---

# 邮件头里的 Received 链条有什么用？如何用它溯源？

1
邮件头里的 Received 链条有什么用？如何用它溯源？
▼

**作用**

每经过一个 MTA，都会在邮件顶部追加一行 `Received:` 头，记录跳点时间、主机、IP 与 SMTP 标识。从下往上读，就是邮件从发件人到收件人的完整路径。

**溯源**

排查伪造/钓鱼时，核对 Received 中的真实连接 IP、HELO 名与认证结果（Authentication-Results），可判断邮件实际来自何处、是否在途被篡改。注意 Received 头可被发件方伪造首行，应以最接近收件人的受信任跳为准。

参考：RFC 5321（Received 头规范）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/mailops-faq-06.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
