---
title: "子域（如 sub.example.com）需要单独设置 SPF 吗？"
source: "https://ztpop.net/kb/spf-faq-08.html"
license: CC-BY 4.0
---

# 子域（如 sub.example.com）需要单独设置 SPF 吗？

1
子域（如 sub.example.com）需要单独设置 SPF 吗？
▼

**建议**

若子域独立发信，应为其单独配置 SPF；若仅主域发信，可依赖主域 SPF，或在 DMARC 中用 sp 标签覆盖子域策略。

参考：RFC 7208 §4.5 / 呼应站内 operational-mistakes-13

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/spf-faq-08.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
