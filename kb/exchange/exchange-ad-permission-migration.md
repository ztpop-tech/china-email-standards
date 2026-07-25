---
title: "Exchange 权限与 AD 迁移技术指南：RBAC/ACL/Security Group 迁移策略与验证"
source: "https://ztpop.net/kb/exchange-ad-permission-migration.html"
license: CC-BY 4.0
---

# Exchange 权限与 AD 迁移技术指南：RBAC/ACL/Security Group 迁移策略与验证

## 一、Exchange 权限体系中的三支柱

理解 Exchange 权限体系是设计和执行迁移方案的前提。三根支柱的具体形式如下：

### 1.1 RBAC — 管理角色分配

Exchange 2010 之后彻底从组织单位（OU）级别的权限管理升级为 RBAC 模型。管理角色（Management Role）通过管理角色分配策略（Management Role Assignment Policy）绑定到用户或安全组。

```
# 查看所有管理角色分配
Get-ManagementRoleAssignment | fl Name,Role,User,AssignmentMethod,RecipientWriteScope

# 查看特定用户的有效权限
Get-ManagementRoleAssignment -GetEffectiveUsers -Role "Mail Recipients" | fl EffectiveUserName,AssignmentMethod
```

RBAC 有两大作用域：配置作用域（Configuration Write Scope）定义角色在服务器、数据库级别的操作范围；收件人作用域（Recipient Write Scope）定义在哪个 OU/Unit 中的收件人受到影响。迁移时需要导出的核心信息包括：角色分配列表、自定义角色定义（自定义的 Management Role）、作用域规则。

### 1.2 AD ACL — 邮箱级权限

Mailbox 级权限——如 Full Access（完全访问）、Send-As（代表发送）、Send on Behalf（代表发送）——由 AD 用户属性中的 ACL（Security Descriptor）存储。

```
# 查看特定邮箱的权限
Get-MailboxPermission -Identity user@domain.com | ft User,AccessRights,IsInherited,Deny

# 查看 Send-As 权限
Get-RecipientPermission -Identity user@domain.com | ft Trustee,AccessRights

# 查看 Send on Behalf 权限
Get-Mailbox -Identity user@domain.com | fl GrantSendOnBehalfTo

# ADSI Edit 中查看用户对象属性
# msExchDelegateListLink, msExchMailboxSecurityDescriptor, publicDelegates
```

Send-As 权限（允许用户以邮箱所有者的身份发送邮件）是最容易被忽视的权限维度。它通过 `ms-Exch-SMTP-Send-As` 扩展权限在 AD 中实现。在迁移过程中，如果国产邮件系统没有对应的 Send-As 实现机制，需要使用共享邮箱或委托发送功能来等效替代。

### 1.3 Security Group — 基于组的授权

Exchange 使用安全组进行大规模权限分配。关键类型：

* **Role Group**：Exchange 内置的管理员组，如 Organization Management（组织管理）、Server Management（服务器管理）、Recipient Management（收件人管理）。
* **Distribution Group**：通讯组，同时可作为安全主体，用于批量授权（Grant-ADPermission）。
* **Universal Security Group (USG)**：用于发布 Exchange 管理角色分配的 AD 安全组。

由于国产邮件系统使用独立的权限模型（通常为内置角色 + 管理域），迁移的核心挑战是将 Exchange 的自定义角色映射到目标平台的等效角色。

## 二、AD LDS 与目录同步方案

AD Lightweight Directory Services（AD LDS）是 AD 的一个轻量级目录服务角色，不依赖域名 DNS 和域控制器架构，可以作为用户属性的中间存储——保留 Exchange 权限相关属性（如 msExch\* 属性、delegation 信息）供目标邮件系统查询。

### 2.1 AD LDS 同步架构

```
[Active Directory（源）]
    |  LDAP 同步 (LDIFDE / ADSync)
    v
[AD LDS 实例（中间件）]
    |  属性映射 / 自定义同步脚本
    v
[国产邮件系统 AD（目标）]
    |
[国产邮件平台（权限评估）]
```

同步频率取决于组织规模和权限变更频率。建议：

* 全量同步：首次部署时执行一次
* 增量同步：每 5-15 分钟执行一次（通过 AD LDS 的 Change Notification 或自定义定时脚本）
* 权限验证：每 24 小时执行一次（对比源端与目标端的权限清单）

### 2.2 通过 LDIFDE 导出权限信息

LDIFDE（LDAP Data Interchange Format Data Exchange）是 Windows Server 自带的目录服务导出工具，可将 AD 对象导出为 LDIF 格式文件：

```
# 导出管理角色分配信息
ldifde -f role-assignments.ldf -s dc01.domain.com -d "CN=RBAC,CN=Microsoft Exchange,CN=Services,CN=Configuration,DC=domain,DC=com" -r "(objectClass=*)" -l "name,msExchRoleLink,msExchRole*"

# 导出邮箱权限相关属性
ldifde -f mailbox-permissions.ldf -s dc01.domain.com -d "DC=domain,DC=com" -r "(&(objectClass=user)(msExchMailboxSecurityDescriptor=*))" -l "distinguishedName,msExchMailboxSecurityDescriptor,msExchRecipientTypeDetails"
```

导出的 LDIF 文件包含二进制格式的安全描述符（Security Descriptor），需要定制解析脚本（使用 C# 或 Python 调用 System.DirectoryServices 命名空间）将二进制 SDDL 转换为可读的权限陈述。

### 2.3 自定义同步工具架构

对于大规模部署（>5000 用户），建议开发或采购基于 LDAP 的定制同步工具：

* **读取阶段**：通过 ADSI 或 LDAP 连接到源端 AD，通过 `Get-MailboxPermission`/`Get-RecipientPermission`/`Get-ManagementRoleAssignment` 命令获取完整的权限清单。
* **映射阶段**：将 Exchange 角色映射到目标平台的内置角色模型。示例映射表：`Organization Management` → `系统管理员`；`Recipient Management` → `邮箱管理员`；`View-Only Organization Management` → `审计员`；自定义角色 → 按权限类型逐个映射。
* **写入阶段**：通过目标平台的 LDAP 或 REST API 写入用户权限和委托设置。

## 三、Send-As 与 FullAccess 权限的等效实现

Send-As 和 FullAccess（完全控制）是 Exchange 迁移中最难以 1:1 复现的权限类型，因为它们在国产邮件系统中没有原生等价物。以下是等效策略方案：

| Exchange 权限 | 目标平台等效实现 | 用户影响 |
| --- | --- | --- |
| FullAccess（完全控制权限） | 1) 在目标平台中创建共享邮箱，将源端 FullAccess 受托者设为该共享邮箱的完全控制方；2) 或授予用户相同名称的邮箱的管理员权限 | 用户可能需要重新登录以获取新权限 |
| Send-As（代表发送） | 1) 目标平台中启用委托发送（Delegate Send），在发件人显示为原邮箱地址的同时标记「代表」字样；2) 或创建共享邮箱为代发专用 | 发件人显示的「代表」标记可能不同于 Exchange 行为 |
| Send on Behalf（代表发送） | 目标平台直接支持此功能（大多数国产邮件系统支持），权限映射相对直接 | 无变化 |
| 邮箱文件夹级权限 | 目标平台通过 IMAP ACL（RFC 4314）或专有文件夹共享机制实现 | 需逐箱配置，建议只在迁移后按需补配 |

对于 Send-As 权限，建议按照以下优先级迁移：

1. **服务账号/系统邮箱**：直接在目标平台中配置为等效的技术帐户。
2. **高管/管理助理路径**：配置委托发送（Delegate Send）——高管邮箱由助理代理发送。
3. **共享邮箱场景**：将共享邮箱在目标平台中重建，并授予 Send-As 对应人员邮箱权限。

## 四、迁移后权限验证与修复流程

权限迁移完成后，验证步骤不应被视为「一次性测试」，而应成为持续运营的一部分。建议执行以下验证计划：

### 4.1 自动化验证脚本

开发自动化脚本将源端权限清单与目标端权限清单逐一匹配：

```
# 在 Exchange 2013 上导出全量权限清单
$mailboxes = Get-Mailbox -ResultSize Unlimited
$exportPath = "C:\Exports\permission-audit-$(Get-Date -Format yyyyMMdd).csv"

$results = @()
foreach ($mailbox in $mailboxes) {
    $mbPerm = Get-MailboxPermission -Identity $mailbox.Identity | Where-Object {$_.User -notlike 'NT AUTHORITY\*' -and $_.User -notlike 'S-1-5-21*'
    $recipPerm = Get-RecipientPermission -Identity $mailbox.Identity
    # 输出到 CSV 供对比
    $results += [PSCustomObject]@{
        Mailbox = $mailbox.UserPrincipalName
        FullAccessUsers = ($mbPerm | Where-Object {$_.AccessRights -eq 'FullAccess'}).User -join ';'
        SendAsUsers = ($recipPerm | Where-Object {$_.AccessRights -eq 'SendAs'}).Trustee -join ';'
    }
}
$results | Export-Csv $exportPath -NoTypeInformation
```

### 4.2 差异分析步骤

1. 从源端 Exchange 导出权限 CSV（包含邮箱地址、受托者、权限类型）
2. 从目标邮件系统导出用户权限清单
3. 逐行比对：对每个邮箱，验证每个源端受托者在目标端是否有对应的权限映射
4. 对差异项进行分级：关键差异（FullAccess/Send-As 缺失）→ 优先修复；非关键差异（文件夹级权限）→ 按需补配

建议在迁移后第 1、3、7、30 天各执行一次全量差异分析，确保没有遗漏。

### 4.3 修复流程

当源端与目标端权限不一致时，分级修复策略：

| 优先级 | 权限类型 | 修复方式 |
| --- | --- | --- |
| P0（24h 内修复） | FullAccess、Send-As | 管理员手动配置等效权限 |
| P1（72h 内修复） | Send on Behalf、Delegate Access | 通过 API 或管理控制台批量配置 |
| P2（7 天内修复） | 文件夹级 ACL、自定义角色映射偏差 | 用户报告后按需修复 |

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/exchange-ad-permission-migration.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
