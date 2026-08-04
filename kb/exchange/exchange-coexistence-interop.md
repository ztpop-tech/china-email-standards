---
title: "Exchange 共存与互操作：混合环境下的邮件路由与目录同步"
source: "https://ztpop.net/kb/exchange-coexistence-interop.html"
license: CC-BY 4.0
---

# Exchange 共存与互操作：混合环境下的邮件路由与目录同步

## 摘要

邮件系统迁移过程中，新旧系统需经历数周至数月的共存期。在此期间，SMTP 邮件流必须在两个系统间正确路由，全局地址列表（GAL）需保持同步，用户的忙/闲状态查询需跨越系统边界。本文详细阐述共享域名邮件路由策略、Accepted Domain 配置差异、LDAP 目录同步方案以及 Free/Busy 跨系统桥接的工程实现。全文引用 RFC 5321（SMTP）、RFC 4791（CalDAV）、RFC 6764（SRV 定位）和 Microsoft Exchange 互操作官方文档。

## 1. 共存架构概述

典型的 Exchange 迁移共存期架构包含三层：

```
                     ┌─────────────────┐
    Internet SMTP ──▶│  邮件安全网关    │
                     └────────┬────────┘
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
    ┌──────────────────┐           ┌──────────────────┐
    │  Exchange (旧)   │◀──SMTP──▶│   新邮件系统      │
    │  用户: A组       │           │   用户: B组       │
    └────────┬─────────┘           └────────┬─────────┘
             │                              │
             └──────── LDAP 同步 ───────────┘
```

## 2. SMTP 共享域名路由

共享域名邮件路由是共存期的核心技术挑战。RFC 5321 §3.7 定义了 SMTP 中继模型，Exchange 通过 Accepted Domain 和 Send Connector 实现共享域名路由。

### 2.1 Accepted Domain 配置

Exchange 接受域有三种类型，在共存场景下有不同含义：

2.1 Accepted Domain 配置

| Accepted Domain 类型 | 行为 | 共存期用途 |
| Authoritative（权威域） | Exchange 认为此域的收件人仅存在于自身组织；无法投递时生成 NDR | 仅 Exchange 用户所在的域 |
| Internal Relay（内部中继） | Exchange 先在自身查找收件人，未找到时转发至配置的中继服务器 | 共享域共存：部分用户在 Exchange，部分在新系统 |
| External Relay（外部中继） | Exchange 不在自身查找收件人，直接转发至中继服务器 | 外部邮件网关/第三方过滤 |

共存期推荐将 Exchange 的共享域配置为 Internal Relay Domain：

```
# Exchange Management Shell — 配置内部中继域
Set-AcceptedDomain -Identity "example.com" -DomainType InternalRelay

# 配置 Send Connector 将未知收件人转发至新邮件系统
New-SendConnector -Name "ToNewMailSystem" \
  -AddressSpaces "example.com" \
  -SmartHosts "newmail.example.com" \
  -SmartHostAuthMechanism None \
  -DNSRoutingEnabled $false
```

### 2.2 共享命名空间路由逻辑

当新邮件服务器收到发往共享域的邮件，同样需要判断收件人位置：

```
# Postfix 共享域路由（transport 表）
# /etc/postfix/transport
example.com   smtp:[exchange.example.com]
# 覆盖：已迁移用户的邮箱通过 LDAP 查询结果路由（不使用 transport）
# 在 main.cf 中配置：
relay_domains = example.com
transport_maps = hash:/etc/postfix/transport
# LDAP 查询判断收件人邮箱归属
virtual_mailbox_domains = example.com
virtual_mailbox_maps = ldap:/etc/postfix/ldap-mailbox.cf
# 未在 LDAP 中命中的收件人自动走 transport 表转发至 Exchange
```

### 2.3 邮件循环防护

共存期必须防止邮件在两个系统间无限循环。Exchange 侧通过 Received 头 X-header 跳数检测实现：

```
# Exchange 传输规则 — 检测邮件循环
# 在 Exchange 传输规则中添加条件：Received 头计数 > N
# 或通过自定义 X-header 标记
New-TransportRule -Name "CoexistenceLoopPrevention" \
  -HeaderContainsMessageHeader "X-Coex-Routed" \
  -HeaderContainsWords "exchange-to-newmail" \
  -SetHeaderName "X-Coex-Count" \
  -SetHeaderValue "2" \
  -RejectMessageReasonText "Mail loop detected"
```

## 3. GAL 同步：LDAP 目录互操作

全局地址列表（GAL）同步确保共存期间用户在撰写邮件时可以检索到对方系统的收件人。Exchange 的 GAL 基于 Active Directory，新邮件系统可能使用 OpenLDAP、389 DS 或自定义目录。

### 3.1 Exchange → 目标系统单向同步

通过 LDAP 查询从 AD 导出 Exchange 收件人信息，写入目标邮件系统目录：

```
# LDAP 查询 Exchange 收件人（匿名绑定）
ldapsearch -H ldap://dc.example.com -x \
  -b "CN=Users,DC=example,DC=com" \
  "(&(objectClass=user)(mail=*))" \
  displayName mail proxyAddresses \
  | tee exchange_users.ldif

# 转换为目标系统联系人格式后导入
# proxyAddresses 中包含 SMTP:user@example.com 格式的主地址
```

### 3.2 双向同步方案

双向同步需要中间同步引擎（如自定义脚本或目录同步工具），核心逻辑：

```
# 双向 GAL 同步伪逻辑
for each record in source_system:
    target_record = lookup(record.email, target_system)
    if not target_record:
        create_contact(target_system, record)
    elif record.modified_time > target_record.modified_time:
        update_contact(target_system, record)

# 反向同理
for each record in target_system:
    source_record = lookup(record.email, source_system)
    if not source_record:
        create_contact(source_system, record)
```

注意：Exchange 侧外部联系人不应覆盖 AD 中的真实用户对象。同步脚本需要区分用户对象（AD user）和联系人对象（AD contact），仅操作联系人。

## 4. Free/Busy 跨系统互操作

日历忙/闲查询是共存期用户体验的关键环节。Exchange 用户发起会议邀请时需查询目标系统中与会者的空闲时段。

### 4.1 Exchange → CalDAV 桥接

RFC 4791 定义了 CalDAV 协议，大多数现代邮件系统支持通过 CalDAV 查询忙/闲信息。Exchange 通过 Availability Service 暴露忙/闲数据。跨系统桥接架构：

```
Exchange (EWS)          Free/Busy 桥接服务器     目标系统 (CalDAV)
     │                         │                        │
     ├──GetUserAvailability──▶ │                        │
     │                         ├──PROPFIND /calendar/──▶ │
     │                         │◀──200 OK (free-busy)─── │
     │◀──AvailabilityResponse──┤                        │
```

在 Exchange 侧配置联合共享（Federation Trust）与可用性地址空间：

```
# Exchange EMS — 配置外部可用性地址空间
Add-AvailabilityAddressSpace -ForestName "newmail.example.com" \
  -AccessMethod OrgWideFB \
  -Credentials $cred

# 设置在目标系统中查询 Free/Busy 的凭据
Set-AvailabilityConfig -OrgWideAccount "fbproxy@example.com"
```

### 4.2 SRV 发现（RFC 6764）

RFC 6764 定义了 CalDAV/CardDAV 服务的 SRV 记录发现机制。目标系统可通过 DNS SRV 记录声明 Free/Busy 端点：

```
# DNS SRV 记录（发至目标系统 DNS 域）
_caldav._tcp.newmail.example.com. 3600 IN SRV 0 1 443 caldav.newmail.example.com.
_carddav._tcp.newmail.example.com. 3600 IN SRV 0 1 443 carddav.newmail.example.com.

# 验证 SRV 记录
dig _caldav._tcp.newmail.example.com SRV
```

## 5. 共享邮箱与公共文件夹过渡

### 5.1 共享邮箱

Exchange 共享邮箱（Shared Mailbox）通过 Full Access / Send As 权限管理。迁移到目标系统后，需转换为 IMAP 共享文件夹或组

* **方案 A：** 将共享邮箱作为独立 IMAP 账户迁移，目标系统创建对应的共享访问权限。
* **方案 B：** 通过 ACL（Access Control List）在 IMAP 层实现共享文件夹。RFC 4314（IMAP ACL）定义了相关标准，Dovecot 等 IMAP 服务器完整支持。

### 5.2 公共文件夹

Exchange 公共文件夹无法直接通过 IMAP 访问（需配置 Public Folder 代理）。迁移步骤：

1. 将 Exchange 公共文件夹内容导出至 PST
2. 转换为 IMAP 层级下的公共文件夹结构
3. 在目标系统创建对等文件夹并设置 ACL

```
# Exchange EMS — 导出公共文件夹
New-PublicFolderMigrationRequest -SourceMailbox "PFMailbox" \
  -TargetMailbox "ExportMailbox"

# 在目标系统 (Dovecot) 创建公共命名空间
# /etc/dovecot/conf.d/10-mail.conf
namespace {
  type = public
  separator = /
  prefix = Public/
  location = maildir:/var/mail/public
}
# 通过 ACL 控制访问
# doveadm acl set -u user@example.com Public/Marketing \
#   group=marketing-team lookup read write-post seen write-deleted insert post expunge create delete admin
```

## 6. 共存期监控与日志

共存期间邮件路由异常可能导致无声邮件丢失。关键监控指标：

```
# Exchange 传输日志检查
Get-MessageTrackingLog -Start (Get-Date).AddHours(-1) \
  -EventId "FAIL" | 
  Select Timestamp, Sender, Recipients, EventData

# SMTP 日志检查（目标系统 /var/log/maillog）
grep "status=bounced\|status=deferred" /var/log/maillog | tail -20

# 队列状态
# Exchange: Get-Queue
# Postfix: mailq | grep -c "^[A-F0-9]"
```

建议在共存期部署邮件流监控探针——每天自动发送测试邮件至两个系统的测试邮箱，验证路由路径与延迟。

本站技术文章采用 CC-BY 4.0 许可，可自由引用，仅需标注来源 [ztpop.net](https://www.ztpop.net)。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/exchange-coexistence-interop.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
