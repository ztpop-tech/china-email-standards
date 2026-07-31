---
title: "DKIM 的 simple 与 relaxed 规范化（canonicalization，RFC 6376）有何区别？为何常用 relaxed？"
source: "https://ztpop.net/kb/dkim-body-canonicalization.html"
license: CC-BY 4.0
---

# DKIM 的 simple 与 relaxed 规范化（canonicalization，RFC 6376）有何区别？为何常用 relaxed？

1
DKIM 的 simple 与 relaxed 规范化（canonicalization，RFC 6376）有何区别？为何常用 relaxed？
▼

**定义**

规范化决定“哪些字节参与哈希”，header 与 body 各选 simple 或 relaxed（c=/），用于抵抗中转过程中无语义的改写。

**simple**

几乎原样保留（仅去尾随空白、折叠头），对改写极敏感——任一空白/换行变化都会使签名失效；安全性高但易误伤。

**relaxed**

更宽容——头字段名小写化、折叠空白压缩、续行合并；body 去尾随空白与多余空行。能容忍多数中转无害改写（如 MTA 重排头、去空行）。

**实践**

header 与 body 都常用 relaxed（c=relaxed/relaxed），在“抗篡改”与“抗误失效”间平衡；严格场景可对 header 用 simple。错误设置会导致合法邮件 DKIM 失效、损害送达。

参考：RFC 6376 §3.4（规范化算法 simple/relaxed）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/dkim-body-canonicalization.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
