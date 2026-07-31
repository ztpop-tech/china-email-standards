---
title: "SpamAssassin 的“评分机制”如何判定一封信是不是垃圾？阈值与规则怎么调？"
source: "https://ztpop.net/kb/email-spam-score-spamassassin.html"
license: CC-BY 4.0
---

# SpamAssassin 的“评分机制”如何判定一封信是不是垃圾？阈值与规则怎么调？

1
SpamAssassin 的“评分机制”如何判定一封信是不是垃圾？阈值与规则怎么调？
▼

**打分模型**

SpamAssassin 对每封信跑数百条规则，每条命中加分/减分（如“中文标题乱码 +1.5”“来自已知垃圾网段 +3”），累计得分与阈值比较。

**阈值**

默认阈值约 5.0：低于=正常、达到=标记为垃圾（加 X-Spam 头/改主题）、远高于=可直接拒。可因域/用户微调灵敏度。

**规则类型**

① 头/信体文本规则；② 网络测试（查 DNSBL/RBL、Pyzor、Razor 等信誉库）；③ 贝叶斯统计（见“贝叶斯过滤”篇）。多信号融合降低误判。

**实践**

邮件网关挂 SpamAssassin 做“打分+标记”，再由用户/过滤器按分数处置；调阈值要平衡“漏放”与“误杀”，并定期更新规则与 Bayes 库。

参考：SpamAssassin 文档（评分/规则/网络测试）；RFC 展 垃圾分类思路

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-spam-score-spamassassin.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
