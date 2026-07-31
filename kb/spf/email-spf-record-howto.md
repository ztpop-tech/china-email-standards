---
title: "如何“写一条正确的 SPF 记录”？常见错误有哪些？"
source: "https://ztpop.net/kb/email-spf-record-howto.html"
license: CC-BY 4.0
---

# 如何“写一条正确的 SPF 记录”？常见错误有哪些？

1
如何“写一条正确的 SPF 记录”？常见错误有哪些？
▼

**结构**

在发信域的 DNS 加一条 TXT：v=spf1 <授权机制> all；机制如 ip4:、include:<服务商域>、a、mx，末位 -all（硬失败）或 ~all（软失败）。

**原则**

只列“确实代你发信”的来源；末位用 -all 最严（不符即拒），~all 为过渡；未授权源不要列。

**常见错**

① 多条 v=spf1 冲突（应合并为一条）；② include 链超 10 次查询（见扁平化篇）；③ 忘了新接入的 ESP 导致合法信被拒；④ 用 +all 等于全放行（危险）。

**实践**

上线前用 SPF 校验工具测；与 DKIM/DMARC 配合；改 DNS 后等 TTL 生效再观察 DMARC 报告验证对齐。

参考：RFC 7208（SPF 语法与机制）；SPF 记录最佳实践

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-spf-record-howto.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
