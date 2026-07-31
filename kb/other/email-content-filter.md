---
title: "邮件内容过滤与垃圾评分（spam score）是如何运作的？"
source: "https://ztpop.net/kb/email-content-filter.html"
license: CC-BY 4.0
---

# 邮件内容过滤与垃圾评分（spam score）是如何运作的？

1
邮件内容过滤与垃圾评分（spam score）是如何运作的？
▼

**评分模型**

内容过滤器（如 SpamAssassin）对邮件逐条规则打分：命中规则加分，低于阈值放行、高于则标记/隔离/拒收。规则涵盖信头异常、可疑 URL、诱饵文本、附件类型、HTML 结构等。

**规则类型**

头规则（缺失 SPF/DKIM、伪造 From）、体规则（中奖/发票诈骗话术、混淆字符）、网络规则（RBL 命中、可疑发信 IP）、贝叶斯评分。各规则有权重，加权得到总分 spam score。

**处置**

按分数分级：低分静默放行、中分加 X-Spam 头/进 junk、高分拒收(5xx)或隔离待审。RFC 2505 建议以内容过滤+黑白名单+发信认证组合防御，而非单一手段。

**调优**

维护本地白名单（伙伴域）避免误杀；定期更新规则集与贝叶斯库；对误报/漏报样本回填训练。过严误伤、过松漏过，需结合信誉数据动态平衡。

参考：RFC 2505（反垃圾邮件建议）；SpamAssassin 评分实践

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-content-filter.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
