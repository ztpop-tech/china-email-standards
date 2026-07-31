---
title: "为什么应校验 HELO/EHLO 主机名？它能挡住哪些垃圾与伪造？"
source: "https://ztpop.net/kb/email-helo-validation.html"
license: CC-BY 4.0
---

# 为什么应校验 HELO/EHLO 主机名？它能挡住哪些垃圾与伪造？

1
为什么应校验 HELO/EHLO 主机名？它能挡住哪些垃圾与伪造？
▼

**背景**

SMTP 握手时客户端先发 HELO/EHLO ；合规发送方应报“真实可解析的 FQDN”，而大量僵尸/垃圾源报 IP、报别人域名或非法名。

**校验项**

① HELO 名应为合法 FQDN（非裸 IP、非空）；② 可反向解析（FCrDNS）与 PTR 一致；③ 不应冒充本域/知名域名。不符可拒绝或加信誉惩罚。

**价值**

廉价前置过滤：多数合法 MTA 都满足，而大量垃圾源不满足，能在“进入内容扫描前”就挡掉一批。

**风险**

过度严格会误杀（部分合法老旧系统 HELO 不规范）；建议“软失败+记分”而非硬拒，配合其余信誉信号。

参考：RFC 5321 §4.1.1.1（HELO/EHLO）；FCrDNS 实践（RFC 1912/施志）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-helo-validation.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
