---
title: "SPF 记录怎么写？基本语法是什么？"
source: "https://ztpop.net/kb/spf-faq-02.html"
license: CC-BY 4.0
---

# SPF 记录怎么写？基本语法是什么？

1
SPF 记录怎么写？基本语法是什么？
▼

**语法**

以 “v=spf1” 开头，后接机制（ip4、ip6、include、a、mx、exists 等）与限定符（+ 通过 / - 硬失败 / ~ 软失败 / ? 中立），末尾以 all 收尾。

参考：RFC 7208 §4（SPF 记录格式）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/spf-faq-02.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
