---
title: "Exchange Online 邮件归档与合规策略 — 安全与合规中心功能深度解析"
source: "https://ztpop.net/kb/exchange-online-archive-compliance.html"
license: CC-BY 4.0
---

# Exchange Online 邮件归档与合规策略 — 安全与合规中心功能深度解析

邮件归档需求在企业环境中从"可选项"变为"必选项"的过程，与邮件系统的部署形态密切相关。Exchange Online 作为云交付的邮件系统，天然集成了部分归档与合规功能——但这种"内置"是一把双刃剑：一方面它减少了额外部署第三方归档系统的运维复杂度，另一方面它在数据驻留、迁移灵活性和长期存储成本上引入了云供应商锁定风险。理解 Exchange Online 归档功能的技术边界，是邮件管理员做出架构决策的前提。

## 一、Exchange Online 归档架构概览

Exchange Online 中的邮件归档（Archiving）与邮件保留（Retention）是两层独立但相互协作的功能：

* **归档邮箱（In-Place Archive）**：每个用户的辅助存储空间，邮件自动从主邮箱移入归档邮箱，释放主邮箱配额。归档邮箱使用与主邮箱相同的存储基础结构，但数据层做了冷热分离优化
* **保留策略（Retention Policies）与保留标签（Retention Labels）**：定义邮件在何时该删除、何时该标记为保留。保留标签是"标签级"的精细控制，保留策略是"文件夹/邮箱级"的批量控制
* **Litigation Hold 与 eDiscovery**：法律调查期间保护相关邮件不被删除，并支持按条件搜索和导出

## 二、保留标签与保留策略：设计原理与实践约束

### 2.1 保留标签（Retention Labels）

保留标签是 Microsoft Purview 合规体系的原子单元。每个标签由两个参数定义：

1. **保留周期**（Retention Period）：以天/月/年为单位，从邮件创建时间或事件时间开始计时
2. **保留操作**（Retention Action）：保留后自动删除（Delete Only）或保留后不再操作（Retain Only）

关键的技术约束在于：保留标签的计时起点可以是"邮件创建时"或**事件基准**（Event-based retention）。事件基准保留（Event-triggered retention）是 Exchange Online 特有的设计——例如"员工离职当日开始计算 7 年保留"，这种场景下计时起点不是邮件创建时间，而是 HR 系统标记的离职事件。这个设计对邮件归档合规非常有价值，但引入了跨系统事件协调的复杂度：

* 需要将 HR 系统的员工离职事件推送到 Purview Compliance Portal
* 事件必须在保留标签的"事件类型"中预先注册
* 如果事件从未触发，邮件将无限期保留——这是常见的配置错误源

### 2.2 保留策略（Retention Policies）

保留策略是保留标签的"容器"。一条保留策略可以包含多个保留标签，每个标签作用于不同的内容类型（电子邮件、文档、Skype 聊天记录等）。在邮件归档场景下，保留策略的典型配置是：

```
# 在 Exchange Online 中创建保留策略（通过 Security & Compliance Center PowerShell）
# 注意：Exchange Online 的保留策略管理已迁移至 Purview Compliance Portal
Import-Module ExchangeOnlineManagement
Connect-IPPSSession -UserPrincipalName admin@domain.onmicrosoft.com

# 创建"7年-合规审计"保留标签
New-ComplianceTag -Name "7Y-Compliance-Audit" `
    -Comment "All emails related to compliance audit - retain 7 years" `
    -RetentionDuration 2555 `
    -RetentionType CreationAgeInDays `
    -RetentionAction Retain `
    -RetentionActionDelete Delete

# 创建保留策略并关联标签
New-RetentionCompliancePolicy -Name "Financial-Compliance-Policy" `
    -Comment "Compliance retention for finance department" `
    -ExchangeLocation "FinanceTeam@domain.onmicrosoft.com"

# 将保留标签添加到策略
New-RetentionComplianceRule -Name "7Y-Finance" `
    -Policy "Financial-Compliance-Policy" `
    -RetentionComplianceAction Keep `
    -RetentionDuration 2555 `
    -RetentionDurationDisplayHint Days
```

### 2.3 保留策略的常见陷阱

1. **保留与删除的冲突规则**：当同一封邮件同时适用"保留 7 年"和"3 年后删除"两条规则时，Exchange Online 采用"最保守规则优先"——即保留规则始终胜出。这意味着时间最长的保留标签决定了邮件的实际生命周期
2. **自适应范围（Adaptive Scope）与静态范围（Static Scope）**：Exchange Online 支持基于属性的动态范围分配（例如"所有部门为 Finance 的用户"），但动态范围在首次应用时有最多 7 天的延迟。对于审计场景，务必将初始部署设为静态范围再过渡到动态范围
3. **保留锁定（Preservation Lock）**：将保留策略锁定后，任何人都不能关闭保留策略或缩短保留期——这满足了 SEC 17a-4 对非可重写（non-rewritable）格式的要求。但锁定是**不可逆**操作，锁定前必须确认保留策略配置完全正确

## 三、Litigation Hold：法律调查期间的邮件保护机制

Litigation Hold（诉讼保留）是 Exchange Online 中防止邮件在调查期间被用户或自动策略删除的核心功能。当对用户邮箱启用 Litigation Hold 后：

* 用户的已删除邮件（包括"可恢复的项目"文件夹中的内容）被无限期保留
* 用户无法永久删除任何邮件——即使清空了"已删除邮件"文件夹，副本仍保留在可恢复项目文件夹中
* 保留策略中设置的删除操作被静默覆盖——Litigation Hold 的优先级高于任何保留标签

```
# 对用户启用 Litigation Hold
Set-Mailbox user@domain.com -LitigationHoldEnabled $true `
    -LitigationHoldDuration 365 `
    -LitigationHoldDate "2026-07-01" `
    -RetentionComment "Hold initiated for Case #2026-045 - Financial Dispute" `
    -RetentionUrl "https://legal.internal/case/2026-045"

# 查看 Litigation Hold 状态
Get-Mailbox user@domain.com | `
    Select-Object DisplayName, LitigationHoldEnabled, LitigationHoldDuration, `
                    LitigationHoldDate, RetentionComment

# 禁用 Litigation Hold（通常在法院同意后）
Set-Mailbox user@domain.com -LitigationHoldEnabled $false
```

### 3.1 Litigation Hold 的技术限制

* **仅保护邮箱数据本身**：Litigation Hold 只冻结用户邮箱中的数据，不保护[邮件归档](/kb/email-archiving.html)副本中的日志和索引数据——如果你的归档方案使用了独立的日志系统，Litigation Hold 不会自动冻结这些日志
* **不涉及 In-Place Archive 的单独控制**：如果用户同时拥有主邮箱和 In-Place Archive，Litigation Hold 同时作用于两者——无法单独对 Archive 执行 Hold。这使得"仅归档数据需保留，主邮箱数据可灵活管理"的场景难以实现
* **保留项目计数限制**：Exchange Online 中可恢复项目（Recoverable Items）文件夹的最大容量为 30 GB×2（主邮箱 + 归档），超过时 Litigation Hold 会停止接受新的删除项目。需要配置扩容后才能持续保护

## 四、eDiscovery：搜索、审查与导出

### 4.1 eDiscovery 功能层次

Exchange Online 中的 eDiscovery（电子发现）能力分为三个层次：

Exchange Online eDiscovery 功能层次

| 层次 | 功能 | 许可要求 | 适用场景 |
| Content Search | 按关键词、发件人、日期范围的邮件搜索与导出 | E3 / 商业标准版 | 合规自查、数据主体请求（DSR） |
| eDiscovery (Standard) | 含 Case 管理、Hold 管理、导出和日志功能的 Content Search | E3 + 附加许可 | 法律调查、取证 |
| eDiscovery (Premium) | 含线程分析（Conversation Threading）、预测编码（Predictive Coding）、审查集（Review Set） | E5 | 大规模诉讼、复杂取证 |

### 4.2 Content Search 与导出

```
# 创建 Content Search（合规门户 UI 或 PowerShell）
New-ComplianceSearch -Name "Case-2026-045-Q1" `
    -ExchangeLocation user1@domain.com, user2@domain.com `
    -ContentMatchQuery "from:client@supplier.com AND subject:'contract' AND received>=01/01/2026 AND received<=03/31/2026"

# 启动搜索
Start-ComplianceSearch -Identity "Case-2026-045-Q1"

# 检查搜索状态
Get-ComplianceSearch -Identity "Case-2026-045-Q1" | Format-List Status,Items,Size

# 导出搜索结果（生成导出请求，在合规门户下载）
New-ComplianceSearchAction -SearchName "Case-2026-045-Q1" -Export
```

### 4.3 关键限制：与其他集中式归档方案的差异

Exchange Online 的 eDiscovery 与独立邮件归档系统（专注于[邮件服务器](/mail-server.html)日志和消息完整保存的系统）有两个关键差异：

1. **搜索范围受限于邮箱生命周期**：eDiscovery 搜索只能覆盖当前存在的活跃邮箱和已删除但尚未超过邮箱保留期的邮箱。一旦邮箱被永久删除（soft-deleted 期满），该邮箱的历史邮件不可恢复——除非已将邮件副本导入到第三方归档系统
2. **导出格式**：Content Search 导出的邮件以 PST 格式提供——PST 文件本身包含邮件内容，但不包含 SMTP 信封信息（envelope-from）和传输链信息。对于需要完整 MTA 轨迹（RFC 5321 传输路径）的取证场景，这构成了一个关键的证据缺口

## 五、Exchange Online 内置方案 vs 第三方归档方案对比

Exchange Online 内置 vs 第三方档案方案对比

| 维度 | Exchange Online 内置方案 | 第三方独立归档方案 |
| 数据驻留控制 | 受限于 M365 数据中心区域列表 | 可部署在指定数据中心的物理节点上，满足等保 2.0 数据不出境要求 |
| WORM 合规 | Preservation Lock 可满足基本 WORM 要求，但不可审计底层存储介质 | 支持 S3 Object Lock / 磁带 WORM / 哈希链等多种合规方式，底层可审计 |
| 多源数据归档 | 仅归档 Exchange Online 邮箱数据，不支持第三方邮件网关、社交平台、协作工具 | 支持 IMAP/POP3/SMTP Journaling/API 多数据源汇聚 |
| 搜索性能 | 大租户（>50,000 邮箱）的搜索可能在 30+ 分钟后返回结果 | 独立索引引擎（Elasticsearch/Solr），查询性能与邮箱数解耦 |
| 存储成本 | 归档数据存储在 M365 标准存储层，无冷热分级定价 | 支持 Hot→Warm→Cold 三级存储，冷数据成本可降低 60-80% |
| 供应商锁定 | 深度锁定——数据不可迁移至其他邮件系统 | 数据以 EML/MSG 标准格式保存，可迁移至任意邮件系统 |
| 合规审计支持 | 审计日志覆盖 90 天（默认），>90 天需要额外许可 | 自持审计日志，保存期可由归档管理员自定义 |

### 5.1 方案选择指南

* **纯 Exchange Online 环境 + 基本合规需求（180 天-1 年保留、等保 2.0 第一/二级）**——Exchange Online 内置归档 + Purview 保留策略通常足够，无需额外投入
* **Exchange Online + SEC 17a-4/SOX 合规需求 + 长周期保留（>3 年）**——建议使用第三方归档方案。Exchange Online 的 Preservation Lock 虽然在功能上可实现 WORM，但在独立审计验收中缺乏对底层存储介质的可审计性，SEC 合规审计时可能被视为"软 WORM"
* **跨国企业 + GDPR/数据驻留约束 + 多邮件系统混合环境**——必须选择第三方集中式归档方案。Exchange Online 内置方案无法满足数据驻留分区（中国数据不出境 + 欧洲数据不出欧盟）和跨系统（Exchange Online 与自建邮件系统共存）的场景

## 六、迁移规划：从 Exchange Online 内置归档到第三方方案的过渡路径

如果企业当前使用 Exchange Online 内置归档功能，后续决定迁移到第三方[邮件归档](/kb/email-archiving.html)系统，需要注意以下迁移要点：

1. **数据导出**：通过 Content Search 将所有得归档邮箱数据导出为 PST 文件。这可能在拥有大量归档邮箱时非常耗时——50,000 邮箱 × 10 GB 归档 ≈ 500 TB 导出量，建议分批执行
2. **Litigation Hold 交接**：在第三方归档系统就绪并配置了相应的 Legal Hold 之后，方可关闭 Exchange Online 的 Litigation Hold。中间的"保护真空期"不能超过 24 小时
3. **保留策略停用**：在 Purview 中逐步停用保留策略时，注意保留标签的"最保守规则优先"机制——即使策略停用，已应用的保留标签仍然持续生效，直到显式移除

## 总结

Exchange Online 内置的归档与合规功能——保留标签/策略、Litigation Hold、eDiscovery——是微软 Purview 合规体系在邮件场景下的直接映射。三个核心功能各有其"刚好够用"和"明显不够"的边界：保留标签在事件基准保留上很有创意，但缺乏冷热分层的存储优化；Litigation Hold 能有效冻结用户邮箱数据，但不保护日志和传输轨迹；eDiscovery 的 Content Search 对日常自查已够用，但在大规模取证导出和跨系统搜索上明显乏力。与第三方归档方案相比，Exchange Online 内置方案最大的短板在于供应商锁定和数据驻留不可控。在方案选型中，E3/E5 自带的功能不应自动成为"够用"的结论——特别是当业务面临 SEC/SOX/GDPR/等保 2.0 的多重合规审计时，第三方归档系统在独立合规、长期存储成本和数据迁移灵活性上的优势，往往远远超过节省的那一点运维费用。

**参考来源：**Microsoft Purview Compliance Portal 文档 — Retention Policies and Retention Labels；Microsoft Learn — Litigation Hold in Exchange Online；Microsoft Learn — eDiscovery solutions in Microsoft Purview；NIST SP 800-177 Rev.1 — Trustworthy Email；SEC Rule 17a-4(b)(4) — 17 CFR § 240.17a-4；IETF RFC 5321 — Simple Mail Transfer Protocol；IETF RFC 5322 — Internet Message Format；ISO 15489-1:2016 — Information and documentation — Records management；AIIM — Email Archiving Best Practices and Compliance Standards。

### 相关文章

[邮件归档技术全景](/kb/email-archiving.html)
[邮件归档的法律合规要求](/kb/email-archiving-legal-compliance.html)
[邮件归档的合规保留与自动删除策略](/kb/email-archiving-retention-deletion-strategy.html)
[邮件归档性能优化](/kb/email-archiving-performance-optimization.html)
[邮件归档与 eDiscovery 诉讼保管](/kb/email-archiving-ediscovery-legal-hold.html)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/exchange-online-archive-compliance.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
