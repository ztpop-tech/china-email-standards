---
title: "SPF 记录最多 10 个 include，超了怎么办？"
source: "https://ztpop.net/kb/google-faq-04.html"
license: CC-BY 4.0
---

# SPF 记录最多 10 个 include，超了怎么办？

1
SPF 记录最多 10 个 include，超了怎么办？
▼

**说明**

SPF 的 DNS 查询链（include 展开）最多允许约 10 次查找，超出会导致校验超时或失败（permerror），反而让合法邮件认证失败。如果你通过很多第三方服务发信，单纯堆 include 会触顶。

**建议**

尽量合并发信通道：把各类自动邮件、营销邮件统一经一个出口（如出站网关/中继）发出，在 SPF 里只 include 该出口；或在不同子域上分别配置各自的 SPF 记录，避免单一主域记录过载。

参考：Google Workspace 帮助中心《Set up SPF》· support.google.com/a/answer/173534

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/google-faq-04.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
