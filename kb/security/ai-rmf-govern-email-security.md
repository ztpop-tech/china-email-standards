---
title: "怎么用 NIST AI RMF 治理邮件系统里的 AI 组件？"
source: "https://ztpop.net/kb/ai-rmf-govern-email-security.html"
license: CC-BY 4.0
---

# 怎么用 NIST AI RMF 治理邮件系统里的 AI 组件？

**先理解 AI RMF 的定位：它管的是「组织怎么持续管理风险」**

NIST AI 100-1 Artificial Intelligence Risk Management Framework (AI RMF 1.0) 提供的是自愿采用的风险管理框架，核心是四个功能：GOVERN（治理）、MAP（识别情境与风险）、MEASURE（度量）、MANAGE（处置）。NIST Trustworthy & Responsible AI Resource Center：AI RMF Core 提供了这些功能的细分类目说明。

**常见误解是把它当成技术控制清单去逐条对照。**它更接近一套「怎么把 AI 风险纳入现有管理体系」的方法，产出物是职责、台账、指标和处置机制，而不是配置项。理解这一点，落地时才不会走偏。

**GOVERN：先把责任落到具体的人**

邮件场景下最容易缺失的就是这一项——AI 能力往往是随邮件平台一起进来的，没有单独的责任人。需要明确：

* **谁批准**在邮件系统中启用某项 AI 能力，批准的书面依据是什么。
* **谁承担**该能力误判造成的业务后果，以及谁有权紧急关闭它。
* **数据边界**：邮件内容是否离开本组织控制范围、是否用于模型训练、留存多久、如何删除。这一条必须书面化，不能停留在口头理解。
* **变更纪律**：模型版本、提示词、权限范围发生变更时，是否需要重新评审。

**判定条件：**如果问「谁能关掉邮件助手」而无人能立即回答，GOVERN 就没有建立。

**MAP：建立 AI 资产台账**

台账是后续一切工作的基础。每个 AI 组件至少记录：

* 组件名称与用途（判分 / 摘要 / 起草 / 检索 / 反馈学习）。
* **输入来源**：是否包含攻击者可控内容（邮件正文、附件、URL 内容、用户标记）。
* **持有权限**：可读什么、可写什么、可否外发、可调用哪些工具。
* **输出去向**：是否直接影响投递结果、是否直接呈现给用户、是否触发动作。
* 部署位置与数据流经路径，是否涉及外部服务。
* 失效影响：该组件不可用时业务是否中断，有无降级方案。

风险识别可结合 MITRE ATLAS™ (Adversarial Threat Landscape for AI Systems) 的攻击视角与 OWASP Top 10 for Large Language Model Applications 的应用风险清单交叉检查，避免只从「功能好不好用」的角度看问题。

**MEASURE：定义可采集的指标，而不是主观评价**

指标必须是系统能自动采出来的，否则不会长期存在。邮件场景可用的指标：

* 判分类：误判申诉量与解决时长、判定翻转次数、拦截量的异常波动。
* 助手类：工具调用次数与类型分布、被用户拒绝的建议动作数量、输出中出现外部 URL 或敏感字段的次数。
* 数据类：模型访问过的邮件条数、跨用户检索发生次数（正常应为零）。
* 可用性类：组件失效时长、降级触发次数。
* 反馈回路类：标记量的账号分布、异常高频标记账号数。

**每个指标都要预先定义阈值与响应动作**，否则采集了也只是报表。

**MANAGE：处置要接入既有体系，不要另建流程**

处置机制包含四件事，且都应复用现有能力：

1. **降级与关闭**：可快速退回无 AI 的处理路径，且该路径需定期验证仍然可用（长期不用的降级路径通常已经坏了）。
2. **回滚**：模型与提示词版本可回退，保留上一版本判定基线用于对比。
3. **事件响应**：AI 相关事件并入统一工单与值班体系，流程沿用 NIST SP 800-61 Rev.3 Incident Response Recommendations and Considerations，仅在证据清单中补充模型输入输出与工具调用记录。
4. **定期复审**：至少在每次架构变更、权限变更、供应商变更时复审台账与指标。

**不要让 AI 治理挤占基础建设**

一个实际的优先级提醒：**如果本域尚未完成发件人鉴别与传输加密的基础建设，那么它的优先级高于任何 AI 治理工作。**

NIST SP 800-177 Rev.1 Trustworthy Email 给出的可信邮件技术要求、CISA Binding Operational Directive 18-01 所要求的鉴别与加密收敛，属于确定性防护；AI 能力属于概率性增强。**地基未成时先装智能设备，是常见的资源错配。**

**最小起步方案**

若资源有限，按此顺序做前四件事即可产生实质效果：

1. 列出 AI 资产台账（一张表，半天可完成）。
2. 为每个组件写明权限清单与紧急关闭方式。
3. 确认邮件数据是否外流、是否用于训练，并书面化。
4. 为「跨用户检索」「助手外发」两项配置告警，这两项正常情况下不应发生。

参考：[NIST AI 100-1 Artificial Intelligence Risk Management Framework (AI RMF 1.0)](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf) ｜ [NIST Trustworthy & Responsible AI Resource Center：AI RMF Core](https://airc.nist.gov/AI_RMF_Knowledge_Base/AI_RMF) ｜ [OWASP Top 10 for Large Language Model Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/) ｜ [NIST SP 800-177 Rev.1 Trustworthy Email](https://csrc.nist.gov/pubs/sp/800/177/r1/final)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/ai-rmf-govern-email-security.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
