---
title: "MX 记录如何决定入站邮件路由？优先级数值怎么算？"
source: "https://ztpop.net/kb/dnsmail-faq-01.html"
license: CC-BY 4.0
---

# MX 记录如何决定入站邮件路由？优先级数值怎么算？

1
MX 记录如何决定入站邮件路由？优先级数值怎么算？
▼

**MX 的作用**

MX（Mail Exchanger）记录告诉全世界“哪个（些）邮件服务器负责接收某个域名的邮件”。发件方 SMTP 在投递前查询收件域的 MX 记录，得到一组目标主机。

**优先级**

每条 MX 记录带一个整数优先级（preference）。数值越小越优先：发件方先尝试优先级最低（最优先）的服务器，若该服务器不可达，再按优先级递增依次尝试下一个。多个相同优先级的 MX 之间由发送方自行抉择（通常轮询）。

**必须指向主机名**

MX 记录的值必须是主机名（A/AAAA 记录对应的名字），按 RFC 5321 不能直接是 IP 地址；解析 MX 得到主机名后，再解析其 A/AAAA 得到 IP 才能建立连接。

参考：RFC 1035（DNS）；RFC 5321（SMTP 传输，MX）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/dnsmail-faq-01.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
