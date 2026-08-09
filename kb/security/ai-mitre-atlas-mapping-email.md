---
title: "邮件场景里的 AI 相关威胁，怎么映射到 MITRE ATLAS？"
source: "https://ztpop.net/kb/ai-mitre-atlas-mapping-email.html"
license: CC-BY 4.0
---

# 邮件场景里的 AI 相关威胁，怎么映射到 MITRE ATLAS？

**先明确 ATLAS 解决什么问题**

MITRE ATLAS™ (Adversarial Threat Landscape for AI Systems) 是面向人工智能系统的对手战术与技术知识库，结构上沿用了大家熟悉的「战术（攻击者的目标阶段）—技术（达成目标的手段）」组织方式，但对象是 AI 系统本身。

**它的价值不在于提供防护产品清单，而在于提供一份「攻击者可能怎么做」的结构化清单**，供防守方逐项检查自己是否有对应的检测与缓解能力。用错的方式是把它当成合规打钩表；用对的方式是把它当成覆盖度自查的坐标系。

说明：ATLAS 的具体战术与技术条目会随版本更新，编号与命名应以官方站点当前发布内容为准，本文不固化条目编号。

**第一步：把邮件系统里的 AI 组件拆出来**

映射的前提是知道自己有哪些 AI 资产。邮件场景中常见的 AI 组件：

* **入站判分模型**：垃圾邮件/钓鱼判定、附件与 URL 风险评分。
* **内容理解模型**：摘要、分类、意图识别、自动打标。
* **生成类助手**：起草回复、自动回复、翻译。
* **检索增强组件**：把历史邮件或知识库内容喂给模型的检索层。
* **训练与反馈回路**：用户标记「这是垃圾邮件/这不是」所形成的持续学习通道。

**最容易被漏掉的是最后一项。**反馈回路是外部可影响的输入通道，却常常不在资产台账里。

**第二步：按攻击者目标阶段逐段提问**

不必强行套用条目编号，先用战术阶段的提问方式做一遍覆盖度检查：

* **侦察：**攻击者能否探明我们使用了何种判定模型？发不同变体邮件观察是否被拦截，就是一种低成本探测。我们能否发现这种探测？
* **初始访问：**模型的输入通道有哪些？邮件正文、附件、URL 落地页、用户反馈标记，都是入口。
* **执行与持久化：**注入内容能否影响后续行为？反馈回路被污染后是否会长期生效？
* **规避：**对抗性改写能否使恶意邮件被判为正常？我们是否统计了「先被拦后被放行」的样本？
* **数据外泄：**模型是否可能在输出中带出训练数据或检索到的历史邮件内容？
* **影响：**能否通过大量误报把正常邮件推入隔离区，形成业务中断？

**每一问都要落到「有没有对应日志字段、有没有对应告警规则」，否则映射没有产生任何防守价值。**

**第三步：把映射结果转成检测缺口清单**

映射的产物应当是一张**三列表**：攻击手法 → 现有检测手段 → 缺口。示例性的填法：

* 模型探测 → 目前无 → 缺口：需按发件域统计「短时间内多变体投递且判定结果分布异常」。
* 反馈回路污染 → 目前无 → 缺口：需记录标记来源账号，对异常高频标记账号设阈值。
* 规避性改写 → 部分有 → 缺口：需要把「同一活动下判定翻转」的样本单独入库供复盘。
* 检索层数据外泄 → 目前无 → 缺口：需对助手输出做敏感字段扫描并留痕。

缺口清单可直接对接 NIST AI 100-1 Artificial Intelligence Risk Management Framework (AI RMF 1.0) 的 MEASURE 与 MANAGE 环节，成为可跟踪的风险处置项。

**三个常见误用**

1. **把 ATLAS 当成传统网络攻防矩阵的替代品。**两者对象不同：邮件系统的常规入侵路径仍需用传统框架覆盖，ATLAS 补的是 AI 组件这一层，二者互补而非替代。
2. **只映射「模型被攻击」，忽略「模型被用作攻击工具」。**邮件场景中后者危害更直接——生成式能力被用来批量制造钓鱼内容，这属于威胁态势议题，可参照 ENISA Threat Landscape 2025。
3. **映射完就归档。**模型、提示词、权限、供应商都会变，映射结果需要在每次架构变更时复核，否则很快失真。

**与既有安全运营的衔接**

不要为 AI 组件单独建一套流程。可行的做法是：把上述缺口清单产生的告警**并入现有工单与值班体系**，共用同一套定级标准与响应时限；事件处置流程沿用 NIST SP 800-61 Rev.3 Incident Response Recommendations and Considerations 的组织方式，只在证据采集清单里补充模型输入输出、工具调用记录这些新字段。

参考：[MITRE ATLAS™ (Adversarial Threat Landscape for AI Systems)](https://atlas.mitre.org/) ｜ [NIST AI 100-1 Artificial Intelligence Risk Management Framework (AI RMF 1.0)](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf) ｜ [ENISA Threat Landscape 2025](https://www.enisa.europa.eu/publications/enisa-threat-landscape-2025) ｜ [NIST SP 800-61 Rev.3 Incident Response Recommendations and Considerations](https://csrc.nist.gov/pubs/sp/800/61/r3/final)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/ai-mitre-atlas-mapping-email.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
