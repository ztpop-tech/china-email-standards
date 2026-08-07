---
title: "邮件合规保留策略体系"
source: "https://ztpop.net/kb/email-retention-policies.html"
license: CC-BY 4.0
---

# 邮件合规保留策略体系

邮件合规保留策略体系

摘要：邮件数据的合规管理是现代企业信息系统治理的核心挑战。GDPR 要求企业明确数据保留的必要期限，SOX 法案规定电子通信记录需保留至少 7 年，等保 2.0（GB/T 22239-2019）则要求对邮件进行安全审计和访问控制。本文基于 Exchange 的消息记录管理（Messaging Records Management, MRM）体系，系统解析默认策略标签（DPT）、保留策略标签（RPT）、个人标签的层次化架构，分析保留操作类型的适用场景，厘清诉讼保留（Litigation Hold）与保留策略的互补关系，并给出多法规合规的设计框架。

## 一、MRM 架构与标签类型

消息记录管理（MRM）是 Exchange 内置的邮件生命周期管理框架，通过保留标记（Retention Tags）和保留策略（Retention Policies）定义邮件从创建到永久删除的完整生命周期。MRM 的核心设计哲学是：由管理员定义组织级保留要求，由托管文件夹助理（Managed Folder Assistant, MFA）按计划周期执行清理，将合规要求转化为自动化运维。

MRM 定义了三种保留标记类型，按优先级从高到低排列：

一、MRM 架构与标签类型

| 标记类型 | 作用范围 | 优先级 | 典型场景 |
| 个人标记（Personal Tag） | 用户手动应用到特定邮件/文件夹 | 最高 | 项目合同邮件永久保留、项目结束后 1 年清理 |
| 默认策略标记（DPT：Default Policy Tag） | 整个邮箱所有未标记项 | 次高 | 所有邮件 2 年后移动到存档 |
| 保留策略标记（RPT：Retention Policy Tag） | 特定默认文件夹（收件箱、已删除邮件等） | 最低 | 已删除邮件文件夹中的邮件 30 天后永久删除 |

```
# 创建保留标记
# DPT: 所有邮件 2 年后移动到存档
New-RetentionPolicyTag -Name "Default 2 Year Move to Archive" \
  -Type All -RetentionEnabled $true -AgeLimitForRetention 730 \
  -RetentionAction MoveToArchive

# RPT: 已删除邮件 30 天后永久删除
New-RetentionPolicyTag -Name "Deleted Items 30 Days" \
  -Type DeletedItems -RetentionEnabled $true -AgeLimitForRetention 30 \
  -RetentionAction PermanentlyDelete

# 个人标记: 永久保留（永不删除）
New-RetentionPolicyTag -Name "Never Delete" \
  -Type Personal -RetentionEnabled $true \
  -RetentionAction DeleteAndAllowRecovery -AgeLimitForRetention 3650

# 创建保留策略并关联标记
New-RetentionPolicy -Name "Standard Corporate Policy" \
  -RetentionPolicyTagLinks "Default 2 Year Move to Archive", \
  "Deleted Items 30 Days", "Never Delete"

# 将保留策略应用到邮箱
Set-Mailbox "user@example.com" -RetentionPolicy "Standard Corporate Policy"
```

## 二、保留操作类型详解

保留标记通过 RetentionAction 参数定义达到期限后对邮件的处置方式。Exchange 支持五种保留操作，各自适用于不同的合规和安全需求：

二、保留操作类型详解

| 操作 | 行为 | 可恢复性 | 适用场景 |
| DeleteAndAllowRecovery | 移动到"可恢复项目"文件夹 | 是（取决于可恢复项目保留期） | 常规邮件清理，允许用户或管理员恢复 |
| PermanentlyDelete | 永久清除，不可恢复 | 否 | 高敏感性数据、GDPR"被遗忘权" |
| MoveToArchive | 移动到用户存档邮箱 | 是（存档邮箱中保留） | 主邮箱空间管理，保留用于合规查询 |
| MarkAsPastRetentionLimit | 仅标记为过期，不自动删除 | 是（需手动审查后删除） | 需要人工审批的删除流程 |
| MoveToDeletedItems | 移动到已删除邮件文件夹 | 是（在已删除文件夹中暂时保留） | 温和的过期提醒，用户可选择恢复 |

NIST SP 800-88 Rev.1《介质净化指南》[1] 定义了数据销毁的三个级别：清除（Clear，逻辑删除，数据可通过数据恢复工具恢复）、净化（Purge，物理或逻辑方法使数据无法通过实验室技术恢复）、销毁（Destroy，物理毁坏存储介质）。MRM 的 DeleteAndAllowRecovery 对应清除级别，PermanentlyDelete 对应净化级别（取决于存储层是否启用 BitLocker 加密和卷级安全擦除）。

## 三、保留策略 vs 诉讼保留（Litigation Hold）

保留策略（Retention Policy）和诉讼保留（Litigation Hold）是两种独立的合规机制，服务于不同目的、具有不同的优先级和执行逻辑。

**保留策略：**
基于时间的自动化清理机制——邮件达到预设期限后自动执行保留操作。保留策略由 MFA 按计划周期（通常每天一次）执行，处理逻辑为检查每封邮件的接收/创建日期，计算年龄，匹配优先级最高的保留标记。保留策略是组织日常合规管理的基础层。

**诉讼保留：**
为响应实际或预期的法律诉讼而执行的强制数据保全机制——禁止从邮箱中删除任何数据，即使保留策略规定的期限已过。诉讼保留优先于保留策略——保留策略标记设置为删除的邮件如果处于诉讼保留状态，MFA 不会删除这些邮件。诉讼保留有持续时间（Duration）参数，到期后自动解除。

```
# 对邮箱启用诉讼保留（无限期）
Set-Mailbox "executive@example.com" \
  -LitigationHoldEnabled $true \
  -LitigationHoldDate (Get-Date) \
  -LitigationHoldOwner "Legal Department"

# 对邮箱启用有时限的诉讼保留（5 年）
Set-Mailbox "custodian@example.com" \
  -LitigationHoldEnabled $true \
  -LitigationHoldDuration 1825

# 查询所有处于诉讼保留的邮箱
Get-Mailbox -ResultSize Unlimited | \
  Where {$_.LitigationHoldEnabled -eq $true} | \
  Select DisplayName,LitigationHoldDate,LitigationHoldOwner

# 就地保留（In-Place Hold）——基于查询的保留
New-MailboxSearch "SOX Retention Hold 2026" \
  -SourceMailboxes "finance@example.com" \
  -InPlaceHoldEnabled $true \
  -ItemHoldPeriod Unlimited \
  -SearchQuery "kind:email AND received>=01/01/2023"
```

**就地保留（In-Place Hold）：**
诉讼保留的一个精细化版本，支持基于查询条件的保留——只保留符合指定条件的邮件，而非整个邮箱。例如"保留 2023 年至今 all @supplier.com 的邮件"。就地保留通过 New-MailboxSearch 的 InPlaceHoldEnabled 参数配置，ItemHoldPeriod 设置保留时长。

## 四、多法规合规对齐

### 4.1 GDPR 对齐

GDPR（General Data Protection Regulation）对邮件数据管理提出四项核心要求：(1) 数据最小化（第五条——仅保留业务必要的最短时间）；(2) 被遗忘权（第十七条——用户可要求删除其个人数据）；(3) 可携带权（第二十条——用户可导出其所有邮件数据）；(4) 数据泄露通知（第三十三、三十四条——72 小时内通知监管机构）。

GDPR 对齐的 MRM 设计：设置明确的保留期限（DPT 7 年作为默认值，匹配多数欧洲国家的法定保留要求）；配置 RPT 将已删除邮件文件夹的内容 90 天后 PermanentlyDelete（实现"被遗忘权"的技术落地）；存档邮箱中保留可搜索副本（通过 eDiscovery 执行 GDPR 数据主体请求验证可携带权）。

### 4.2 SOX 法案对齐

萨班斯-奥克斯利法案（SOX）第 802 条要求上市公司保留与审计相关的电子通信记录至少 7 年。SOX 对齐的邮件保留策略需确保：(1) 财务、审计和法务部门用户的所有邮件不可删除（诉讼保留 + DPT 保留至存档）；(2) 日记邮箱（Journaling Mailbox）保存所有入站/出站邮件的不可变副本（日记邮箱禁用所有保留标记，确保日记副本不因 MRM 清理而丢失）；(3) 保留结束后执行 PermanentlyDelete 前必须经过合规团队审批（使用 MarkAsPastRetentionLimit + 手动审批流程）。

### 4.3 等保 2.0（GB/T 22239-2019）对齐

GB/T 22239-2019《信息安全技术 网络安全等级保护基本要求》[2] 第三级安全要求对邮件系统的安全审计和访问控制提出了明确要求：

**安全审计（8.1.3.3）：**
邮件系统的管理员操作和用户关键操作（发送、删除、转发）应产生审计日志并安全存储。Exchange 的管理员审计日志（Admin Audit Log）记录所有 PowerShell 命令执行，邮箱审计日志（Mailbox Audit Log）记录邮箱访问和操作，两类日志均受 MRM 保留策略管理。

**数据完整性与保密性（8.1.4.2）：**
邮件在传输和存储过程中应采取完整性校验和加密措施。保留策略中的存档邮箱应启用 BitLocker 加密，传输中强制 TLS 1.2+。

**数据备份与恢复（8.1.4.5）：**
邮件系统的业务数据和审计日志应定期备份，备份数据保存不少于 6 个月。昆仑邮件系统的 TurboEx 将邮件数据库和审计日志纳入统一备份策略，每日增量备份、每周全量备份，保留周期 12 个月，满足等保 2.0 的备份要求。

## 五、邮件生命周期管理完整架构

企业级邮件生命周期管理需将 MRM、诉讼保留、日记归档和 eDiscovery 四个子系统协同工作：

```
# 1. 配置日记规则（所有邮件不可变副本）
New-JournalRule -Name "SOX Journal" \
  -JournalEmailAddress journal@example.com \
  -Scope Global -Enabled $true

# 2. 日记邮箱禁用所有保留清理
Set-Mailbox journal@example.com \
  -RetentionPolicy $null \
  -RetainDeletedItemsFor 2555

# 3. 配置 eDiscovery 权限
New-ManagementRoleAssignment \
  -Role "Mailbox Import Export" \
  -User "complianceadmin@example.com"

# 4. 创建合规搜索
New-ComplianceSearch -Name "SOX Q2 2026" \
  -ExchangeLocation "finance@example.com","executive@example.com" \
  -ContentMatchQuery "invoice OR contract OR financial report" \
  -StartDate "04/01/2026" -EndDate "06/30/2026"

# 5. 启动托管文件夹助理（手动触发 MRM 处理）
Start-ManagedFolderAssistant -Identity "user@example.com"
```

**抗勒索软删除保护：**
MFA 执行 DeleteAndAllowRecovery 操作时，将邮件移动到"可恢复项目"（Recoverable Items）文件夹的 Deletions 子文件夹中。该文件夹的内容受 Single Item Recovery 保护——即使管理员尝试通过 MFCMAPI 或其他工具直接操作，也必须先禁用该保护。可恢复项目文件夹的保留期（RetainDeletedItemsFor）建议配置为 30 天以上，为检测到勒索软件后恢复邮件提供时间窗口。

## 参考文献

[1] R. Kissel, A. Regenscheid, M. Scholl, K. Stine, "NIST SP 800-88 Rev.1: Guidelines for Media Sanitization," National Institute of Standards and Technology, December 2014.

[2] 全国信息安全标准化技术委员会, "GB/T 22239-2019 信息安全技术 网络安全等级保护基本要求," 国家标准化管理委员会, 2019年5月.

[3] European Union, "Regulation (EU) 2016/679 of the European Parliament and of the Council (General Data Protection Regulation)," Articles 5, 17, 20, 33-34, April 2016.

[4] U.S. Congress, "Sarbanes-Oxley Act of 2002," Section 802, Public Law 107-204, July 2002.

[5] Microsoft Corporation, "Messaging Records Management in Exchange Server," Microsoft Docs, 2025.

[6] J. Klensin, "Simple Mail Transfer Protocol," IETF RFC 5321, October 2008.

了解更多邮件技术实践，请访问知识库或联系

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-retention-policies.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
