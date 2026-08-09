---
title: "邮件系统引入第三方 AI 模型，供应链风险要评估哪些点？"
source: "https://ztpop.net/kb/ai-vendor-model-supply-chain-email.html"
license: CC-BY 4.0
---

# 邮件系统引入第三方 AI 模型，供应链风险要评估哪些点？

**先认清引入的到底是什么**

把邮件接给外部模型服务，本质上是**把组织最敏感的数据集合的读取权，授予了一个自己无法审计其内部行为的系统**。邮件里有合同、报价、人事、法务、凭据线索、客户名单——它的敏感度通常高于多数业务数据库。

因此评估的核心问题不是「模型效果好不好」，而是**「数据到哪里去了、谁能看到、出问题我能不能退出」**。CISA Artificial Intelligence 官方专题页 与 ENISA Artificial Intelligence and Cybersecurity Research 均把 AI 系统的供应链与数据边界列为需要专门关注的方向。

**维度一：数据流必须逐段画清楚**

要求供应方以书面形式回答，且答案要能对应到技术事实，而非营销表述：

* **哪些数据会离开本组织控制范围？**全文、摘要、元数据、附件、还是仅特征向量。
* **数据在何处处理与存储？**地域与法域，是否涉及跨境。
* **留存多久？如何删除？删除是否可验证？**
* **是否用于训练或改进模型？**默认值是什么，能否关闭，关闭后如何证明。
* **是否存在人工查看环节？**标注、质检、故障排查都可能引入人工接触。
* **是否存在下游第四方？**供应方自身可能也在调用别人的模型服务。

**判定条件：任何一项回答含糊或只有口头承诺，即视为不满足。**

**维度二：合同与责任条款**

技术评估之外，需要在协议层固定的内容：

* 数据用途限定、禁止再利用与转售的明确条款。
* 子处理方清单与变更通知义务。
* 安全事件通知时限与通知内容要求。
* 审计权或第三方审计报告的提供义务。
* **服务终止时的数据删除与证明**。
* 模型或服务发生重大变更时的通知与重新评估权。

**最容易被忽略的是最后一条。**模型版本更换可能显著改变行为与风险特征，若无通知义务，组织会在毫不知情的情况下运行在一个全新系统上。

**维度三：技术隔离与最小权限**

无论合同写得多好，技术侧都应假设外部服务可能出问题：

1. **最小数据面**：只传递完成任务必需的内容。摘要任务不需要传附件原文，分类任务往往不需要传全文。
2. **脱敏前置**：在数据离开前剥离或替换明显的敏感标识。
3. **权限单向**：外部服务只接收数据并返回结果，**不得反向持有对邮箱的访问凭据**。这是硬边界。
4. **输出不可直接触发动作**：外部返回的结果只能作为建议，副作用动作由本地系统按既定规则执行。
5. **分级豁免**：法务、人事、并购等高敏邮件类别默认不进入外部处理链路。

模型自身的风险类别可对照 OWASP Top 10 for Large Language Model Applications，攻击视角可对照 MITRE ATLAS™ (Adversarial Threat Landscape for AI Systems) 做覆盖度检查。

**维度四：可观测性——不能只看供应方的报表**

必须在**本地侧**留有独立记录，否则出事时只能听供应方一面之词：

* 每次调用的时间、数据量、数据类别、发起主体。
* 返回结果与本地最终动作的对应关系。
* 调用失败与超时的统计（**异常增长可能意味着服务侧发生了变更**）。
* 调用量的基线与异常波动告警。
* 涉及高敏类别邮件的调用单独审计。

**本地日志的留存期应独立设定，不依赖供应方的留存策略。**

**维度五：退出能力必须在接入前验证**

「能不能退出」不能等到要退出时才发现。接入前应确认并**实测**：

1. 能否一键关闭该 AI 能力，关闭后邮件系统**功能降级但不中断**。
2. 降级路径是否被定期验证仍然可用（长期不用的降级路径通常已经损坏）。
3. 是否存在对该供应方的硬性依赖（例如判定结果已被写死进投递决策链，无法绕过）。
4. 历史数据能否导出，格式是否可用。
5. 更换供应方的迁移成本是否已评估。

**判定条件：若关闭该能力会导致邮件无法正常收发，说明耦合过深，应先解耦再上线。**

**把评估结论纳入持续治理**

供应链评估不是一次性动作。应把上述五个维度的结论写入 AI 资产台账，并在**供应方变更、模型版本变更、权限范围变更、数据流变更**四种情况下强制复审。治理结构可直接沿用 NIST AI 100-1 Artificial Intelligence Risk Management Framework (AI RMF 1.0) 的 GOVERN 与 MANAGE 功能，避免为此另建一套管理流程。

参考：[CISA Artificial Intelligence 官方专题页](https://www.cisa.gov/ai) ｜ [ENISA Artificial Intelligence and Cybersecurity Research](https://www.enisa.europa.eu/publications/artificial-intelligence-and-cybersecurity-research) ｜ [OWASP Top 10 for Large Language Model Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/) ｜ [NIST AI 100-1 Artificial Intelligence Risk Management Framework (AI RMF 1.0)](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/ai-vendor-model-supply-chain-email.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
