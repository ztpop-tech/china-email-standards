---
title: "为什么需要 TLS-RPT？没有它会有什么隐患？"
source: "https://ztpop.net/kb/tlsrpt-faq-08.html"
license: CC-BY 4.0
---

# 为什么需要 TLS-RPT？没有它会有什么隐患？

1
为什么需要 TLS-RPT？没有它会有什么隐患？
▼

**可见性缺口**

在 MTA-STS enforce 或 DANE 下，TLS 失败会被直接阻断。若没有 TLS-RPT，你只能看到“邮件发不出去”，却分不清是自己对端配置错误、证书过期，还是遭到了主动降级/中间人攻击。

**价值**

TLS-RPT 把不可见的失败变成可量化、可定位的报告，既是上线前的“安全网”（先 testing 观察），也是运行中的“雷达”（发现攻击迹象与配置漂移），是邮件 TLS 治理的必备一环。

参考：RFC 8460（motivation / operational use）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/tlsrpt-faq-08.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
