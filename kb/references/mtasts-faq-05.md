---
title: "MTA-STS 策略文件中的 mx 与 max_age 字段有何含义？"
source: "https://ztpop.net/kb/mtasts-faq-05.html"
license: CC-BY 4.0
---

# MTA-STS 策略文件中的 mx 与 max_age 字段有何含义？

1
MTA-STS 策略文件中的 mx 与 max\_age 字段有何含义？
▼

**mx**

列出本域允许接收邮件的 MX 主机名（可含通配，如 `mx: *.mx.cloudflare.net`）。发送方只应向这些 MX 发起 TLS 投递。

**max\_age**

指定发送方可以缓存该策略的最长秒数（如 `max_age: 86400`）。缓存期内发送方持续按策略强制 TLS，无需每次重新获取。

参考：Cloudflare 策略示例（version: STSv1 / mode: enforce / mx / max\_age）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/mtasts-faq-05.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
