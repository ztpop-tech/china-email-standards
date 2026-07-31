---
title: "Sieve 的“正则表达式（regex）扩展”能做什么？用正则过滤要注意什么？"
source: "https://ztpop.net/kb/email-sieve-regex.html"
license: CC-BY 4.0
---

# Sieve 的“正则表达式（regex）扩展”能做什么？用正则过滤要注意什么？

1
Sieve 的“正则表达式（regex）扩展”能做什么？用正则过滤要注意什么？
▼

**能力**

regex 扩展让 Sieve 用正则表达式匹配信头/信体（如按“特定模式发件域、主题关键词组合”分流），比单字符串匹配更灵活。

**风险**

复杂正则开销大、易 ReDoS（灾难性回溯）拖垮服务器；且正则对“编码/换行/多语言”敏感，易漏配。

**建议**

优先用内置测试（address/header :contains 等）能满足就别上正则；确需时用“锚定、限长、避免嵌套量词”的稳妥写法，并限资源。

**实践**

邮件系统若开 Sieve regex，应在沙箱限制 CPU/步数，防止单条规则拖垮整队列；用户写规则时给示例与告警。

参考：Sieve 正则扩展（RFC 5228 体系；regex 扩展草案）；ReDoS 防护

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-sieve-regex.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
