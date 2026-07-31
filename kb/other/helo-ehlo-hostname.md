---
title: "HELO/EHLO 主机名（RFC 5321 §4.1.1.1）有哪些合规要求？用 IP 字面量有何后果？"
source: "https://ztpop.net/kb/helo-ehlo-hostname.html"
license: CC-BY 4.0
---

# HELO/EHLO 主机名（RFC 5321 §4.1.1.1）有哪些合规要求？用 IP 字面量有何后果？

1
HELO/EHLO 主机名（RFC 5321 §4.1.1.1）有哪些合规要求？用 IP 字面量有何后果？
▼

**要求**

RFC 5321 §4.1.1.1 规定：HELO/EHLO 参数应为“发送方主机的完全合格域名（FQDN）”；若无 FQDN，可用地址字面量但必须用方括号包裹的 IP（如 [192.0.2.1]），且不得用裸 IP 或当地址。

**合规要点**

FQDN 应能正向解析回来源 IP（FCrDNS）；主机名不能是“无效/占位”域名；这些直接影响对方是否信任该连接。

**后果**

用裸 IP 作 HELO（如 HELO 192.0.2.1 无括号）或 HELO 与 PTR 不符，常被反垃圾策略扣分甚至拒收（4xx/5xx）；动态 IP 主机尤需配置正确 HELO。

**运维**

MTA 的 myhostname/HELO 名应设成与公网 PTR 一致的 FQDN；云主机默认 HELO 常是内部名，需显式修正。

参考：RFC 5321 §4.1.1.1（EHLO/HELO 参数语法与要求）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/helo-ehlo-hostname.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
