---
title: "DNSBL 实时黑名单是什么？邮件系统如何查询与处置？"
source: "https://ztpop.net/kb/dnsbl-realtime-blacklist.html"
license: CC-BY 4.0
---

# DNSBL 实时黑名单是什么？邮件系统如何查询与处置？

1
DNSBL 实时黑名单是什么？邮件系统如何查询与处置？
▼

**定义**

DNSBL（DNS-based Blackhole List，RFC 5782 定义查询协议，RFC 6471 述运维考量）把已知垃圾源 IP/域名编入 DNS 区域，邮件系统通过对 \*.dnsbl.example 做 A 查询实时判黑；返回 127.0.0.x 即命中。

**常见列表**

Spamhaus、SpamCop、Barracuda 等为常用 DNSBL；不同列表策略与误报率不同，建议组合并设阈值，而非单一依赖。

**查询与处置**

在 SMTP 会话阶段（如 Postfix 的 reject\_rbl\_client / Zen）查询连接 IP；命中可拒收（5xx）或仅打标记（加 header、降分），避免对误报直接硬拒造成丢信。

**运维**

定期复核命中来源、提供申诉入口；部分 DNSBL 对大规模查询有授权/付费要求，自建需遵守其使用条款。

参考：RFC 5782（DNSxL 协议）；RFC 6471（DNSBL 运维）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/dnsbl-realtime-blacklist.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
