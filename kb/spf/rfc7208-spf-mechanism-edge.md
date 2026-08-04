---
title: "SPF（RFC 7208）的机制与边界案例有哪些？"
source: "https://ztpop.net/kb/rfc7208-spf-mechanism-edge.html"
license: CC-BY 4.0
---

# SPF（RFC 7208）的机制与边界案例有哪些？

1
SPF（RFC 7208）的机制与边界案例有哪些？
▼

**限定符与默认值**

RFC 7208 §4.6.2 规定机制前的限定符决定 `check_host()` 返回值：`+` 为 pass、`-` 为 fail、`~` 为 softfail、`?` 为 neutral；限定符可省略，**默认值为 `+`**（即未写限定符匹配即 pass）。

**机制详解**

§5 定义各机制：`all` 始终匹配，其后机制被忽略且存在 `all` 时 `redirect` 被忽略；`include` 触发对 `check_host()` 的递归评估；`a`/`mx` 按 A/AAAA 与 MX 地址匹配（**无 MX 记录时不回退查 A/AAAA**）；`ptr` 因慢且不可靠被标注“SHOULD NOT 发布”；`ip4`/`ip6` 省略 CIDR 时默认 `/32` 与 `/128`；`exists` 只要查到任何 A 记录即匹配。

**DNS 查询上限与 void lookups**

§4.6.4 是关键边界：实现**必须把 include/a/mx/ptr/exists 与 redirect 引发的总 DNS 查询限制在 10 次**，超出返回 `permerror`；每个 `mx` 至多查 10 个地址记录，超出同样 `permerror`。此外“void lookups”（返回空 answer 或 Name Error 的查询）**默认限制为 2**，超出亦为 `permerror`。评估耗时建议上限约 20 秒，超时返回 `temperror`。

**转发边界与修饰符**

§10.3 指出：SPF 基于“最后一跳发送服务器”的 IP 评估，转发中介若不重写信封 `MAIL FROM`，原域 SPF 记录会使新发送 IP 评估为 fail——这是邮件列表/转发合法丢信的主因，通常用 SRS 重写信封缓解。`redirect=`（§6.1）在全部机制不匹配时以扩展域重查，且记录中不可出现两次；`exp=`（§6.2）仅当结果为 fail 时计算解释串。

参考：RFC 7208（Sender Policy Framework），https://www.rfc-editor.org/rfc/rfc7208 —— 章节 4.6.2 / 5.1–5.7 / 4.6.4 / 6.1 / 6.2 / 10.3

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/rfc7208-spf-mechanism-edge.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
