---
title: "在 Google Workspace 里如何设置 DMARC？"
source: "https://ztpop.net/kb/google-faq-05.html"
license: CC-BY 4.0
---

# 在 Google Workspace 里如何设置 DMARC？

1
在 Google Workspace 里如何设置 DMARC？
▼

**说明**

DMARC 通过在域名 DNS 添加 `_dmarc` TXT 记录实现，无需在 Google Admin console 里做任何操作。示例记录：`v=DMARC1; p=reject; rua=mailto:postmaster@example.com; pct=100; adkim=s; aspf=s`。`v` 与 `p` 标签必须排在最前，其余标签顺序任意。

**重要前置**

启用 DMARC 前必须先为域名开启 SPF 和/或 DKIM，且建议 SPF/DKIM 已稳定运行至少 48 小时再开 DMARC，否则来自你域名的邮件可能出现送达问题。首次使用建议先将策略 `p` 设为 `none` 监控，再逐步升到 quarantine / reject。

参考：Google Workspace 帮助中心《Set up DMARC》· support.google.com/a/answer/2466580

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/google-faq-05.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
