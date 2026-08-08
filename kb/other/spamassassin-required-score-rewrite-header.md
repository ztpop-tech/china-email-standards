---
title: "SpamAssassin 的 required_score 与 rewrite_header 如何配置？"
source: "https://ztpop.net/kb/spamassassin-required-score-rewrite-header.html"
license: CC-BY 4.0
---

# SpamAssassin 的 required_score 与 rewrite_header 如何配置？

1
SpamAssassin 的 required\_score 与 rewrite\_header 如何配置？
▼

**required\_score 阈值**

默认 5.0。一封邮件各规则命中的分数累加（如 BAYES\_99、HTML\_FONT\_LOW\_CONTRAST 等带正负分），总分 ≥ required\_score 即判为垃圾。可按环境调高（更宽松、少误杀）或调低（更严格），写在 local.cf 或用户 user\_prefs 中。

**rewrite\_header 标头改写**

例如 rewrite\_header Subject \*\*\*\*\*SPAM\*\*\*\*\* 会在被判垃圾的邮件主题前加标记。还可用 add\_header / remove\_header 控制注入的 X-Spam-\* 标头（如 X-Spam-Status、X-Spam-Level、X-Spam-Flag）。report\_safe 控制是否把原始邮件作为附件封装。

**注意**

阈值与规则集由官方 sa-update 持续更新；自定义调参应放进 local.cf，不要改动被 sa-update 管理的规则文件，以免更新时被覆盖。

参考：Apache SpamAssassin 官方文档（Conf：required\_score / rewrite\_header）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/spamassassin-required-score-rewrite-header.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
