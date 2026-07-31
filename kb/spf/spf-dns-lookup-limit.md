---
title: "SPF 的 DNS 查询上限（10 次）是什么意思？include 嵌套过深会怎样？"
source: "https://ztpop.net/kb/spf-dns-lookup-limit.html"
license: CC-BY 4.0
---

# SPF 的 DNS 查询上限（10 次）是什么意思？include 嵌套过深会怎样？

1
SPF 的 DNS 查询上限（10 次）是什么意思？include 嵌套过深会怎样？
▼

**上限来源**

RFC 7208 §4.6.4 规定评估一个域的 SPF 时，DNS 查询总数不得超过 10 次（含初始，以及每次 include / a / mx / exists / redirect）。超出即 PermError，通常导致结果 none（不生效）。

**常见陷阱**

多层 include（如 include:spf1 各又 include 多个）迅速累计；每含一个 a / mx 算一次查询；宏（macros）不额外计次。

**后果**

超限会让合法邮件 SPF 失败 → DMARC 对齐失败 → 可能被拒或进垃圾箱，且难以排查（仅 PermError 日志）。

**优化**

合并为少量扁平 include、用 ip4 / ip6 直列、避免冗余；大型代发平台应提供单一充分 include。可用 SPF 校验工具预先数查询次数。

参考：RFC 7208 §4.6.4（DNS 查询上限）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/spf-dns-lookup-limit.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
