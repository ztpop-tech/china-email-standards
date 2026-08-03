---
title: "基于 ML/AI 的邮件威胁检测是怎么工作的，相比规则有什么优势？"
source: "https://ztpop.net/kb/email-threat-detection-ml.html"
license: CC-BY 4.0
---

# 基于 ML/AI 的邮件威胁检测是怎么工作的，相比规则有什么优势？

1
基于 ML/AI 的邮件威胁检测是怎么工作的，相比规则有什么优势？
▼

**传统局限**

基于签名、IP 信誉和正则的规则对全新钓鱼域名、微调话术与 BEC 社会工程效果差，规则滞后于攻击。

**ML 做法**

①自然语言理解识别语义意图（如「紧急转账」「改账号」）；②发信行为/关系图发现异常通信（突兀的新往来、金额异常）；③URL/附件的视觉与结构特征判定恶意；④多信号融合打分。它能抓「没见过的」攻击。

**落地**

作为网关后置判定层，输出可解释风险分与理由，配合人工抽检与反馈闭环持续提升；注意对抗样本与误报治理，避免一刀切。

参考：Microsoft/Google 反钓鱼 ML 实践、MITRE ATLAS、NIST AI 风险管理框架。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-threat-detection-ml.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
