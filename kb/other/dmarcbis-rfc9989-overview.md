---
title: "DMARCbis 协议更新：RFC 9989 替代 RFC 7489 完整解读"
source: "https://ztpop.net/kb/dmarcbis-rfc9989-overview.html"
license: CC-BY 4.0
---

# DMARCbis 协议更新：RFC 9989 替代 RFC 7489 完整解读

# DMARCbis 协议更新：RFC 9989 替代 RFC 7489 完整解读

⁣​‌​‌‌​‌​​‌​‌​‌​​​‌​‌​​​​​‌​​‌‌‌‌​‌​‌​​​​​‌‌‌‌‌​​​​‌‌​​‌​​​‌‌​​​​​​‌‌​​‌​​​‌‌​‌‌​​​‌​‌‌​‌​​‌‌​​​​​​‌‌‌​​​​‌‌‌‌‌​​​‌‌‌​‌‌​​​‌‌​​​‌​‌‌‌‌‌​​​‌​​​‌‌​​‌​​​‌​‌​‌​​​‌​​​‌​​​‌​‌⁤

RFC 9989 / Standards Track / 2026 年 5 月发布

2026-07-28 · ztpop.net 邮件技术知识库

## 一、概述（摘要）

2026 年 5 月，IETF 正式发布了 **RFC 9989**（Domain-Based Message Authentication, Reporting, and Conformance (DMARC)），标志着 DMARC 协议从 Informational（信息性）RFC 正式升级为 **Internet Standards Track（标准轨道）**RFC。该文档同时废弃了服役 11 年的 RFC 7489（2015 年 3 月发布）和 RFC 9091（PSD DMARC，2021 年 7 月发布），是 DMARC 协议自诞生以来最重要的一次版本更新。

RFC 9989 的发布是 IETF DMARC Working Group 正式工作组 5 年工作的成果。与 RC 7489 由独立投稿人向 RFC 系列发表不同，RFC 9989 经历了完整的 IETF 标准化流程——工作组讨论、WG Last Call、IESG 评审等环节，代表了 IETF 社区的广泛共识。正如 Steve Atkins 在 Word to the Wise 的评论文章中所说："It's not DMARCbis any more, it's just DMARC."（"bis"在拉丁语中意为"再次"，协议界用于表示第二版；但 RFC 9989 承载的不只是修订，而是 DMARC 的正式标准身份。）

**核心变更一览：**

* 从 **Informational** 升级为 **Standards Track**（DMARC 工作组正式成果）
* 废弃 **RFC 9091**（PSD DMARC），PSD 策略发现整合入 DNS Tree Walk
* RFC 7489 的 **15 个勘误（Errata）**全部修复
* 引入 **DNS Tree Walk** 替代 PSL（公共后缀列表）依赖
* 新增 **3 个标签**（np、psd、t），移除 **3 个标签**（pct、rf、ri）
* 新增 **7 个术语**，更新 **2 个术语**
* 大幅扩展域名所有者行动指南（从 2 段扩展到 8 步完整指南）

## 二、核心升级：从 Informational 到 Standards Track

### 2.1 标准化历程

RFC 7489 于 2015 年 3 月由独立投稿编辑（Independent Submissions Editor）发布，属于 Informational RFC 类型。这意味着它描述了社区的实践经验而非正式的 IETF 标准。自发布以来，DMARC 在全球得到了广泛部署——Google、Microsoft、Yahoo! 等大型邮箱提供商均采用 DMARC 策略保护其品牌域名。然而，作为一个 Informational 文档，RFC 7489 缺乏正式的 IETF 标准化背书，同时也存在多个已知的勘误和实现歧义。

2019 年，IETF 成立了正式的 DMARC Working Group，启动了 DMARCbis（"bis"=修订版）项目。历经 5 年的讨论和修订，RFC 9989 最终于 2026 年 5 月以 Standards Track 身份发布，标志着 DMARC 正式成为互联网标准。

### 2.2 废弃 RFC 9091（PSD DMARC）

RFC 9091（"DMARC Extension for Public Suffix Domains"）于 2021 年发布，作为 Experimental RFC 试图解决公共后缀域（如 .com、.co.uk 等）的 DMARC 策略发现问题。该实验的结果表明：RFC 9091 **并未按原文实现**。RFC 9989 重新定义了 PSD 策略发现算法——通过 DNS Tree Walk 直接整合 PSD 检测功能，从而废弃并取代了 RFC 9091。

### 2.3 15 个勘误全部修复

RFC 9989 及其附属文档（RFC 9990、RFC 9991）逐一解决了 RFC 7489 自 2015 年发布以来累积的全部 15 个勘误（Errata）。这些勘误涵盖 IP 地址正则表达式错误、策略发现算法描述不准确、示例语法错误、标签定义模糊等多个方面。其中涉及 DMARC 策略发现流程（Errata 5495、7835）和 PSL 使用（Errata 6729）的勘误已通过对 DNS Tree Walk 的重新设计完全清除。

## 三、三大架构性变更

### 3.1 DNS Tree Walk：告别 PSL 依赖

RFC 9989 最具影响力的架构变更当属 **DNS Tree Walk**——一种不再依赖人工维护的公共后缀列表（PSL），转而通过直接在 DNS 树中进行层级遍历来发现 DMARC 策略记录的技术。

#### 3.1.1 为什么需要改变？

RFC 7489 定义了 Organizational Domain（组织域）的概念，即"在域名注册商处注册的域"。然而 RFC 7489 要求借助 PSL（如 publicsuffix.org 维护的列表）来确定一个域名到底"注册"到哪一层。这种做法存在几个问题：

* **PSL 是人工维护的**——更新滞后、覆盖不全、无法保证所有邮件接收方使用同一个版本
* **RFC 7489 未强制要求使用特定的 PSL**——不同邮件接收方可能使用不同的 PSL，导致互操作性问题
* **未规定 PSL 的获取频率**——部分接收方可能使用数月甚至数年前的旧数据
* **无法支持复杂组织的分层管理**——大型企业可能希望在不同子域层级上应用不同的 DMARC 策略

RFC 7489 本身已经意识到了这个问题（见原文档 Section 3.2 中的相关讨论），指出：如果能够创建一种更可靠、更安全的 Organizational Domain 确定方法，应该替代对 PSL 的依赖。RFC 9989 正是用 DNS Tree Walk 回应了这一呼吁。

#### 3.1.2 DNS Tree Walk 算法

DNS Tree Walk 的核心思想很简单：从 Author Domain 开始，逐级向上层父域查询 \_dmarc TXT 记录，直到找到有效的 DMARC Policy Record 或到达根域。具体算法步骤（RFC 9989 Section 4.10）如下：

1. **查询域**：在 Author Domain 的 \_dmarc 子域下查询 TXT 记录（如 \_dmarc.example.com）
2. **过滤无效记录**：丢弃不以正确版本号 v= 标记开头的记录；如果返回多条记录，全部丢弃
3. **检查终止条件**：如果找到的单条记录包含 psd=n 或 psd=y 标签，停止遍历
4. **标签剥离**：将域名拆分为标签序列（从右向左编号 1,2,3,...），如 x < 8 则移除最左标签，如 x ≥ 8 则一直缩短到只剩 7 个标签
5. **查询父域**：在新目标域名上重复上述查询
6. **迭代**：循环执行步骤 2-5，直到找到有效的 DMARC Policy Record 或没有更多标签可移除

#### 3.1.3 8 层查询限制

为防止恶意域名所有者构造超长 Author Domain（如 a.b.c.d.e.f.g.h.i.j.mail.example.com）对邮件接收方实施拒绝服务攻击，DNS Tree Walk 内置了一个关键安全限制：

**规则**：如果 Author Domain 超过 8 个标签（labels），直接缩短至 7 个标签后再开始遍历，从而保证最多执行 8 次 DNS 查询。

观察数据显示，截至 RFC 9989 发布时，实际使用中的 Author Domain 最多包含 7 个标签，因此 8 层限制足以覆盖当前所有合法使用场景，并为未来留有一定扩展空间。

#### 3.1.4 psd 标签与 PSD 策略发现

psd 标签是 RFC 9989 新增的标签之一，用于标注一个域是否为公共后缀域（PSD，如 .com、.org、.co.uk 等顶级或伪顶级域）。其有效值：

* **y**：表明该域是一个 PSD，下游的 Organizaitonal Domain 需要在其子域中查找
* **n**：表明该 DMARC Policy Record 的发布者虽然不是一个 PSD，但它希望被视为其自身及其子域的组织域
* **u**（默认）：不确定，使用标准的 DNS Tree Walk 确定 Organizational Domain

PSO（公共后缀运营商）在 PSD 上发布 DMARC 策略记录时，必须包含 psd=y 标签。例如，运营商在 example.co.uk 上发布 \_dmarc TXT 记录并设置 psd=y，则邮件接收方在遍历时遇到该记录会停止并向下一级（如 sub.example.co.uk）查找真正的组织域策略。

### 3.2 新增标签

#### 3.2.1 np：从不存在的子域策略

np（non-existent policy）标签定义了当 Author Domain 在 DNS 中不存在（NXDOMAIN）时应用的子域策略。该标签源自 RFC 9091 的实验性定义，在 RFC 9989 中正式纳入核心标准。

语法与 p 标签相同（值可为 none、quarantine、reject）。如果未设置 np，则回退到 sp 标签（如果存在），否则回退到 p 标签。

**典型用例**：  
`v=DMARC1; p=reject; sp=quarantine; np=none; rua=mailto:dmarc@example.com`  
这意味着：主域策略为 reject，现有子域策略为 quarantine，但从不存在的子域（DNS 查询返回 NXDOMAIN）发送的邮件仅做监控（none）。这种差异化策略可以避免因域名拼写错误或临时 DNS 问题导致的误拒。

#### 3.2.2 psd：PSD 标志

如上所述，psd（Public Suffix Domain）标签用于标记 DMARC Policy Record 的发布者是否为公共后缀域。这是一个服务于 DNS Tree Walk 的标志性标签，帮助邮件接收方在树遍历过程中确定停止点。

#### 3.2.3 t：测试标签

t（testing）标签替代了 RFC 7489 中 pct 标签的部分功能。其有效值：

* **y**：请求邮件接收方不实际应用声明的策略，而是将策略降低一级执行。即 p=reject + t=y → 实际应用 quarantine；p=quarantine + t=y → 实际应用 none
* **n**（默认）：正常应用策略

为什么用 t 替代 pct？RFC 9989 Appendix A.6 指出：运营经验表明，pct 标签通常只在取值为 0 或 100（默认值）时被准确执行。中间值的实现在不同邮件接收方之间差异极大。然而 pct=0 的实际效果——触发某些中间件和邮箱提供商对 From 头部进行特殊改写以避免下游 DMARC 失败——对域名所有者具有重要价值。因此 RFC 9989 将这一二元功能（"测试 / 非测试"）抽取为独立的 t 标签，语义更加清晰。

### 3.3 移除标签

| 移除标签 | 原名 | 移除原因 | 替代方案 |
| --- | --- | --- | --- |
| **pct** | 百分比 | 只在 0 和 100 时被准确执行，中间值实现不统一 | t 标签（二元测试模式） |
| **rf** | 报告格式 | 报告格式只有一种（XML AFNF），定义多余 | 不替换（始终使用 XML） |
| **ri** | 报告间隔 | 日常运营中邮件接收方很少遵循指定的间隔 | 不替换（接收方自行决定） |

## 四、术语更新

### 4.1 新增 7 个术语

RFC 9989 在 Section 3.2 中新增了以下术语：

| 术语 | 英文 | 定义摘要 |
| --- | --- | --- |
| 域名所有者评估策略 | Domain Owner Assessment Policy | 域名所有者在 DMARC Policy Record 中表达的关于验证失败消息的处理偏好（p=、sp=、np= 三个标签的值） |
| 强制执行状态 | Enforcement | 组织域的 p 标签不为 none 的状态（即 p=quarantine 或 p=reject） |
| 监控模式 | Monitoring Mode | 组织域的 p=none 且域名所有者正在接收聚合报告的状态 |
| 不存在的域 | Non-existent Domains | 与 RFC 8020 定义一致：DNS 查询返回 NXDOMAIN 的域名 |
| 公共后缀域 | Public Suffix Domain (PSD) | 顶级域或类似顶级域（如 .com、.co.uk） |
| 公共后缀运营商 | Public Suffix Operator (PSO) | 管理 PSD 的实体 |
| PSO 控制的域名 | PSO-Controlled Domain Names | PSO 直接控制的域名（在 PSD 中注册的域名归属 PSO 管理） |

### 4.2 更新术语

**Organizational Domain（组织域）**：RFC 7489 将其定义为"在域名注册商处注册的域"，并依赖 PSL 来确定。RFC 9989 将其重新定义为"域名命名空间层次结构中处于顶部且具有相同管理权限的域"，其确定方法不再依赖 PSL，而是通过 DNS Tree Walk 完成。

**Report Consumer（报告消费者）**：原名 Report Receiver（报告接收方）。重命名是为了更精确地反映该实体的角色——它是消费和分析 DMARC 报告的实体，而不仅仅是"接收"邮件。

## 五、域名所有者行动指南

RFC 7489 的"Domain Owner Actions"部分仅有两个段落，提供了非常简约的指导。RFC 9989 将其大幅扩展为 8 个步骤的完整实施指南（Section 5.1.1 - 5.1.8），不仅说明了"做什么"，还解释了"为什么"以及每个决策的影响。

### 5.1 八步实施步骤

1. **为对齐域发布 SPF 记录**（Section 5.1.1）：确保发送邮件的 RFC5321.MailFrom 域能产生与 Author Domain 对齐的 SPF 认证标识符。
2. **配置 DKIM 签名**（Section 5.1.2）：使用与 Author Domain 对齐的 DKIM Signing Domain 签署所有外发邮件。
3. **设置聚合报告接收邮箱**（Section 5.1.3）：创建用于接收 DMARC 聚合报告的邮箱（通过 rua 标签指定）。
4. **发布 DMARC Policy Record**（Section 5.1.4）：在 Author Domain 及其 Organizational Domain 上发布 DMARC TXT 记录，初始使用 p=none（监控模式）。
5. **收集并分析报告**（Section 5.1.5）：通过 DMARC 聚合报告审计自身的邮件发送流，找出认证配置中的缺口。
6. **修复不合规邮件流**（Section 5.1.6）：对通过报告发现的合法但未通过 DMARC 验证的邮件流进行修复（补充 DKIM 签名、修正 SPF 记录等）。
7. **决定是否升级到强制执行**（Section 5.1.7）：在确认所有合法邮件流都已通过认证后，考虑将 p 值从 none 升级为 quarantine 或 reject。
8. **大型组织与分散 DNS 管理**（Section 5.1.8）：特别为大型复杂组织提供的分散式 DNS 管理指南，利用 psd 标签实现子域层级策略自治。

### 5.2 最大变化：通用邮件域不推荐 p=reject

**重点**：RFC 9989 Section 7.4 明确指出——**拥有普通用户发送日常邮件的域不应部署 p=reject 策略**（SHOULD NOT deploy a DMARC policy of "p=reject"）。此建议在 Section C.6 中再次强调。Section 7.4 同时指出：邮件接收方不得仅凭 p=reject 策略拒绝邮件，而应将其作为综合决策的输入，结合其他知识和分析（内容过滤、发送模式等）来处理。

具体来说，Section 7.4 做出一系列"关键"（critical）声明：

* 发布 p=reject 的域名所有者如果仅依赖 SPF 实现 DMARC pass，则必须同时应用有效的 DKIM 签名，因为 SPF 在间接邮件流（转发、邮件列表）中几乎必然失败。
* 如果域名所有者有用户参与互联网邮件列表，发布 p=reject 将导致严重的互操作性问题——邮件列表服务通常因转发路径问题使 SPF 失败，而这些消息通常有有效的 DKIM 签名。
* 邮件接收方不应仅凭 p=reject 策略拒绝入站邮件，而应将该策略作为裁决的一部分，结合其他知识（观察到的发送模式、内容过滤等）。在没有其他信息来源的情况下，接收方应将策略视为 p=quarantine 而非 p=reject。

### 5.3 多报告 URI 支持

RFC 9989 Section 4.6（以及 C.7）明确规定：当 DMARC Policy Record 中指定了多个报告目标 URI 时，**报告应发送到列表中的每个 URI**（SHOULD be sent to each listed URI）。相比之下，RFC 7489 只要求接收方支持至少两个 URI（MAY impose a limit），但没有强调应发送到所有 URI。这一变更使得域名所有者可以同时向多个服务商发送 DMARC 报告，增强了审计和备案的灵活性。

## 六、互操作性与部署注意

### 6.1 Tree Walk 可能造成的互操作性问题

DNS Tree Walk 算法虽然更加灵活，但在过渡期可能造成互操作性问题：

* 如果邮件接收方使用了基于 RFC 7489（依赖 PSL）的实现，而域名所有者预期接收方使用 DNS Tree Walk，双方可能得出不同的 Organizational Domain
* 在 DNS 配置复杂（如有多级子域、CNAME 链式引用的场景）的域上，Tree Walk 和 PSL 方法的结果可能不一致

### 6.2 使用 strict alignment 可避免

RFC 9989 Section C.3 明确指出：**此问题完全可以通过使用 strict alignment 和在组织所有发送域上发布明确的 DMARC Policy Record 来避免**。如果域名所有者在每个实际使用的 Author Domain 上直接发布 \_dmarc 策略记录，则不论接收方使用 Tree Walk 还是 PSL，结果都是一致的——因为策略记录在 Author Domain 本身被发现，不需要向上遍历。

### 6.3 推荐配置（基于 Section 7.4）

**通用邮件域推荐配置**：  
`v=DMARC1; p=none; rua=mailto:dmarc-rua@example.com,mailto:rua@third-party-service.com`  
  
**阶段性升级建议**：  
1. 先发布 p=none 至少一个月 → 收集基线数据  
2. 升级到 p=quarantine 至少一个月 → 观察误判情况  
3. 评估是否继续升级到 p=reject（需关注邮件列表兼容性）  
4. 使用 t=y 标签在强制执行前进行最终测试

## 七、对中国邮件系统的影响

### 7.1 国内主流邮件系统对 DMARC 的支持情况

目前国内主流邮件系统对 DMARC 的支持情况如下：

| 邮件系统 | DMARC 验证 | 聚合报告 | 备案 |
| --- | --- | --- | --- |
| QQ 邮箱 | 部分支持（p=reject 时外部入信可能被拒） | 有限支持 | - |
| 网易邮箱 | 支持基本 DMARC 验证 | 有限支持 | - |
| 阿里邮箱 | 支持（企业版） | 支持 | - |
| 腾讯企业邮 | 支持 | 支持 | - |
| Coremail | 完整支持（兼容 RFC 7489 和部分 RFC 9989） | 支持 | 支持 rua 解析 |

值得注意的是，大部分国内邮件系统目前仍基于 RFC 7489 实现，尚未完全适配 DNS Tree Walk。这意味着在过渡期内：

* 国内邮箱可能仍然依赖 PSL（而非 DNS Tree Walk）确定 Organizational Domain
* 使用 RFC 9989 新增标签（如 np、t、psd）的域名所有者可暂时作为冗余配置——接收方会忽略不认识的标签
* 移除的标签（pct、rf、ri）已经失去效用，新部署不应再使用

### 7.2 Coremail 等国产邮件系统如何适配

Coremail 作为国内部署最广泛的邮件系统之一，已在近年版本中加强了对 DMARC 的完整支持。针对 RFC 9989 的适配，预计需要关注以下方面：

* **DNS Tree Walk**：需要新增 DNS 树级遍历逻辑，替代或并行运行现有的 PSL 依赖实现。在过渡期，建议两个方法同时运行并对比结果
* **新增标签解析**：需要解析 np、psd、t 标签，并适配相应的策略逻辑（如 np=none 对 NXDOMAIN 域放行）
* **报告功能调整**：pct 标签已移除，需要使用 t 标签的语义来替代

### 7.3 金融/政府等受等保合规约束的单位

对于金融、政府、央企等受等保（信息安全等级保护）和关键信息基础设施保护条例约束的单位，RFC 9989 的发布需要关注以下几点：

1. **修订安全基线**：等保三级及以上单位的安全配置基线中通常包含 DMARC 部署要求。应根据 RFC 9989 更新基线，确认使用 p=reject 适当性（Section 7.4 建议通用邮件域不应使用 p=reject）。
2. **DNS 基础设施升级**：DNS Tree Walk 要求 DNS 基础设施支持子域粒度的 TXT 查询。党政机关通常使用多级子域结构（如 xxx.gov.cn），需要验证 DNS 解析器对深层域名遍历的支持。
3. **审计报告适配**：公共邮箱域（如 gov.cn 下的子域）的 PSO（主管部门或域名运营商）可能需要在伪顶级域上发布带有 psd=y 的 DMARC 记录，以便下级单位能正确发现和管理自己的域策略。
4. **旧系统兼容验证**：如果单位部署了基于 RFC 7489 的 DMARC 验证中间件或网关，需要联系供应商确认其 RFC 9989 适配时间表。

## 八、总结与行动建议

RFC 9989 的发布是 DMARC 协议发展的重要里程碑。对于中国邮件行业从业者，以下是立即可以采取的行动：

* **学习**：通读 RFC 9989 的 Section 7.4（互操作性考量）和 Appendix C（与 RFC 7489 的变更对照），这是理解新版协议的最快路径。
* **审计**：检查现有的 DMARC 部署，确认 pct、rf、ri 三标签已替换为 t 标签等新机制。
* **配置**：在 DNS 中为多级子域结构评估是否需要使用 np、psd 标签。
* **评估**：对于通用邮件域，认真参考 Section 7.4 的建议——不要在未充分评估影响前升级到 p=reject。
* **关注**：跟踪国内邮件系统供应商（Coremail、阿里邮箱等）的 RFC 9989 适配计划。

正如 Steve Atkins 所总结的："It's not DMARCbis any more, it's just DMARC."——DMARC 的版本号仍然是 1，但协议本身已经成熟到了正式互联网标准的水平。

## 参考文献

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/dmarcbis-rfc9989-overview.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
