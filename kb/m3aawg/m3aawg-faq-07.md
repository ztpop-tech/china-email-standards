---
title: "接收方（邮箱服务商）应如何处理 DMARC 校验？DMARC 通过能否覆盖 SPF 失败？"
source: "https://ztpop.net/kb/m3aawg-faq-07.html"
license: CC-BY 4.0
---

# 接收方（邮箱服务商）应如何处理 DMARC 校验？DMARC 通过能否覆盖 SPF 失败？

1
接收方（邮箱服务商）应如何处理 DMARC 校验？DMARC 通过能否覆盖 SPF 失败？
▼

**基础动作**

接收方应对入站邮件执行 SPF、DKIM、DMARC 认证检查，并依结果指导接收与过滤决策；同时要**尊重已发布的 DMARC 策略**（尤其是 `p=reject`），策略覆盖应少而可解释、并在聚合报告的 policy override 中留痕。

**DMARC 通过覆盖 SPF 失败**

由于 DMARC 通过只需一次“对齐的”SPF 或 DKIM 通过，而 Return-Path（RFC5321.From）域常与邮件头 From（RFC5322.From）域不对齐，因此当 SPF 以 `-all` 结尾且校验未过时，产生的 SPF Fail 判定**不应在 DMARC 评估之前导致拒信**——唯一的例外是 SPF 记录为 `v=spf1 -all`（声明不允许任何使用）时，接收方/中转方可据此 preemptive 处理。此外接收方应发送 DMARC 聚合报告，并在最终判定中参考到达邮件所带的 ARC 头。

参考：M3AAWG《Email Authentication Recommended Best Practices》(2020-09)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/m3aawg-faq-07.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
