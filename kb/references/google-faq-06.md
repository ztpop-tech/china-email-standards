---
title: "DMARC 的严格对齐（adkim=s / aspf=s）与宽松对齐有什么区别？"
source: "https://ztpop.net/kb/google-faq-06.html"
license: CC-BY 4.0
---

# DMARC 的严格对齐（adkim=s / aspf=s）与宽松对齐有什么区别？

1
DMARC 的严格对齐（adkim=s / aspf=s）与宽松对齐有什么区别？
▼

**说明**

对齐（alignment）指邮件 `From:` 头域名与 SPF 信封域或 DKIM `d=` 域的匹配程度。严格（`s`）要求两者完全相等；宽松（`r`，默认）允许子域匹配。DMARC 通过 SPF 或 DKIM 任一通过"认证 + 对齐"即可放行。

**建议**

当你的邮件由不受控的子域、或由他方管理的子域发出时，Google 建议改为严格对齐以加强防冒名。但注意：严格对齐可能使关联子域发来的合法邮件被拒或进垃圾箱，需评估后再改。

参考：Google Workspace 帮助中心《Set up DMARC》· support.google.com/a/answer/2466580

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/google-faq-06.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
