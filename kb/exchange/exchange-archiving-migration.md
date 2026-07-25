---
title: "Exchange 邮件归档策略迁移指南"
source: "https://ztpop.net/kb/exchange-archiving-migration.html"
license: CC-BY 4.0
---

# Exchange 邮件归档策略迁移指南

#### 目录

1. [Exchange 归档体系概述](#sec1)
2. [Exchange 原生归档 vs 第三方归档](#sec2)
3. [保留策略映射：MRM → 国产邮件系统](#sec3)
4. [法务 Hold 与 eDiscovery 迁移](#sec4)
5. [归档数据迁移技术方案](#sec5)
6. [迁移验证与回滚策略](#sec6)
7. [参考文献](#ref)

## 1. Exchange 归档体系概述

Exchange 邮件归档体系经历了三个发展阶段：**Managed Folders（ELC, Exchange 2007）**→ **Messaging Records Management（MRM, Exchange 2010+/Exchange Online）**→ **统一归档 + 法务 Hold（Exchange Online 现代体系）**。

Exchange 原生归档的核心机制基于**受管理内容设置（Managed Content Settings）**和**保留策略标签（Retention Policy Tag, RPT）**。自 Exchange 2010 起，MRM 引入了保留策略（Retention Policy）概念，每个邮箱可关联一个策略，策略内包含多个保留标签，每个标签定义一段邮件在该标签下的保留时长和到期动作（Delete / Archive / Permanently Delete）。[RFC 6376][RFC 7489]

> **关键概念：**保留策略标签分为三类：默认策略标签（Default Policy Tag, DPT）作用于整个邮箱；保留策略标签（RPT）作用于特定默认文件夹（收件箱、已发送等）；个人标签（Personal Tag）允许用户手动应用。到期动作为 MoveToArchive 或 DeleteAndAllowRecovery / PermanentlyDelete。

第三方归档方案（如 Veritas Enterprise Vault、Mimecast、Barracuda Cloud Archiving）则采用"日志捕获"或"邮箱爬取"模式。日志捕获通过 Journaling 邮箱接收组织所有收发邮件副本；邮箱爬取通过 EWS（Exchange Web Services）周期遍历用户邮箱归档旧邮件。第三方归档系统独立存储索引数据，保留策略在其内部独立管理，与 Exchange MRM 形成两套并行的保留生命周期[RFC 5322]。

## 2. Exchange 原生归档 vs 第三方归档

归档架构对比

| 维度 | Exchange 原生归档 (MRM) | 第三方归档方案 |
| 存储位置 | Exchange 数据库内（归档邮箱） | 独立存储（NAS / S3 / 云存储） |
| 索引引擎 | Exchange Search Index | 独立搜索引擎 (如 Veritas Index) |
| 策略执行点 | 邮箱助理 (Mailbox Assistant) 周期性执行 | 归档代理或日志传送机制 |
| 用户可见性 | Outlook 在线存档可见 | 归档加签 / Outlook 插件 |
| 法务 Hold | In-Place Hold / Litigation Hold | 独立 Freeze 机制 |
| 跨系统迁移难度 | 高（MRM 标签体系私有） | 中（可导出 PST 或 EML） |

**对迁移的关键影响：**Exchange 原生归档将归档邮箱存储在同一个 Exchange 组织内，数据库（EDB）中归档项与活跃项通过"邮件类型"属性区分。这意味着迁移到国产邮件系统时，需要一并迁移归档邮箱内容，且必须保留"归档"的元数据标记。对于第三方归档方案，数据通常以 PST 或原始 EML 格式导出，国产邮件系统的导入难度取决于其 API 兼容性[RFC 6857]。

## 3. 保留策略映射：MRM → 国产邮件系统

Exchange MRM 的保留标签包含三个核心属性：`RetentionId`（GUID）、`AgeLimitForRetention`（保留天数）、`RetentionAction`（到期动作）。国产邮件系统普遍采用基于**分类 + 期限 + 动作**的保留策略模型，两者之间存在直接的映射关系。

### 策略映射要点

* **DPT → 默认归档策略：**Exchange 的默认策略标签映射为国产系统的"全局默认归档策略"，适用于所有用户的未归类邮件。
* **RPT → 文件夹级别覆盖：**Exchange 的文件夹级保留标签映射为国产系统的"文件夹绑定策略"，仅作用于特定 IMAP 文件夹。
* **Personal Tag → 用户自定义策略：**映射为用户可自行选择的应用级策略或手动归档标记。
* **MoveToArchive → 自动归档：**映射为国产系统自动将超过 N 天的邮件移入归档存储。
* **DeleteAndAllowRecovery → 可恢复删除：**映射为保留在"已删除邮件"区域并可恢复（类似 Exchange 的 Deleted Item Retention）。
* **PermanentlyDelete → 不可恢复删除：**直接映射为彻底删除（需合规审批流以避免合规风险）。

### 3.1 实际命令：导出 Exchange MRM 策略

```
# 使用 Exchange PowerShell 导出当前组织的所有保留策略
Get-RetentionPolicy | ForEach-Object {
    $policy = $_
    $tags = Get-RetentionPolicyTag -Mailbox $_.DistinguishedName | Where-Object {$_.Type -eq "All"}
    $tags | ForEach-Object {
        [PSCustomObject]@{
            PolicyName   = $policy.Name
            TagName      = $_.Name
            TagType      = $_.Type
            RetentionAge = $_.AgeLimitForRetention.Days
            Action       = $_.RetentionAction
            Comment      = $_.Comment
        }
    }
} | Export-Csv -Path retention_policy_export.csv -NoTypeInformation -Encoding UTF8
```

### 3.2 策略映射转换表

MRM 保留动作 → 国产系统映射

| Exchange MRM 动作 | 等效国产系统动作 | 注意事项 |
| MoveToArchive | 移至归档存储 | 需确认国产系统归档路径是否支持分层存储 |
| DeleteAndAllowRecovery | 软删除（保留 N 天可恢复） | Exchange 默认保留期 14 天，建议迁移时保留该参数 |
| PermanentlyDelete | 彻底删除（不可恢复） | 建议迁移前由法务重新评审合规必要性 |
| MarkAsPastRetentionLimit | 标记为过期（保留不动） | Exchange 特有动作，国产系统多数不支持，建议改为 Archive |

## 4. 法务 Hold 与 eDiscovery 迁移

Exchange 的法务保留（Legal Hold）分为两种模式：**Litigation Hold**（邮箱级）和 **In-Place Hold**（查询级，Exchange 2013+）。Litigation Hold 启用后，用户修改和删除的邮件均被保留到"可恢复项"文件夹的 Purges 子文件夹中，由系统写保护。In-Place Hold 则基于特定查询条件（日期范围、发件人、关键词），仅保留匹配的邮件项。

**迁移挑战：**国产邮件系统多数不支持"按查询条件 Hold"的精细化保留机制。建议的策略是：在 Exchange 端导出 Hold 查询范围的邮件列表，在国产系统中为这些邮件打上"法务保留"标签，并设置**写保护**策略禁止用户硬删除。具体流程如下：

```
# 导出处于 Litigation Hold 的用户列表
Get-Mailbox -ResultSize Unlimited | Where-Object {$_.LitigationHoldEnabled -eq $true} |
    Select-Object DisplayName, PrimarySmtpAddress, LitigationHoldDate, LitigationHoldOwner |
    Export-Csv -Path litigation_hold_users.csv -NoTypeInformation -Encoding UTF8

# 导出 In-Place Hold 的定义（Exchange 2013+）
Get-MailboxSearch | Where-Object {$_.InPlaceHoldEnabled -eq $true} |
    Select-Object Name, TargetMailboxes, SearchQuery, StartDate, EndDate, Description |
    Export-Csv -Path inplace_hold_export.csv -NoTypeInformation -Encoding UTF8
```

在国产邮件系统中创建等效法务保留时，建议将 In-Place Hold 的 SearchQuery 作为补充说明记录，而非强制在国产系统中实现全文检索过滤（多数国产系统不具备此引擎）。法务团队需重新评估 Hold 覆盖范围。

## 5. 归档数据迁移技术方案

归档数据迁移有三种技术路径：

### 5.1 PST 导出/导入（通用方案）

使用 Exchange 原生工具 `New-MailboxExportRequest` 将邮箱（含归档）导出为 PST，再使用国产邮件系统的 PST 导入工具恢复。此方案适用于中规模迁移（单邮箱 <50GB），但 PST 格式对大邮件量环境性能不足。

```
# 导出主邮箱和归档邮箱到一个 PST
New-MailboxExportRequest -Mailbox user01 -FilePath "\\fileserver\pst\user01.pst"
New-MailboxExportRequest -Mailbox user01 -FilePath "\\fileserver\pst\user01_archive.pst" -IsArchive
```

### 5.2 IMAP 同步（无损迁移）

通过 IMAP 协议从 Exchange 同步归档文件夹。Exchange 归档邮箱通过 Outlook 在线存档功能暴露 IMAP 访问。国产邮件系统若支持 IMAP 归档文件夹，可进行文件夹级同步。此方案保留文件夹结构和邮件属性，但丢失 MRM 标签元数据。

```
# 使用 imapsync 同步归档文件夹
imapsync --host1 exchange.contoso.com --user1 user01 --authuser1 admin@contoso.com \
         --host2 mail.domestic.cn --user2 user01 --authuser2 admin@domestic.cn \
         --ssl1 --ssl2 --no-modseq --folder "Archive" --folder "Archive/Inbox" \
         --folder "Archive/Sent Items" --exclude "Archive/Deleted Items" \
         --useuid --noregexmess
```

### 5.3 第三方归档迁移（委托导出）

对于 Veritas Enterprise Vault、Mimecast 等第三方归档方案，通常可以按用户导出归档内容为 EML/PST 格式，再通过标准导入工具迁移。部分第三方归档系统提供 REST API 用于批量导出。迁移前需确认归档系统是否已将过期数据清除，建议在源系统执行一次归档完整性验证。

```
# 从 EV PST 导出目录批量导入
for user in $(cat user_list.txt); do
    curl -X POST "https://api.domestic.cn/v1/import/pst" \
         -H "Authorization: Bearer ${API_KEY}" \
         -F "file=/exports/${user}.pst" \
         -F "target_user=${user}@domestic.cn" \
       --connect-timeout 30 --max-time 3600
done
```

## 6. 迁移验证与回滚策略

归档迁移成功后，必须执行以下验证：

* **数量校验：**对比 Exchange 端归档邮件总数与国产系统归档邮件数，误差应 <0.1%
* **随机样本检查：**每个邮箱抽取归档文件夹中 3-5 封邮件验证附件完整性、日期、发件人信息
* **法务 Hold 验证：**确认法务 Hold 用户在国产系统中无法删除已标记为"法务保留"的邮件
* **过期策略验证：**确认国产系统到期删除/归档策略生效时间符合预期

### 归档迁移清单

* ☐ 导出所有 Exchange 保留策略定义（CSV）
* ☐ 导出 Litigation Hold / In-Place Hold 用户和定义
* ☐ 编制策略映射表（MRM 动作 → 国产系统动作）
* ☐ 按数据量决定迁移路径（PST / IMAP / API）
* ☐ 执行 POC 迁移（3-5 个代表性邮箱）
* ☐ 验证归档邮件完整性
* ☐ 上线前同步一次增量（镜像最后一次更改）
* ☐ 监控国产系统归档存储水位 72 小时

## 参考文献

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/exchange-archiving-migration.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
