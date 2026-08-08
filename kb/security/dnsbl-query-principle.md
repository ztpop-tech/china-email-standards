---
title: "DNSBL 黑名单是怎么通过一次 DNS 查询判定的？"
source: "https://ztpop.net/kb/dnsbl-query-principle.html"
license: CC-BY 4.0
---

# DNSBL 黑名单是怎么通过一次 DNS 查询判定的？

1
DNSBL 黑名单是怎么通过一次 DNS 查询判定的？
▼

DNSBL（RFC 5782 称 DNSxL，DNS-based black/white list）是最早也是最轻量的**实时信誉拦截**机制之一。

#### 一、查询怎么构造

把待查 IPv4 地址**四段反转**后拼到名单 zone 前。例如查 `198.51.100.7` 在 `dnsbl.example` 上，发查询 `7.100.51.198.dnsbl.example`。

#### 二、返回值的约定

RFC 5782 规定返回地址必须落在 `127.0.0.0/8` 保留段内：若命中黑名单，返回如 `127.0.0.2`；不同末位字节可区分**列入原因类别**（如开放中继、直邮、劫持）。查询无结果（NXDOMAIN）即表示未列入。

#### 三、使用边界

DNSBL 是**异步、低开销的实时信号**，适合在 SMTP 会话中即时拒绝；但它只反映名单运营方的口径，存在误杀与滞后，生产环境应作为**多信号之一**而非唯一依据，并注意选择维护良好、规则透明的名单。

参考：https://www.rfc-editor.org/rfc/rfc5782

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/dnsbl-query-principle.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
