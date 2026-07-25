---
title: "Exchange 邮件合规策略跨系统迁移"
source: "https://ztpop.net/kb/exchange-compliance-migration.html"
license: CC-BY 4.0
---

# Exchange 邮件合规策略跨系统迁移

#### 目录

1. [Exchange 合规政策体系全景](#sec1)
2. [MRM 保留策略导出与结构分析](#sec2)
3. [合规标签与分类映射](#sec3)
4. [Journaling 邮箱迁移](#sec4)
5. [合规审计链路的跨系统延续](#sec5)
6. [合规策略验证清单](#sec6)
7. [参考文献](#ref)

## 1. Exchange 合规政策体系全景

Exchange 的邮件合规体系分为三大支柱：**Messaging Records Management（MRM）**负责邮件保留与到期处置，**Journaling（日志记录）**负责邮件副本捕获，**Information Rights Management（IRM）**负责邮件权限保护。这三者共同构成了 Exchange 的合规能力栈。迁移到国产邮件系统时，需要将这三类策略逐一映射。[RFC 7208]

MRM 的核心构件是**保留策略标签（Retention Policy Tag）**，其 XML 定义包含在 Active Directory 的 `msExchMailboxTemplate` 属性中（Exchange 2010 起迁移到 `msExchRetentionPolicyTagLink`）。Exchange 管理控制台（EAC）提供保留标签的可视化管理界面，底层则通过 Exchange PowerShell 操控 AD 对象。[RFC 7001]

> **合规策略管理架构：**Exchange 的合规管理员属于"Records Management"管理角色，可创建/修改/删除保留标签和保留策略。迁移后，国产邮件系统的合规管理员角色应被赋予等效权限，确保合规管理岗位职责在系统切换后继承。

## 2. MRM 保留策略导出与结构分析

在迁移 MRM 保留策略之前，需要完整导出 Exchange 组织的所有保留策略定义。以下命令导出全部保留标签：

```
# 导出所有保留策略标签及其详细属性
$allTags = Get-RetentionPolicyTag -ResultSize Unlimited
$tagReport = @()
foreach ($tag in $allTags) {
    $tagReport += [PSCustomObject]@{
        Name               = $tag.Name
        Type               = $tag.Type
        RetentionAction    = $tag.RetentionAction
        AgeLimitForRetention = $tag.AgeLimitForRetention
        RetentionId        = $tag.RetentionId.Guid
        MessageClass       = $tag.MessageClass
        LocalizedComment   = $tag.LocalizedComment
        SystemTag          = $tag.SystemTag
        IsDefaultTag       = $tag.IsDefaultTag
        IsDefaultAutoGroupTag = $tag.IsDefaultAutoGroupTag
        PolicyName         = ($tag | Get-RetentionPolicy).Name -join "; "
    }
}
$tagReport | Export-Csv -Path mrm_tags_full_export.csv -NoTypeInformation -Encoding UTF8

# 导出每个保留标签的 XML 定义（用于审计）
$allTags | ForEach-Object {
    $outFile = "mrm_xml/$($_.Name).xml"
    $_.OriginatingServer
    $_.Identity
    Get-RetentionPolicyTag -Identity $_.Identity | Format-List | Out-File $outFile -Encoding utf8
}
```

### 2.2 标签结构分析：分类方式

MRM 保留标签分类体系

| 标签类型 | 特性 | 示例 | 迁移策略 |
| Default Policy Tag (DPT) | 作用于整个邮箱，所有未归类文件夹 | 3年自动归档 | → 全局默认归档策略 |
| Retention Policy Tag (RPT) | 作用于特定默认文件夹 | 收件箱7天删除 | → 文件夹绑定策略 |
| Personal Tag | 用户手动标记 | "重要客户"5年 | → 用户自定义标签 |
| Archive Policy | 仅作用于归档邮箱 | 归档7年自动删除 | → 归档存储策略 |

## 3. 合规标签与分类映射

Exchange 支持通过 `Message Classification` 为邮件标注合规分类（例如"客户保密""内部公开""法律诉件"）。这些分类存储在 AD 的 `msExchMessageClassification` 对象中，与 MRM 标签协同工作：分类决定"这封邮件是什么类型"，MRM 标签决定"这封邮件应该保留多久"。

```
# 导出所有邮件分类定义
Get-MessageClassification -ResultSize Unlimited |
    Select-Object Name, DisplayName, SenderDescription, RecipientDescription, Locale, Version |
    Export-Csv -Path message_classifications.csv -NoTypeInformation -Encoding UTF8
```

**映射到国产系统：**国产邮件系统通常不支持"Message Classification + MRM"的双层标签模型。建议的迁移策略是将 Message Classification 转换为国产系统的**邮件标签/标记**功能（如果支持），同时将 MRM 保留标签独立映射为国产系统的保留策略。[RFC 7597]

### 合规标签迁移原则

* **分类与保留解耦：**将 Exchange 中混合的分类+保留标签拆分为"标记"（分类）和"策略"（保留时长），分别映射到国产系统不同模块
* **法务标签优先：**包含法语/合规关键字的分类（如"Attorney-Client Privilege"）应优先建立映射
* **丢失的元数据：**国产系统如果缺乏邮件分类功能，需在邮件头或备注字段中保留原始分类信息
* **标签颜色映射：**Exchange 的标签颜色应尽量在国产系统保留一致的视觉标记

## 4. Journaling 邮箱迁移

Exchange Journaling 是将组织内所有（或指定收件人范围的）收发邮件副本发送到一个或多个专用 Journaling 邮箱的功能。Journaling 分为：**标准 Journaling**（整个组织级别）和**高级 Journaling**（按收件人/通信组筛选）。迁移 Journaling 机制是合规迁移中技术难度最高的部分之一。

### 4.1 导出 Journaling 配置

```
# 导出当前 Journaling 规则
Get-JournalRule | Select-Object Name, JournalEmailAddress,
    Scope, Recipient, Enabled, GloballyUniqueId |
    Export-Csv -Path journal_rules.csv -NoTypeInformation -Encoding UTF8
```

### 4.2 Journaling 替代架构

国产邮件系统通常不支持 Exchange 原生的 Journaling 机制。替代方案有三种：

Journaling 替代方案对比

| 方案 | 实现方式 | 优点 | 缺点 |
| SMTP BCC 路由 | 在 MTA 级为每个出站邮件添加 BCC 到合规邮箱 | 传输层实现，不依赖邮箱系统 | 需要维护 BCC 规则库 |
| 归档网关前置 | 将归档系统作为邮件传输的中继网关 | 独立于邮箱系统 | 增加邮件转发延迟 |
| Milter 插件捕获 | 在 MTA 侧通过 milter 程序捕获邮件副本 | 灵活可编程 | 维护成本较高 |

```
# MTA 级 BCC 实现示例（Postfix content_filter + 自定义脚本）
# /etc/postfix/main.cf
content_filter = smtp:[archive-gateway.domestic.cn]:10025
# 在网关端对入站邮件添加合规 BCC
smtpd_recipient_restrictions =
    check_recipient_access regexp:/etc/postfix/compliance_bcc
    permit_sasl_authenticated
    permit_mynetworks
    reject_unauth_destination

# /etc/postfix/compliance_bcc
/.*@contoso.com/  BCC:compliance-archive@domestic.cn
```

Exchange 的 Journaling 邮件包含一个特殊的"Journal Report"信封头（Content-Type: message/rfc822 的封装），其中包含原始邮件和元数据（发送时间、收件人列表等）。迁移时需确认国产系统的归档系统是否能解析这种封装格式。如果否，需要在导入前对 Journal 邮件进行解封装处理。

## 5. 合规审计链路的跨系统延续

合规审计链路的核心要求是：**邮件从创建到销毁的所有操作都可追溯、不可篡改**。Exchange 通过以下机制实现：

* 管理员操作审计日志（`Admin Audit Log`）— 记录所有 PowerShell/cmdlet 操作
* 邮箱审计日志（`Mailbox Audit Log`）— 记录用户对邮箱的访问、移动、删除等操作
* Journaling 审计 — 记录邮件副本的完整保留过程

### 5.1 导出 Exchange 审计日志

```
# 导出管理员审计日志（近 90 天）
Search-AdminAuditLog -StartDate (Get-Date).AddDays(-90) -EndDate (Get-Date) |
    Export-Csv -Path admin_audit_log_export.csv -NoTypeInformation -Encoding UTF8

# 导出邮箱审计日志配置
Get-Mailbox -ResultSize Unlimited |
    Where-Object {$_.AuditEnabled -eq $true} |
    Select-Object DisplayName, PrimarySmtpAddress,
        AuditAdmin, AuditDelegate, AuditOwner,
        AuditLogAgeLimit |
    Export-Csv -Path mailbox_audit_config.csv -NoTypeInformation -Encoding UTF8
```

### 5.2 国产系统审计配置

迁移后，需要在新系统中重建审计能力。建议的国产系统审计配置参数：

```
# 国产邮件系统审计配置（示例）
audit:
  enabled: true
  # 记录的管理员操作类型
  admin_events:
    - user_create/delete/modify
    - policy_create/modify/delete
    - system_config_change
    - mailbox_search
    - export_operation
  # 记录的用户操作类型
  mailbox_events:
    - mailbox_access
    - message_hard_delete
    - move_to_archive
    - apply_retention_tag
    - folder_permission_change
  # 日志保留时长
  log_retention_days: 365
  # 审计日志不可篡改存储（WORM）
  worm_storage: enabled
  worm_storage_path: /opt/compliance/audit_logs/worm
  # 审计日志定期导出
  export_schedule: daily
  export_target: s3://compliance-bucket/audit-logs/
```

## 6. 合规策略验证清单

完成迁移后，必须验证以下内容：

* **保留策略正确性：**选择 3 个不同保留时长的标签，确认国产系统的到期动作与 Exchange 一致（例如：30天归档策略 → 第31天自动移入归档）
* **Journaling 连续性：**向 Exchange 中最后一个活跃邮箱发送测试邮件，确认国产系统归档网关正确捕获
* **审计链路完整性：**随机抽取 5 条迁移前管理操作，与迁移后操作对比，确认审计记录格式可解析
* **eDiscovery 功能：**在国产系统执行合规搜索，确认搜索结果范围与 Exchange 端一致

### 合规迁移关键指标

* 保留策略标签映射率 ≥ 95%（剩余 ≤5% 为自定义标签，需手动审核）
* Journaling 覆盖率 100%（迁移期间无合规捕获空窗期）
* 审计日志可追溯期 ≥ 源系统保留期
* 合规标签验证抽样通过率 ≥ 99%

## 参考文献

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/exchange-compliance-migration.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
