---
title: "反向 DNS（PTR）记录为何影响外发邮件送达？什么是 FCrDNS？"
source: "https://ztpop.net/kb/dnsmail-faq-02.html"
license: CC-BY 4.0
---

# 反向 DNS（PTR）记录为何影响外发邮件送达？什么是 FCrDNS？

1
反向 DNS（PTR）记录为何影响外发邮件送达？什么是 FCrDNS？
▼

**PTR 与正向解析**

正向 DNS 把域名解析成 IP；反向 DNS（PTR）把 IP 解析回域名（在 .in-addr.arpa / .ip6.arpa 下）。对外发送邮件的服务器，其出网 IP 应有 PTR 记录，且许多接收方会做 FCrDNS 校验。

**FCrDNS（正向确认反向 DNS）**

FCrDNS 指“用 PTR 得到的域名，再正向解析回来能得到原 IP”形成闭环。接收方常把 FCrDNS 通过作为发件主机可信的信号之一，未通过的主机更容易被标记或拒收。

**运维要点**

PTR 通常由承载 IP 的运营商/云厂商管理，需向其申请设置；PTR 主机名应与 HELO/EHLO 声明的名字一致，并能被正向解析回该 IP。

参考：RFC 1912（PTR 实践）；RFC 5321（HELO/EHLO 与可达性）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/dnsmail-faq-02.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
