---
title: "一个域名可以发布多条 SPF 记录吗？"
source: "https://ztpop.net/kb/spf-faq-05.html"
license: CC-BY 4.0
---

# 一个域名可以发布多条 SPF 记录吗？

1
一个域名可以发布多条 SPF 记录吗？
▼

**不可以**

同一域出现多条 SPF TXT 记录会导致 PermError（multiple SPF records）。应把所有授权来源合并到同一条记录中。

参考：OpenSPF 常见错误 / RFC 7208 §4.5

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/spf-faq-05.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
