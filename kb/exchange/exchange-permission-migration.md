---
title: "Exchange 权限管理向国产邮件系统迁移"
source: "https://ztpop.net/kb/exchange-permission-migration.html"
license: CC-BY 4.0
---

# Exchange 权限管理向国产邮件系统迁移

#### 目录

1. [Exchange RBAC 模型解析](#sec1)
2. [核心管理角色映射表](#sec2)
3. [AD 安全组同步策略](#sec3)
4. [ACL 权限矩阵转换](#sec4)
5. [邮箱级别权限（FullAccess/SendAs）迁移](#sec5)
6. [迁移验证与审计](#sec6)
7. [参考文献](#ref)

## 1. Exchange RBAC 模型解析

Exchange 2010 起引入基于角色的访问控制（RBAC）模型，替代了 Exchange 2007 的管理角色管理模型。RBAC 的核心由四个层次构成：**管理角色（Management Role）**→ **管理角色项（Role Entry）**→ **管理角色分配（Role Assignment）**→ **分配策略（Assignment Policy）**[RFC 5398]。

每一层的作用域范围进一步通过**管理作用域（Management Scope）**控制，包括独占作用域（Exclusive Scope）和常规作用域（Regular Scope），实现精细的 OU/Server/数据库级权限隔离。这种粒度在国产邮件系统中通常不可直接复制，需要重新设计权限层级[RFC 5593]。

> **理解 Exchange RBAC：**Management Role 定义了"可以做什么"，Management Scope 定义了"可以对谁做"。例如"Recipient Administrators"角色可以对"contoso.com/Sales OU"范围内的收件人进行操作。Role Assignment 将角色+作用域绑定到安全组或用户。

## 2. 核心管理角色映射表

Exchange 管理角色 → 国产邮件系统映射

| Exchange 管理角色 | 国产系统等效角色 | 差距分析 |
| Organization Management | 系统管理员/超级管理员 | 基本 1:1 对应 |
| Recipient Management | 用户管理员 | 国产系统缺少"通讯组管理"分解 |
| Server Management | 系统运维管理员 | 国产系统通常无"服务器级"权限概念 |
| View-Only Organization Management | 审计管理员 | 国产系统只读角色通常更粗粒度 |
| Discovery Management | 合规搜索管理员 | 部分国产系统未实现 |
| Records Management | 归档管理员 | 需确认归档功能是否独立 |
| Mailbox Search | 邮件搜索角色 | 国产系统权限模型可能不同 |
| Transport Management | 邮件流管理员 | 国产系统多数无此独立角色 |

### 2.1 导出 Exchange 角色分配清单

```
# 导出所有管理角色分配
Get-ManagementRoleAssignment | ForEach-Object {
    [PSCustomObject]@{
        Name            = $_.Name
        Role            = $_.Role
        RoleAssignee    = $_.RoleAssignee
        AssignmentMethod = $_.AssignmentMethod
        RecipientReadScope   = $_.RecipientReadScope
        RecipientWriteScope  = $_.RecipientWriteScope
        ConfigWriteScope     = $_.ConfigWriteScope
        IsValid               = $_.IsValid
    }
} | Export-Csv -Path role_assignments.csv -NoTypeInformation -Encoding UTF8

# 导出自定义角色定义
Get-ManagementRole | ForEach-Object {
    $entries = Get-ManagementRoleEntry $_.Identity
    [PSCustomObject]@{
        RoleName = $_.Name
        RoleType = $_.RoleType
        RoleEntries = ($entries.Name -join "; ")
    }
} | Export-Csv -Path custom_roles.csv -NoTypeInformation -Encoding UTF8
```

中文邮件系统（如 \u56fd\u4ea7\u90ae\u4ef6\u7cfb\u7edf、安宁邮件、昆仑邮件系统 等）的管理权限模型通常分为"系统管理员""部门管理员""安全审计员"三层，与 Exchange 的 70+ 角色粒度差距明显。迁移策略应以"角色合并"为原则，将多个 Exchange 细粒度角色合并为国产系统的一个粗粒度角色，同时在岗位说明文档中记录原有细化权限边界。

## 3. AD 安全组同步策略

Exchange 将管理权限分配给 AD 安全组（Universal Security Groups）而非单用户，以支持组继承和审批流转。迁移到国产邮件系统后，AD 同步策略需做如下调整：

### 3.1 原有 Exchange 管理安全组

```
# 列出所有 Exchange 管理安全组（类似以下命名模式）
Get-Group -ResultSize Unlimited |
    Where-Object {$_.GroupType -eq "UniversalSecurity" -and $_.Name -like "*Exchange*"} |
    Select-Object Name, SamAccountName, DistinguishedName, Members |
    Export-Csv -Path exchange_admin_groups.csv -NoTypeInformation -Encoding UTF8
```

### 3.2 国产邮件系统管理组创建

建议在国产邮件系统中创建与 Exchange 管理安全组等效的本地管理组。组映射规则如下：

AD 安全组 → 国产系统组映射

| Exchange 管理组 | 国产系统目标组 | 成员同步方式 |
| Exchange Org Admins | admin\_super\_admin | 手动 + LDAP 同步 |
| Exchange Recipient Admins | admin\_user\_admin | 来自 AD 组递归展开 |
| Exchange View-Only Admins | admin\_auditor | 来自 AD 组递归展开 |
| Exchange Server Operators | admin\_ops | 来自 AD 组递归展开 |
| Exchange Discovery Admins | admin\_compliance (自定义) | 如有等效权限 |

### 3.3 LDAP 组同步配置示例

```
# 国产邮件系统 LDAP 同步配置（示例 yml 格式）
ldap_sync:
  enabled: true
  server: ldap://dc01.contoso.com:389
  base_dn: "OU=Security Groups,OU=Exchange Migration,DC=contoso,DC=com"
  sync_groups:
    - name: admin_super_admin
      filter: "(cn=OrgAdmins*)"
      role: super_admin
    - name: admin_user_admin
      filter: "(cn=RecipientAdmins*)"
      role: user_admin
    - name: admin_auditor
      filter: "(cn=ViewOnlyAdmins*)"
      role: auditor
  sync_interval: 300   # seconds
```

## 4. ACL 权限矩阵转换

Exchange 的 ACL（Access Control List）权限矩阵涵盖**邮箱级权限**（FullAccess、SendAs、SendOnBehalf）和**公共文件夹权限**。国产邮件系统的 ACL 模型通常基于 IMAP ACL（RFC 4314）扩展，权限粒度为：`lrsxtikpa`（Lookup/Read/Seen/Write/Insert/Create/Delete/Admin）。[RFC 4314]

Exchange 邮箱权限 → IMAP ACL 映射

| Exchange 权限 | IMAP ACL 等效 | 说明 |
| FullAccess | `lrswipkxte` | 除 Admin 外全部 |
| Read Permission | `lrs` | 仅阅读 |
| Reviewer (公共文件夹) | `lr` | 查找+阅读 |
| Contributor (公共文件夹) | `ip` | 插入+发布 |
| Editor | `lrswip` | 读写基本操作 |
| Owner | `lrswipkxte a` | 全部权限（含管理） |

```
# 提取邮箱 FullAccess/SendAs 权限
$mailboxes = Get-Mailbox -ResultSize Unlimited
$results = @()
foreach ($mbx in $mailboxes) {
    $perms = Get-MailboxPermission -Identity $mbx.Identity |
             Where-Object {!$_.IsInherited -and $_.User -like "nt authority*"}
    $sendAs = Get-RecipientPermission -Identity $mbx.Identity |
              Where-Object {!$_.IsInherited}
    $results += [PSCustomObject]@{
        Mailbox    = $mbx.DisplayName
        User       = $perms.User.UserName -join "; "
        AccessRights = $perms.AccessRights -join "; "
        SendAsUsers  = $sendAs.Trustee -join "; "
    }
}
$results | Export-Csv -Path mailbox_permissions.csv -NoTypeInformation -Encoding UTF8
```

Exchange 的 SendAs 权限在 IMAP ACL 中没有直接对应项。在国产邮件系统中，这通常需要**身份后门（alias mapping）**或**代理发送**功能实现。建议建立 SendAs 清单作为迁移后功能验证的强制检查项。

## 5. 邮箱级别权限（FullAccess/SendAs）迁移

邮箱级别权限迁移分为三步：

### 5.1 导出 Exchange 权限基线

```
# 批量导出所有邮箱权限
$users = Get-Mailbox -ResultSize Unlimited
$permReport = @()
foreach ($u in $users) {
    $mbxPerms   = Get-MailboxPermission -Identity $u.Identity | Where-Object {$_.User -notlike "NT AUTHORITY*" -and $_.User -notlike "S-1-*"}
    $recvPerms  = Get-RecipientPermission -Identity $u.Identity | Where-Object {$_.Trustee -notlike "NT AUTHORITY*"}
    $sendOnBehalf = $u.GrantSendOnBehalfTo
    $permReport += [PSCustomObject]@{
        Mailbox        = $u.DisplayName
        PrimarySMTP    = $u.PrimarySmtpAddress
        FullAccessUsers   = ($mbxPerms | Where-Object {$_.AccessRights -like "*FullAccess*"} | %{$_.User}) -join "|"
        SendAsUsers       = ($recvPerms | Where-Object {$_.AccessRights -eq "SendAs"} | %{$_.Trustee}) -join "|"
        SendOnBehalfUsers = ($sendOnBehalf) -join "|"
    }
}
$permReport | Export-Csv -Path full_mailbox_permissions.csv -NoTypeInformation -Encoding UTF8
```

### 5.2 在国产系统中重建权限

编写迁移脚本逐邮箱重建权限。注意：SendAs 权限在国产系统中的实现方式可能完全不同（如代理邮箱、别名映射等），需提前与系统厂商确认。

```
#!/bin/bash
# 批量恢复 FullAccess 权限（示例 API 调用）
CSV_FILE="full_mailbox_permissions.csv"
API_ENDPOINT="https://mail.domestic.cn/api/v1/set-acl"
API_KEY="${DOMESTIC_API_KEY}"

tail -n +2 "${CSV_FILE}" | while IFS=, read mailbox smtp fullaccess sendas sendbehalf; do
    # 设置 FullAccess = IMAP ACL lrswipkxte
    IFS='|' read -ra USERS <<< "$fullaccess"
    for delegate in "${USERS[@]}"; do
        if [ -n "$delegate" ]; then
            curl -s -X POST "${API_ENDPOINT}" \
                -H "Authorization: Bearer ${API_KEY}" \
                -H "Content-Type: application/json" \
                -d "{\"mailbox\":\"${smtp}\",\"user\":\"${delegate}\",\"rights\":\"lrswipkxte\"}"
        fi
    done
done
```

## 6. 迁移验证与审计

权限迁移完成后，必须执行以下验证步骤：

* **角色验证：**每个被委派管理角色的用户测试其操作边界，确认无法越权
* **FullAccess 验证：**授权用户可打开目标邮箱阅读邮件
* **SendAs 验证：**授权用户能以目标邮箱身份成功发信（接收方显示为被代理邮箱）
* **安全组一致性：**确认国产系统中管理组与 AD 组中成员列表一致
* **ACL 矩阵完整性：**随机抽样 10 个邮箱确认 ACL 权限正确

### 权限迁移核心原则

* 先导出再映射：一次性导出 Exchange 完整权限快照，建立映射表后再实施
* 最小权限：借迁移之机收敛过度授权的用户（常见于 FullAccess 授权泛滥）
* SendAs 特殊处理：国产系统中 SendAs 机制差异最大，预留额外测试时间
* 保留权限基线：迁移后保留 Exchange 端权限快照 ≥3 个月，用于审计追踪

## 参考文献

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/exchange-permission-migration.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
