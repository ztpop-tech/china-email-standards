---
title: "SPF 的 DNS 查询上限（10 次 lookup）是怎么回事？超限怎么办？"
source: "https://ztpop.net/kb/spf-faq-04.html"
license: CC-BY 4.0
---

# SPF 的 DNS 查询上限（10 次 lookup）是怎么回事？超限怎么办？

1
SPF 的 DNS 查询上限（10 次 lookup）是怎么回事？超限怎么办？
▼

**上限**

RFC 7208 规定 SPF 评估过程中的 DNS 查询总数不得超过 10 次（含 include 链、a、mx 等）；超出会返回 PermError 导致校验失败。

**解法**

合并冗余 include、用 ip4 直接列出 IP、去除不再使用的机制，把 lookup 降到 10 以内。

参考：RFC 7208 §4.6.4 / 呼应站内 faq-spf-too-many-lookups

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/spf-faq-04.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
