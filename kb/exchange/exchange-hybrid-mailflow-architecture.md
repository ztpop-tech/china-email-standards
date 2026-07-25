---
title: "Exchange混合部署架构与邮件流排错：On-Prem ↔ Exchange Online ↔ 第三方全链路解析"
source: "https://ztpop.net/kb/exchange-hybrid-mailflow-architecture.html"
license: CC-BY 4.0
---

# Exchange混合部署架构与邮件流排错：On-Prem ↔ Exchange Online ↔ 第三方全链路解析

## 一、Exchange Hybrid 邮件流拓扑概览

Exchange Hybrid 部署的核心成果是「统一命名空间」（unified namespace）和「统一目录」（GAL synchronization）。这两者的实现依赖以下组件：

* **混合配置引擎（Hybrid Configuration Wizard, HCW）**：运行在本地 Exchange 2013/2016/2019 服务器上的向导工具，自动配置本地 Exchange 与 Exchange Online 之间的连接器、OAuth 信任关系以及传输设置 [1]。
* **混合传输代理（Hybrid Mail Flow）**：建立在本地 Exchange Transport Service 与 Exchange Online Protection（EOP）之间的 TLS 加密通道。
* **Azure AD Connect / Microsoft Entra Connect**：负责将本地 AD 用户与 Exchange 属性同步至 Microsoft Entra ID。

在标准 Hybrid 配置中，邮件流路径取决于 Centralized Mail Transport（CMT）开关的设置：

**Non-Centralized Transport（非集中式邮件流，默认）**：

```
外部发信 --> MX --> EOP --> 本地邮箱（On-Premises Mailbox）
                         --> Exchange Online 邮箱（Cloud Mailbox）

本地发信 --> 本地 Exchange Hub Transport --> 根据收件人目标路由至 EOP 或本地

外部收信 <-- 本地 Send Connector / EOP 出站 <-- 本地或云端邮箱
```

在 Non-CMT 模式下，Exchange Online 的入站邮件经过 EOP 直接路由至目标邮箱（无论是云端还是本地），不强制经过本地 Exchange 服务器。这种方式优点是邮件路径最短、延迟最低，但对出站邮件流的统一监控不如 CMT 模式。

**Centralized Mail Transport（集中式邮件流）**：

```
外部发信 --> MX --> EOP --> [本地 Exchange Hub Transport] --> 本地 或 云端邮箱

所有云端邮箱的出站邮件 --> EOP --> 本地 Exchange --> 外部
```

在 CMT 模式下，所有发往云端邮箱的入站邮件也先经本地 Exchange 传输服务，再由本地转发至 Exchange Online。所有云端邮箱发出的出站邮件（发往外部）同样先路由至本地 Exchange，再通过本地 Send Connector 外发。CMT 模式的优势在于邮件流监控和合规审核可以统一在本地完成。

## 二、混合邮件流排错：系统性方法

当 Hybrid 邮件流出现异常时，应按照「从外到内」的原则逐层排查：

### 2.1 DNS 层排查

邮件流排错的第一步是验证 DNS 配置的正确性：

```
# 检查 MX 记录指向 EOP
dig MX domain.com +short
# 期望输出: domain-com.mail.protection.outlook.com  （优先值 0）

# 检查 Autodiscover CNAME 或 SRV
dig CNAME autodiscover.domain.com +short
# 期望指向 autodiscover.outlook.com

# 检查 SPF 记录包含 Exchange Online
dig TXT domain.com +short | grep "spf1"
# 期望包含 include:spf.protection.outlook.com
```

常见问题：MX 记录未指向 EOP（而是指向了旧的邮件服务器或第三方网关），导致发往云端邮箱的邮件被错误路由。

### 2.2 连接器层排查

HCW 创建了两个关键的连接器：

* **入站连接器（Inbound Connector）**——在 Exchange Online 端创建，标识来自本地 Exchange 的入站邮件。通过 `Get-InboundConnector -Identity "Inbound from %Server%"` 查看配置。
* **出站连接器（Outbound Connector）**——在 Exchange Online 端创建，将发往本地邮箱的邮件路由至本地 Exchange 服务器。通过 `Get-OutboundConnector -Identity "Outbound to %Server%"` 查看配置。

典型问题排除：

```
# Exchange Online PowerShell
# 检查入站连接器 TLS 证书主题
Get-InboundConnector | fl Name,TlsSettings,TlsDomain,SenderDomains

# 检查出站连接器路由目标
Get-OutboundConnector | fl Name,SmartHosts,UseMxRecord

# 检查是否启用了 Centralized Mail Transport
Get-HybridConfiguration | fl Features
```

### 2.3 传输服务层排查

连接到本地 Exchange 服务器的邮件队列是排查的核心数据源：

```
# Exchange Management Shell
# 查看所有传输队列状态
Get-Queue -Server ex2019-hybrid | fl Identity,MessageCount,Status,NextHopDomain

# 查看具体队列中的卡住邮件
Get-Message -Queue "ex2019-hybrid\Submission" | fl Subject,FromAddress,InternetMessageId,Sender

# 查看传输服务日志的最后 50 行
Get-MessageTrackingLog -Start "07/24/2026 8:00:00 AM" -End "07/24/2026 12:00:00 PM" -ResultSize 50 | fl Timestamp,EventId,Source,Recipients
```

### 2.4 协议层调试

当怀疑是 SMTP 协议层面的问题（协商失败、证书不匹配、协议版本不兼容）时，开启增强协议日志：

```
# 本地 Exchange 启用协议日志
Set-ReceiveConnector "Default SERVERNAME" -ProtocolLoggingLevel Verbose

# 模拟 SMTP 会话测试
$ telnet mail.domain.com 25
EHLO test
# 检查 250-STARTTLS
# 检查 250-AUTH LOGIN
```

## 三、常见邮件流中断场景与解决方案

| 症状 | 可能原因 | 诊断命令/方法 | 解决方案 |
| --- | --- | --- | --- |
| 发往云端邮箱的邮件在本地队列中卡住 | 出站连接器 SmartHosts 配置错误或 TLS 证书不匹配 | `Get-OutboundConnector | fl SmartHosts,TlsDomain` | 更新出站连接器的 SmartHosts 值，确认 TlsDomain 匹配 EOP 终结点 |
| 本地用户无法发送邮件到云端用户 | 混合配置中的 Organizational Relationships 未正确配置 | `Get-OrganizationRelationship | fl Name,Enabled,TargetApplicationUri,TargetAutodiscoverEpr` | 重新运行 HCW 或手动修复 OrganizationRelationship |
| 云端用户收到退回邮件 554 5.4.1 | 本地 Send Connector 的 Address Space 未覆盖收件域 | `Get-SendConnector | fl Name,AddressSpaces` | 为目标域添加 Send Connector Address Space |
| 邮件路由到 EOP 后进入循环 | Hybrid mail flow misconfiguration（两条连接器互指） | 检查 Inbound/Outbound Connector 的 SmartHosts 是否指向自身 | 重建连接器，确保 Outbound Connector 的 SmartHosts 指向本地 Exchange IP/FQDN |
| 云端到本地的邮件延迟 > 30 分钟 | TLS 协商频繁失败引起重试回退 | 查看 MessageTrackingLog 中的 DELIVERFAIL 事件 | 检查本地 Exchange 的 TLS 证书是否过期；检查端点间防火墙 25/TCP 端口是否稳定 |
| OAuth 认证失败导致邮件退回 | Entra ID 中的应用注册证书/密钥过期 | `Test-OAuthConnectivity -Service EWS` | 更新本地 Exchange 和 O365 之间的 OAuth 证书 |

## 四、混合 SMTP 网关场景：Exchange Online ↔ 第三方邮件系统

在混合部署后期或过渡方案中，部分组织可能需要在 Exchange Online 与第三方邮件系统（如国产邮件平台、Google Workspace）之间维持邮件流。这种场景下邮件流路径变为：

```
外部 --> MX --> EOP --> [SMTP 网关/连接器] --> 第三方邮件系统

第三方 ---[SMTP relay/gateway]---> EOP ---> Exchange Online
```

实现要点：

* 在 Exchange Online 中为第三方域创建额外的入站/出站连接器，指定 SMTP 网关地址（非 EOP）[2]。
* 在第三方邮件系统中配置出站中继（Smart Host），将发往云端用户的邮件路由至 EOP（`domain-com.mail.protection.outlook.com`）。
* 确保第三方邮件系统支持 STARTTLS（RFC 3207），否则连接器配置中的 TLS 要求将导致邮件被拒收。

**⚠️ 注意：**在多系统共存邮件流场景下，SPF 记录的 include 语句需要同时包含 EOP 和第三方网关的出站 IP 范围。缺少任一 SPF include 都可能导致 DMARC 失败，进而影响送达率。

## 五、邮件跟踪与日志分析工具链

Hybrid 部署的邮件跟踪通常需要跨平台协作：

* **本地 Exchange**：`Get-MessageTrackingLog` cmdlet 提供按时间、事件类型、发送/接收者的日志查询能力。日志存储在 Exchange 安装目录的 TransportRoles/Logs/MessageTracking 下。
* **Exchange Online**：[Exchange admin center (EAC) Message Trace](https://admin.exchange.microsoft.com/#/mailflow) 提供基于 GUI 的邮件跟踪。建议将日志自留存周期从默认 30 天延长至 90 天以满足合规要求。
* **SMTP 握手日志**：对特定域启用 SMTP 协议日志（Set-ReceiveConnector / Set-SendConnector -ProtocolLoggingLevel Verbose），详细记录 EHLO 命令到 QUIT 的完整会话过程 [5]。

在排错方法论上，遵循以下优先级路径：

1. 确认发件人/收件人邮箱位置（本地 or 云端）→ 决定邮件流应走哪条路径
2. 检查连接器配置（Inbound/Outbound Connector）是否正确创建且状态为 Enabled
3. 查看队列（Get-Queue）和卡住邮件（Get-Message）→ 判断是路由问题还是身份验证问题
4. 查看消息跟踪日志（Get-MessageTrackingLog）的 EventId 链：RECEIVE → SUBMIT → SEND/DELIVER → DELIVERFAIL → 判断是传输服务内部还是外部原因
5. 对 TLS/Auth 问题，启用详细协议日志并执行测试 SMTP 会话（telnet 或 openssl s\_client）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/exchange-hybrid-mailflow-architecture.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
