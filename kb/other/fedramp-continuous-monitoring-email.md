---
title: "FedRAMP 持续监控（ConMon）对邮件类云服务提出了哪些要求？"
source: "https://ztpop.net/kb/fedramp-continuous-monitoring-email.html"
license: CC-BY 4.0
---

# FedRAMP 持续监控（ConMon）对邮件类云服务提出了哪些要求？

1
FedRAMP 持续监控（ConMon）对邮件类云服务提出了哪些要求？
▼

**ConMon 的方法论基线与三大目标**

FedRAMP（Federal Risk and Authorization Management Program，美国联邦风险与授权管理计划）官方文档明确说明：FedRAMP 的持续监控（ConMon）建立在 **NIST SP 800-137《Information Security Continuous Monitoring for Federal Information Systems and Organizations》**所描述的持续监控流程之上，目标是提供三项能力：

1. **运行可见性（operational visibility）**；
2. **受管控的变更控制（managed change control）**；
3. **履行事件响应职责（attendance to incident response duties）**。

云服务商（CSP）ConMon 能力的有效性，直接支撑联邦机构的**持续授权决策**。CSP 通过向联邦机构客户提供 ConMon 交付物来报告云服务产品（CSO）的安全态势。若 CSP 拥有**一个以上**联邦机构客户，则必须实施**协同式 ConMon（collaborative ConMon）**，以精简流程、尽量减少重复工作，同时仍让每个机构能履行各自的尽职调查。

**时效提示：**FedRAMP 官方于 2026 年 6 月 24 日声明，legacy 文档站的全部材料仅供向「Consolidated Rules for 2026」过渡期间参考，并特别提醒「人类与 AI 服务在引用 fedramp.gov/legacy 内容时须谨慎」。本文所述为 Rev5 时期的 ConMon 要求，实际合规请以 FedRAMP 当期生效规则为准。

**运行可见性：月度交付物**

官方对交付节奏的规定是：交付物与支撑证据按**每月、每年、每三年以及按需**提供；各项持续监控活动所对应控制的**最低频率要求**标注在 FedRAMP 安全控制基线工作簿的 J 列中。

月度 ConMon 上报的核心要求：

* 安全控制 **CA-5** 要求 CSP 制定并维护**行动计划与里程碑（POA&M）**，记录针对安全评估与 ConMon 活动中识别出的风险（弱点、缺陷与漏洞）的整改计划。
* 安全控制 **CM-8** 要求 CSP **至少每月**、或在发生变更时提供更新后的资产清单（inventory）。
* 每月 CSP 需向安全存储库上传最新的 POA&M 与资产清单，并在与机构客户的协议要求时一并上传**原始漏洞扫描文件**与报告。机构授权官（AO）审查这些交付物，以确认 CSO 的风险态势仍足以支撑本机构对该系统的使用。

POA&M 管理的关键规则包括：初始授权包提交的 POA&M 必须与 SAR 中的**风险暴露表（RET）**一一对应；所有未关闭风险都必须记录在 POA&M 的「Open」页签，即便尚未逾期；在 ConMon 阶段，CSP 仅需捕获并跟踪**已逾期**的扫描类风险，但 3PAO 安全评估中识别的所有风险都必须体现在初始授权包的 POA&M 中。此外文件规定了三类特殊处置：**风险调整（RA）**需以缓解因素或补偿控制说明其降低了被利用的可能性或影响；**误报（FP）**经 3PAO 验证后移入「Closed」页签；**运行必需项（OR）**指因系统无法按预期运行或厂商明确表示不打算修复而无法整改的发现——FedRAMP **不会为高危漏洞批准 OR**。未经 3PAO 验证的 RA 与 FP 须标为「Pending」，并在授权前获得机构 AO 批准。

**漏洞扫描的具体要求**

官方说明漏洞扫描是持续监控的关键组成部分，相关要求围绕控制 **RA-5** 展开，适用于全部 FedRAMP 安全控制基线。主要规定包括：

* **扫描器自身韧性**：扫描器应加固以抵御未授权使用或篡改（例如关闭不必要的端口与服务）。
* **经鉴别扫描**［RA-5(5)］：对中（Moderate）与高（High）影响系统，CSP 必须尽可能执行经鉴别的扫描。
* **完整授权下扫描**［RA-5(5)］：对所有中、高影响系统，扫描必须在系统完整授权下进行，须避免典型的权限不足问题（无法访问远程注册表、注册表访问受限、文件访问受限等）。
* **机器可读的发现结果**：扫描输出必须以结构化机器可读格式（如 XML、CSV 或 JSON）呈现所有低风险及以上的发现；若扫描器支持多种机器可读格式，CSP 须选择信息量最大的一种。条件允许时，机器可读数据须包含扫描的鉴别与授权状态，以证明每台主机上经鉴别扫描的执行程度。
* **NVD 与 CVE 引用**：对最新版 NIST 国家漏洞库（NVD）中列出的任何漏洞，机器可读数据中必须包含其 CVE 编号。
* **CVSS 风险评分**：对在最新版 NVD 中已赋予 CVSSv3 基础分的漏洞，必须以该 CVSSv3 基础分作为原始风险评级；若无 CVSSv3 分数，可用 CVSSv2 基础分；若均无 CVSS 分数，则可采用扫描器原生的基础风险评分。
* **配置一致性证据**：月度扫描须附带机器可读证据，证明扫描器配置未偏离最近一次授权评估中经评估方验证批准的配置（例如配置副本或配置校验和）；若需超出常规打补丁与更新的配置变更，必须通知 AO 并获其批准。
* **特征库更新**［RA-5(2)］：每次交付前，CSP 必须把已扫描漏洞清单更新到最新可用列表；所用扫描器须**至少每月**检查其漏洞库的自动特征更新，并提供扫描前最近一次更新的自动化机器可读证据。
* **充分的资产识别**：扫描结果必须包含可映射到资产清单的唯一资产标识符；CSP 须具备自动化机制，**每月**识别并编目授权边界内的全部资产，以确保无遗漏扫描。

**变更控制与年度评估**

**显著变更（Significant Changes）**：官方引用 NIST SP 800-37 Rev.2 的定义——「可能实质性影响系统安全或隐私态势的变更」。FedRAMP 将显著变更分为三类：**Routine Recurring（常规重复）、Transformative（变革型）与 Adaptive（适应型）**。其中常规重复变更**无需**机构授权官审查批准；变革型与适应型变更**必须**经审查批准。常规重复变更指 CSP 为处理缺陷或漏洞、应对事件以及执行日常维护与服务交付而**定期且例行**开展的变更，它们依托成熟流程识别、缓解与修复风险，常常完全自动化、甚至无需人工介入。官方给出的判定要点是：**若该活动并非定期且例行发生，就不能归为此类**——例如为修复漏洞而更换全部物理防火墙显然不属于常规例行。CSP 需记录显著变更、执行安全影响分析，并按变更类型走对应流程。

**年度评估（Annual Assessment）**：安全控制 **CA-2** 要求 CSP **至少每年**接受一次对云服务产品的独立评估。流程要点包括：制定评估排期（多数 FedRAMP 认可的 3PAO 已有排期模板，排期须涵盖全部交付物的技术与质量保证审查所需时间与资源）；**至少每年**审查并按需更新 SSP 及其附录，以纳入系统变更与流程规程变化（注意 FedRAMP 会定期更新 SAP、SAR 含 SRTM 与 RET、POA&M 等模板，须使用最新版）；**至少每年**测试事件响应计划（IRP）与应急计划（CP），未执行测试会拖延评估；由 CSP 与评估方共同使用 FedRAMP 年度评估控制选择工作表界定评估范围。此外，最近一次仅按 FedRAMP Rev 4 基线评估过的 CSO，必须针对 Rev 5 基线重新执行一次**完整**安全评估。

**对邮件类云服务的启示：**若邮件系统以 SaaS/托管方式向联邦或类似监管客户交付，需把「月度 POA&M 与资产清单」「经鉴别的月度漏洞扫描与机器可读结果」「显著变更分类与审批」「年度独立评估与 IRP/CP 演练」四项固化为常态化运营流程，而不是把安全评估视为一次性的准入动作。

参考：FedRAMP Continuous Monitoring (ConMon) Playbook（整合自 ConMon 策略指南 v3.2、漏洞扫描要求 v3.0、年度评估指南 v3.0、显著变更政策与规程 v1.0 等），[fedramp.gov/legacy/playbook/csp/continuous-monitoring/intro/](https://www.fedramp.gov/legacy/playbook/csp/continuous-monitoring/intro/)；方法论基线为 NIST SP 800-137《Information Security Continuous Monitoring for Federal Information Systems and Organizations》，显著变更定义引自 NIST SP 800-37 Rev.2

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/fedramp-continuous-monitoring-email.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
