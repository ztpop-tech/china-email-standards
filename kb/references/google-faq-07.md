---
title: "DMARC 的 pct 标签（抽样比例）如何帮助渐进部署？"
source: "https://ztpop.net/kb/google-faq-07.html"
license: CC-BY 4.0
---

# DMARC 的 pct 标签（抽样比例）如何帮助渐进部署？

1
DMARC 的 pct 标签（抽样比例）如何帮助渐进部署？
▼

**说明**

`pct` 指定有多少比例的未认证邮件受 DMARC 策略约束，取值范围 1–100（整数）。渐进部署 DMARC 时，可以先设一个较小比例，随着来自你域名的合法邮件在接收方通过认证的比例提升，再把 pct 调高，直到 100%。若记录里不带 pct，则策略默认作用于 100% 邮件。

**注意**

若你的域名使用 BIMI（品牌标识邮件识别），DMARC 的 `p` 必须为 quarantine 或 reject，且 `pct` 必须为 100——BIMI 不支持 p=none 或 pct<100 的策略。

参考：Google Workspace 帮助中心《Set up DMARC》· support.google.com/a/answer/2466580

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/google-faq-07.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
