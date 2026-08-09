---
title: "人机协同的邮件威胁研判流程该怎么设计？"
source: "https://ztpop.net/kb/ai-human-in-the-loop-triage.html"
license: CC-BY 4.0
---

# 人机协同的邮件威胁研判流程该怎么设计？

**先划清职责边界：机器做收敛，人做定性**

人机协同失败的典型原因是**职责边界没划清**——要么让模型直接下结论，人只是点确认；要么模型只输出一个分数，人还是得从头看一遍。两种都没有产生增益。

合理的划分是：

* **机器负责收敛与排序：**聚合同源事件、提取关键字段、还原时间线、按风险排队列、给出可比对的历史相似案例。这些是人做起来慢且易错的机械工作。
* **人负责定性与决策：**判断业务上下文是否合理、决定处置强度、承担误判后果。这些依赖机器不掌握的组织知识。

**一条硬规则：涉及资金、权限、账号状态变更的处置，最终动作必须由人触发。**

**分析员界面必须呈现的证据字段**

如果界面上只有「风险分 87」，分析员就只能选择相信或不信，协同不成立。界面必须呈现**可独立复核的原始事实**：

* 信封发件人与头部发件人（RFC 5321 Simple Mail Transfer Protocol MAIL FROM 与 RFC 5322 Internet Message Format From）及其是否一致。
* RFC 8601 Message Header Field for Indicating Message Authentication Status 的 Authentication-Results 原文，而不是简化后的「通过/不通过」。
* 若邮件经过转发或列表，RFC 8617 The Authenticated Received Chain (ARC) Protocol 的 ARC 链信息与 RFC 7960 Interoperability Issues between DMARC and Indirect Email Flows 所述的间接流场景说明。
* 发件域首次出现时间、历史通信计数、Reply-To 是否异域。
* URL 的完整跳转链与最终落地域名。
* 同批次投递的其他收件人清单。
* **模型给出该判定所依据的具体信号及其权重**，而非仅有总分。

**设计要求：每一项都可一键复制取证，且可直接跳转到原始日志。**

**防止自动化偏见：让分析员保有独立判断**

当模型准确率较高时，会出现**自动化偏见**——分析员逐渐停止独立思考，默认接受机器结论。这在长期是危险的，因为它恰好在攻击者成功绕过模型时失效。

可用的机制：

* **先呈现证据，后呈现结论。**界面默认折叠模型判定，展开证据；分析员可主动查看模型意见。这一个小改动对维持独立判断很有效。
* **定期插入盲样复核**：在队列中混入已知结论的样本，观察分析员是否仍在实质研判。
* **要求填写「不同意理由」但不要求填写「同意理由」**，同时统计同意率；**同意率过高本身是需要关注的信号**。

**反过来也要防止告警疲劳**

另一端的失败模式是告警太多、分析员批量点掉。缓解方式不是降低灵敏度，而是**改变呈现粒度**：

* 按活动聚合：同一发件域、同一模板、同一落地页的邮件合并为一个事件，一次处置全批生效。
* 队列按「可行动性」排序，而不是只按分数——能立即采取动作的排前面。
* 把明确的低价值告警（已被拦截且无人点击的批量垃圾邮件）移出人工队列，只做统计。
* 为重复出现的处置模式提供一键剧本，减少机械操作。

**闭环：处置结论必须回流**

协同流程若不闭环，模型无法改进，分析员也在重复劳动。回流应包含：分析员的最终定性、依据的关键字段、处置动作、事后是否发生实际损害。

同时要防止回流通道被污染：**回流数据须记录操作人与时间，模型更新前对样本抽样审核，并保留回滚能力**。这一点与判分模型的反馈回路治理是同一套要求。

**度量：看什么指标才有意义**

不要只看「拦截了多少封」。有意义的指标是：

* 从投递到定性的中位时长（研判效率）。
* 误判申诉量及其解决时长（业务影响）。
* 分析员对模型结论的不同意率及其趋势（独立判断是否还在）。
* 同源事件的聚合率（收敛能力是否有效）。
* 事后追认为漏判的数量与发现渠道（防线真实缺口）。

整体治理可挂到 NIST AI 100-1 Artificial Intelligence Risk Management Framework (AI RMF 1.0) 的 MEASURE 环节，事件处置沿用 NIST SP 800-61 Rev.3 Incident Response Recommendations and Considerations 的流程框架，不另起炉灶。

参考：[NIST AI 100-1 Artificial Intelligence Risk Management Framework (AI RMF 1.0)](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf) ｜ [NIST SP 800-61 Rev.3 Incident Response Recommendations and Considerations](https://csrc.nist.gov/pubs/sp/800/61/r3/final) ｜ [RFC 8601 Message Header Field for Indicating Message Authentication Status](https://www.rfc-editor.org/rfc/rfc8601.html) ｜ [RFC 8617 The Authenticated Received Chain (ARC) Protocol](https://www.rfc-editor.org/rfc/rfc8617.html)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/ai-human-in-the-loop-triage.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
