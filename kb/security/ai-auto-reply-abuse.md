---
title: "AI 自动回复和自动摘要功能会被怎样滥用？该如何治理？"
source: "https://ztpop.net/kb/ai-auto-reply-abuse.html"
license: CC-BY 4.0
---

# AI 自动回复和自动摘要功能会被怎样滥用？该如何治理？

**风险来源：自动回复是「无人值守的对外输出通道」**

自动回复与传统外出自动应答的本质区别在于：传统应答返回一段固定文本，**内容与来信无关**；而模型驱动的自动回复会**依据来信内容生成响应**，这意味着外部输入可以影响对外输出。

一旦成立，攻击者就获得了一个可反复查询的接口：他发什么，就能影响组织自动回什么。这是所有滥用方式的共同基础。

**滥用方式一：信息探测**

攻击者用一系列精心构造的来信探测组织内部信息。可能被套取的内容包括：在职状态与休假安排、组织架构与汇报关系、项目名称与进度、内部系统名称、联系人邮箱格式规律、审批流程细节。

这些信息单看都不敏感，**汇总后却构成高质量的攻击前置情报**——尤其是「谁在休假」加「谁代为审批」，正是商务邮件欺诈选择时机与目标的关键输入。

**控制措施：**自动回复的输出内容**必须来自受控模板与白名单字段**，不得由模型自由生成涉及人员状态、组织结构、项目信息的表述。可以说「已收到，将尽快回复」，不应说「张某休假至某日，由李某代理该项目审批」。

**滥用方式二：自动化对话推进欺诈**

若自动回复能够就业务内容作出实质性答复，攻击者可以把它当作对话对手，逐步推进：确认对方身份、确认流程环节、获取内部用语与格式，再据此伪造后续邮件。整个过程**不需要任何真人参与，可批量对多个组织同时进行**。

ENISA Threat Landscape 2025 在威胁面梳理中指出社会工程手法正因自动化能力而扩大规模，这与邮件侧的观察一致：攻击的瓶颈从「人力」变成了「通道是否开放」。

**控制措施：**对**首次通信的外部地址**不启用实质性自动回复，仅返回最小确认；实质性答复必须经人工确认后发出。

**滥用方式三：把自动回复当作放大器**

自动回复对来信必答的特性，可被用于两类放大：其一，向大量伪造的发件地址投递，使自动回复涌向第三方（回散射）；其二，构造两个互相自动回复的地址形成循环。

**控制措施：**

* 对同一发件地址、同一发件域设置回复频率上限与时间窗。
* 不对退信、列表类邮件、批量邮件自动回复（依据 RFC 5322 Internet Message Format 与相关头部字段判断）。
* 仅对通过 RFC 7489 Domain-based Message Authentication, Reporting, and Conformance (DMARC) 校验且对齐的来信启用自动回复，未通过者只记录不回复。
* 为自动回复设置全局速率上限，超限即熔断并告警。

**滥用方式四：与提示注入组合**

若自动回复由模型生成，来信正文即是模型输入，**提示注入的全部风险在此处自动继承**：攻击者可指示模型在回复中附上历史邮件内容、附上内部信息，或改变回复的收件人。

OWASP Top 10 for Large Language Model Applications 对提示注入与不安全输出处理的描述，直接适用于这一场景。

**控制措施：**自动回复路径下，模型**不得具备任何检索历史邮件的权限**，收件人固定为原发件人且不可被内容改变，输出经模板约束后发出。

**治理落地清单**

1. 盘点当前所有自动回复与自动摘要功能的启用范围与权限。
2. 把输出内容收敛到受控模板，禁止自由生成人员与组织信息。
3. 对首次通信外部地址关闭实质性自动回复。
4. 配置频率上限、批量邮件例外、鉴别失败不回复三项规则。
5. 自动回复全量留痕：触发条件、来信 Message-ID、实际发出内容。
6. 按 NIST AI 100-1 Artificial Intelligence Risk Management Framework (AI RMF 1.0) 的风险管理循环定期复审，功能变更后重新评估。

参考：[OWASP Top 10 for Large Language Model Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/) ｜ [ENISA Threat Landscape 2025](https://www.enisa.europa.eu/publications/enisa-threat-landscape-2025) ｜ [RFC 7489 Domain-based Message Authentication, Reporting, and Conformance (DMARC)](https://www.rfc-editor.org/rfc/rfc7489.html) ｜ [NIST AI 100-1 Artificial Intelligence Risk Management Framework (AI RMF 1.0)](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/ai-auto-reply-abuse.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
