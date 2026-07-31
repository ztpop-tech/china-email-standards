---
title: "Exchange 数据迁移操作流程：从全量到增量的无感迁移实践"
source: "https://ztpop.net/kb/exchange-data-migration-procedure.html"
license: CC-BY 4.0
---

# Exchange 数据迁移操作流程：从全量到增量的无感迁移实践

#### 📑 目录

1. [背景：Exchange EOL 驱动下的迁移窗口](#s1)
2. [迁移目标与分层需求](#s2)
3. [迁移流程总览（七阶段框架）](#s3)
4. [第一阶段：原系统评估与资产盘点](#s4)
5. [第二阶段：目标系统部署与环境准备](#s5)
6. [第三阶段：全量数据迁移](#s6)
7. [第四阶段：增量同步](#s7)
8. [第五阶段：DNS 切换与割接](#s8)
9. [第六阶段：共存期运行与监控](#s9)
10. [第七阶段：下线旧系统与归档](#s10)
11. [关键技术要点：断点续传、去重校验与性能优化](#s11)
12. [常见问题与对策](#s12)

## 一、背景：Exchange EOL 驱动下的迁移窗口

Microsoft 已正式宣布 Exchange Server 2016 和 Exchange Server 2019 的主流支持截止日期为 **2025 年 10 月 14 日**（详见 [Microsoft Lifecycle Policy](https://learn.microsoft.com/en-us/lifecycle/products/exchange-server-2019)）。在此日期之后，Microsoft 将不再为这些版本提供常规安全更新和非安全热修复程序，仅可能提供受限的扩展安全更新（ESU）。

对于运行 Exchange 多年的中大型组织而言，这并非简单的版本升级问题，而是一次**邮件基础设施的整体迁移契机**。这类组织通常面临以下现实：

* **历史数据体量巨大**：数 TB 级邮件数据，部分用户邮箱超过 50 GB，迁移窗口有限
* **业务连续性要求高**：邮件是核心办公工具，不能接受超过数小时的停机
* **用户无感要求**：迁移过程不应要求最终用户提供密码、重新配置客户端或手动导入数据
* **合规与审计需求**：历史邮件必须完整保留，包括原始邮件的所有元数据（时间戳、发件人、收件人、Message-ID 等）

> **关键时间节点：**Exchange 2016/2019 EOL 日期为 2025 年 10 月 14 日。对于计划迁移到国产邮件系统的组织，建议至少提前 6–12 个月启动评估和迁移项目，以确保在 EOL 前完成切换并留出充足的共存验证期。

## 二、迁移目标与分层需求

一次成功的 Exchange 数据迁移需要满足两个层次的需求：**基础数据完整性** 和 **应用功能提升**。

### 2.1 基础要求 — 完整迁移历史数据

* **全量数据迁移**：Exchange 运行多年积累的数 TB 历史邮件、日历、联系人、任务和便签，必须在影响最小的前提下平滑迁移至目标邮件系统
* **无感迁移**：整个迁移过程中，不需要最终用户提供密码——迁移通过管理员权限在服务端完成，用户仅在切换后感知到新系统
* **海量异构数据支持**：T 级以上数据量、不同用户间的异构邮件结构（嵌套附件、内嵌图片、RTF/HTML/纯文本混合格式），均需保持完整性
* **数据一致性保证**：迁移后的邮件数量、文件夹结构、已读/未读状态、标记/旗标状态需与源系统一致

### 2.2 核心需求 — 提升应用与性能

* **功能对等覆盖**：新系统需完整提供原 Exchange 所有核心功能：邮件收发与管理、日历/会议邀请、全局/个人通讯录、任务管理、移动端（ActiveSync/IMAP）兼容
* **性能瓶颈突破**：解决旧系统在以下方面的性能问题 —— 大邮箱搜索速度（Exchange 本地搜索在 50 GB+ 邮箱上常需数十秒）、WebMail 大附件上传、并发用户访问时延
* **智能化能力补充**：新增 AI 辅助功能（如智能分类、自动摘要、邮件优先级识别）、全文检索引擎（毫秒级海量邮件搜索）、多语言翻译集成等原 Exchange 不具备的现代化功能

迁移不只是一次数据搬移，更是邮件基础设施的**升级换代**。在规划阶段就应明确新系统需要比旧系统"多出什么"，而不是简单的一比一对等替换。

## 三、迁移流程总览（七阶段框架）

Exchange 数据迁移遵循分阶段推进原则，每一阶段都有明确的输入输出和验收标准。以下为全流程框架：

Exchange 数据迁移七阶段流程概览

| 阶段 | 核心任务 | 关键交付物 | 预计耗时 |
| --- | --- | --- | --- |
| **1. 原系统评估** | 导出 Exchange 用户列表、邮件组、权限结构、存储使用量；识别 SMTP 中继客户端和集成系统 | 资产清单、数据量评估报告 | 1–2 周 |
| **2. 目标系统部署** | 安装配置新邮件系统、网络打通、域名验证、SSL/TLS 证书部署 | 系统部署确认书、网络拓扑图 | 1–3 周 |
| **3. 全量数据迁移** | 从运维后台发起全量迁移，支持断点续传和重复校验 | 迁移进度报告、数据校验报告 | 1–4 周（取决于数据量） |
| **4. 增量同步** | 捕获全量迁移之后的增量变化，进行二次导入 | 增量同步差异报告 | 1–2 天 |
| **5. DNS 切换与割接** | MX 记录指向新系统，旧系统设为中继转发；Autodiscover 更新；客户端配置推送 | 割接方案 + 回退预案 | 1 个变更窗口 |
| **6. 共存期运行** | 新旧并行 7–30 天，监控投递成功率、用户反馈、异常日志 | 共存期日报、监控大盘 | 1–4 周 |
| **7. 下线旧系统** | 确认无遗留数据后关闭 Exchange 服务器，PST 归档，更新 CMDB | 下线确认单、归档完成确认 | 1–2 周 |

## 四、第一阶段：原系统评估与资产盘点

评估是迁移项目的**基石**——不充分的前期评估是迁移延期的首要原因。评估需要产出的核心信息包括：

### 4.1 用户清单与存储使用量

Exchange 管理员可通过以下 PowerShell 命令导出全量用户邮箱统计：

```
# 导出所有用户邮箱的存储使用量、邮件数量、最后登录时间
Get-Mailbox -ResultSize Unlimited |
  Get-MailboxStatistics |
  Select-Object DisplayName, ItemCount,
    @{N="SizeMB";E={[math]::Round($_.TotalItemSize.Value.ToMB(),2)}},
    LastLogonTime |
  Export-Csv -Path "C:\Reports\MailboxReport.csv" -NoTypeInformation -Encoding UTF8
```

评估的关键指标：

* **总用户数**和**活跃用户数**（基于 LastLogonTime 筛选）
* **总数据量**（TB 级别需提前评估存储和网络迁移承载能力）
* **大邮箱用户分布**：识别邮箱超过 20 GB 的"重负载用户"，单独规划迁移策略
* **共享邮箱和资源邮箱**：会议室、设备邮箱、共享邮箱的数量和权限配置

### 4.2 邮件组与权限结构

```
# 导出所有通讯组及成员
Get-DistributionGroup -ResultSize Unlimited |
  ForEach-Object {
    $dg = $_
    Get-DistributionGroupMember -Identity $dg.Identity |
      Select-Object @{N="Group";E={$dg.DisplayName}},
        @{N="Member";E={$_.DisplayName}},
        @{N="MemberType";E={$_.RecipientType}}
  } |
  Export-Csv -Path "C:\Reports\DGMembers.csv" -NoTypeInformation -Encoding UTF8
```

**动态通讯组**（Dynamic Distribution Group）需特别关注——它基于 LDAP 查询条件动态生成成员列表，大多数目标邮件系统不支持等效机制。迁移前应使用脚将其当前成员导出并转为静态组，或评估目标系统是否支持 LDAP 过滤规则。

### 4.3 SMTP 中继客户端识别

这是**最容易被遗漏的环节**。Exchange 部署多年后，组织中常存在大量未被文档化的"幽灵中继"：

* 监控系统（如 Zabbix、Prometheus Alertmanager）通过 Exchange 发送告警
* 打印机的扫描到邮件功能
* ERP / CRM / OA 系统通过 Exchange SMTP 中继发送报表和通知
* 内部应用系统的邮件发送接口

建议在评估阶段使用 Exchange 的**消息跟踪日志**（Message Tracking Log）统计所有出站连接的源 IP：

```
# 获取过去 30 天内所有 SMTP 连接的源 IP 统计
Get-MessageTrackingLog -Start (Get-Date).AddDays(-30) -EventId RECEIVE |
  Where-Object { $_.Source -eq "SMTP" } |
  Group-Object ClientHostname, ClientIP |
  Select-Object Count, Name |
  Sort-Object Count -Descending |
  Export-Csv "C:\Reports\SMTPClients.csv" -NoTypeInformation -Encoding UTF8
```

> **实践提示：**迁移期间，任何一个被遗漏的中继客户端都可能在割接后造成业务中断。建议在资产盘点阶段逐一确认：每个 IP 对应的业务系统、维护负责人、是否需要在目标系统中重新配置中继授权。

## 五、第二阶段：目标系统部署与环境准备

### 5.1 服务器部署与网络规划

目标邮件系统的部署需遵循以下原则：

* **高可用架构**：至少部署 2 个以上节点（主备或多活），前端部署负载均衡（如 HAProxy / Nginx Stream），确保任意单节点故障不影响服务
* **网络可达性**：确保目标邮件系统与 Exchange 服务器之间网络畅通（内网互通或 VPN），迁移数据流量优先走内网而非公网
* **防火墙规则**：开放必要的 SMTP（25/TCP）、IMAP（143/TCP 或 993/TCP）、HTTP/HTTPS（80/443/TCP）端口
* **存储规划**：根据评估阶段的数据量，预留不少于当前数据量 1.5 倍的存储空间（含增量增长和索引空间）

### 5.2 域名与证书配置

* **域名验证**：在目标系统中添加并验证组织域名（通过 DNS TXT 记录或 HTTP 验证）
* **SSL/TLS 证书**：部署通配符证书或多 SAN 证书，覆盖 `mail.yourdomain.com`、`autodiscover.yourdomain.com`、`imap.yourdomain.com`、`smtp.yourdomain.com`
* **邮件认证记录**：预先配置 SPF（RFC 7208）、DKIM、DMARC（RFC 7489）记录，确保新系统的出站邮件不会被拒收

### 5.3 IMAP 协议连接配置

大多数迁移工具基于 IMAP 协议（RFC 3501）实现数据迁移。需在 Exchange 端确认以下配置：

* IMAP4 服务已启动（默认在 Exchange 2013+ 中为手动启动）
* IMAP 端口（993/TCP for SSL, 143/TCP for STARTTLS）已在防火墙放行
* 迁移专用管理员账号拥有 `ApplicationImpersonation` 角色（EWS 迁移）或 `Receive-As` 权限（IMAP 迁移）

```
# Exchange 端启用 IMAP4 服务
Set-Service MSExchangeIMAP4 -StartupType Automatic
Start-Service MSExchangeIMAP4

# 创建迁移专用管理员并授予 ApplicationImpersonation 角色
New-ManagementRoleAssignment -Name "MigrationImpersonation" `
  -Role ApplicationImpersonation -User "migration_admin@yourdomain.com"
```

## 六、第三阶段：全量数据迁移

### 6.1 迁移发起方式

全量迁移通过**邮件系统运维后台**直接发起，无需终端用户参与。运维管理员在后台配置以下信息后即可启动批量迁移任务：

* 源服务器地址（Exchange IMAP/EWS 端点）
* 迁移范围（全部用户 / 指定 OU 分组 / 按 CSV 列表）
* 迁移内容（邮件 / 日历 / 联系人 / 任务 / 便签）
* 并发控制参数（最大并发用户数、带宽限制阈值）

### 6.2 断点续传机制

TB 级别的数据迁移不可能一次完成且不发生任何中断。断点续传是全量迁移的**核心保障能力**：

* 每个用户邮箱的迁移进度（已成功同步的邮件 Message-ID 列表 + 文件夹结构快照）持久化存储在迁移任务状态数据库中
* 当迁移因网络中断、服务器重启或人工暂停而中止时，恢复后从最近检查点继续，**不重传已完成的邮件**
* 检查点粒度建议为**单用户级别**——即完成一个用户后再标记其状态为 "已完成"，失败用户单独重试队列

### 6.3 重复校验（Message-ID 去重）

根据 RFC 5322（Internet Message Format）Section 3.6.4，每封标准邮件都有一个全局唯一标识符 `Message-ID`。迁移系统的去重逻辑基于此标准实现：

* 导入每封邮件前，先在目标系统中查询该 `Message-ID` 是否已存在
* 若已存在且邮件正文哈希值一致，则跳过（**幂等导入**）
* 若已存在但正文内容不一致（极少数情况，如同主题的转发/回复可能产生相同 Message-ID，违反 RFC 规范），则以源系统为准覆盖

```
# 伪代码：迁移去重逻辑
def should_skip_email(message_id, content_hash, target_system):
    existing = target_system.lookup_by_message_id(message_id)
    if existing is None:
        return False  # 新邮件，需要导入
    if existing.content_hash == content_hash:
        return True   # 已存在且一致，跳过
    # 内容不一致，覆盖导入（并记录告警日志）
    log.warning(f"Message-ID collision: {message_id}")
    return False
```

去重机制带来的关键好处：

* **可重复执行**：全量迁移脚本可在任意阶段重新运行而不会产生重复邮件
* **断点续传的基础**：续传时无需关心哪些已导入，直接按 Message-ID 去重即可
* **冲突检测**：发现异常 Message-ID 冲突时生成运维告警

### 6.4 迁移性能优化

全量迁移性能关键配置

| 配置项 | 推荐值 | 说明 |
| --- | --- | --- |
| 并发用户数 | 50–200 | 取决于源服务器 IMAP 会话并发能力；过高会触发 Exchange 的 IMAP 连接限制 |
| 单用户并发线程 | 4–8 | IMAP 协议支持多线程拉取不同文件夹 |
| 带宽上限 | 500 Mbps–1 Gbps | 避免迁移流量挤占正常业务带宽 |
| 批量提交大小 | 每批 100–500 封 | 减少目标系统的索引压力；过大批次会导致单次事务超时 |
| 源端限速 | 启用 Exchange 策略 | 通过 Exchange 限流策略保护源服务器性能 |

## 七、第四阶段：增量同步

全量迁移通常需要数天到数周（取决于数据量）。在此期间，用户仍在 Exchange 上正常收发邮件，产生了**全量迁移窗口内的增量数据**。增量同步的目的是捕获这些变化。

### 7.1 增量同步策略

* **基于 IMAP UID 的增量检测**：IMAP 协议为每个邮箱内的邮件分配递增的唯一 ID（UID）。迁移系统记录最后一次同步时的最大 UID，增量同步时仅拉取 UID 大于该值的邮件（见 RFC 3501 Section 2.3.1.1）
* **文件夹结构变化检测**：增量同步时对比文件夹层次结构（新创建、删除、重命名的文件夹）
* **日历与联系人的增量检测**：对日历事件和联系人，使用其元数据中的 `LastModifiedTime` 或 `ETag` 值进行增量识别

```
# IMAP UID 增量伪代码
last_uid = migration_state.get_last_uid(user_mailbox)
new_messages = imap.fetch(f"UID {last_uid + 1}:*")
for msg in new_messages:
    import_to_target(msg)
migration_state.update_last_uid(user_mailbox, max_uid_of_batch)
```

### 7.2 增量同步执行时机

* **首次增量**：全量迁移完成后的 24 小时内执行，捕获全量窗口内的增量
* **割接前增量**：在 DNS 切换前的数小时内执行最后一次增量同步，确保切换间的数据差最小
* **割接后增量**（可选）：割接后可能仍有少量邮件投递到旧系统（由于 DNS 传播延迟），割接后 24 小时再执行一次增量同步以补全

> **应用实践：**理想的增量同步窗口应控制在 30 分钟以内。如果某用户的增量邮件超过数千封（如群发列表邮件），可将其列入单独的重试队列，优先完成普通用户的增量同步。

## 八、第五阶段：DNS 切换与割接

### 8.1 割接前准备

* **MX 记录 TTL 提前降低**：在割接前至少 24 小时，将 MX 记录的 TTL 从常规的 3600 秒降低到 300 秒（5 分钟）。这确保割接时 DNS 变更能在 5 分钟内传播生效，而非数小时
* **Autodiscover CNAME 准备**：若使用 Outlook 客户端，提前准备好 `autodiscover.yourdomain.com` 的 CNAME 记录更新（指向新邮件系统的自动发现端点）
* **SRV 记录准备**（如适用）：部分客户端通过 `_autodiscover._tcp.yourdomain.com` 的 SRV 记录定位自动发现服务

### 8.2 割接操作步骤

1. **DNS MX 记录切换**：将 MX 记录优先级指向新邮件系统的 SMTP 入口（如 `10 mail-new.yourdomain.com`），保留旧 Exchange 为更低优先级的中继备份（如 `20 mail-old.yourdomain.com`）
2. **旧系统设为中继转发**：在 Exchange 端配置发送连接器（Send Connector），将发往本域用户但尚未迁移的邮件中继到新系统。参考 RFC 5321 Section 3.7（Relaying）
3. **Autodiscover 切换**：更新 `autodiscover.yourdomain.com` 的 DNS 记录指向新系统
4. **客户端配置更新**：通过 GPO 或 MDM 策略批量更新 Outlook 客户端配置，或引导用户重启客户端以自动发现新服务器
5. **验证投递通路**：从外部邮箱（如 Gmail）发送测试邮件到组织域，确认能正确投递到新系统；从新系统发送邮件到外部邮箱，确认 SPF/DKIM/DMARC 检查通过

### 8.3 回退预案

割接必须配备**完整的回退预案**：

* MX 记录回滚：将优先级恢复为割接前的配置
* 在割接窗口中，保留旧 Exchange 服务器的完整运行状态（不卸载、不修改核心配置）
* 提前准备回退后手动迁移割接期间邮件到原系统的脚本（保证无邮件丢失）
* 定义回退触发条件：如投递成功率低于 95%、关键用户报告无法收发邮件、新系统出现严重故障

## 九、第六阶段：共存期运行与监控

### 9.1 共存期配置

共存期（Coexistence Phase）是新旧系统**并行运行**的阶段，持续时间建议为 7–30 天。核心配置包括：

* **SMTP 路由双向配置**：新系统将未识别用户的邮件中继到 Exchange；Exchange 将已迁移用户的邮件中继到新系统。两边都需要正确的 TLS 证书配置以保证传输加密
* **地址簿同步**：保持新系统中的通讯录与 AD/Exchange 同步。此阶段不应因为通讯录信息缺失影响用户使用
* **共享忙闲状态互通**（Free/Busy Interop）：若组织的部分用户暂未迁移，确保新旧系统间的日历忙闲状态可以相互查询

### 9.2 监控指标体系

共存期关键监控指标

| 指标 | 健康阈值 | 监控方式 |
| --- | --- | --- |
| 外部邮件投递成功率 | ≥ 99.5% | SMTP 日志分析 / 邮件流监控面板 |
| 内部邮件路由延迟 | < 30 秒 | 探针邮件监测 |
| 新系统 WebMail 响应时间 | P95 < 2 秒 | APM / 前端性能监控 |
| 用户报障率 | < 1% 用户/天 | IT 服务台工单统计 |
| 旧系统中继队列长度 | < 100 封 | Exchange 队列查看器 |
| 新系统 SMTP 队列长度 | < 500 封 | Postfix / 邮件系统队列面板 |

### 9.3 共存期日报

共存期内，运维团队应每日产出或自动化生成包含以下内容的日报：

* 过去 24 小时邮件总量（入站/出站/内部）
* 投递失败邮件数量和 Top 5 失败原因
* 新系统服务健康状态（CPU / 内存 / 磁盘 / 队列）
* 用户工单统计（数量、类型分布、平均解决时间）
* 次日工作计划（如需处理异常、优化配置等）

## 十、第七阶段：下线旧系统与归档

当共存期监控指标持续满足标准 7 天以上，且无任何遗留数据或功能依赖后，可以启动下线流程。

### 10.1 下线前置确认清单

* 所有用户已成功迁移至新系统（零遗留）
* 所有 SMTP 中继客户端已切换至新系统
* 所有集成系统的邮件接口已更新为新系统的 SMTP 端点
* 邮件流监控确认连续 7 天无邮件经过旧 Exchange 服务器
* 所有动态邮件组已完成转换并在新系统中验证可用
* 共享邮箱和资源邮箱已在新系统中配置并正常工作

### 10.2 归档策略

在物理关闭 Exchange 服务器之前，建议做最后一次数据归档：

* **全量 PST 导出**：将所有用户邮箱导出为 PST 文件（使用 `New-MailboxExportRequest`），存储到归档 NAS 或对象存储中
* **日志归档**：导出并压缩 Exchange 的 IIS 日志、SMTP 协议日志、消息跟踪日志，保留合规归档期（通常 1–7 年）
* **配置导出**：导出 Exchange 的组织配置（`Get-OrganizationConfig`、发送连接器、接收连接器、地址策略等）为文档，留存备查

```
# Exchange 端批量导出所有用户邮箱为 PST
$mailboxes = Get-Mailbox -ResultSize Unlimited
foreach ($mb in $mailboxes) {
    $exportRequest = New-MailboxExportRequest `
      -Mailbox $mb.Identity `
      -FilePath "\\NAS\PSTArchive\$($mb.Alias).pst"
    Write-Host "Export initiated: $($mb.DisplayName)"
}
```

### 10.3 正式下线

1. 关闭 Exchange 的所有邮箱数据库
2. 停止 Exchange 相关服务（Transport、IIS、IMAP、POP3）
3. 观察 48–72 小时，确认无因旧系统掉线引发的报障
4. 物理下线 / 重装操作系统（如硬件回收）
5. 更新 CMDB、监控系统（移除旧服务器监控项）
6. 更新网络拓扑文档和运维手册

## 十一、关键技术要点：断点续传、去重校验与性能优化

### 11.1 断点续传的工程实现

断点续传是全量迁移可靠性的核心。一个健壮的实现需要包含以下组件：

* **迁移状态数据库**：持久化存储每个用户的迁移状态（进行中 / 已完成 / 失败）、最后同步时间戳、最后同步的 IMAP UID、同步完成的消息计数
* **检查点粒度**：以用户为单位，完成一个用户后立即标记状态并写入数据库——而非等待整批用户完成后统一标记
* **失败重试队列**：单用户迁移失败不影响整体进度。失败用户自动进入重试队列，按指数退避策略重试（1 分钟 → 5 分钟 → 15 分钟 → 1 小时）
* **手动暂停/恢复**：运维管理员可在业务高峰期手动暂停迁移任务，低峰期恢复，所有状态由状态数据库保证

### 11.2 去重校验的边界情况

Message-ID 去重是标准的、可靠的，但需注意以下边界情况：

* **非标准邮件**：某些内部系统生成的邮件可能不包含 Message-ID 头。此时退化为（发件人 + 时间戳 + 主题 + 正文哈希）组合键进行去重
* **草稿邮件**：草稿邮件的 Message-ID 可能在每次编辑时重新生成。迁移时应单独处理草稿文件夹，使用最后修改时间戳作为去重辅助
* **Sent Items 与 Inbox 中的同一邮件**：BCC 抄送给自己的邮件可能同时出现在已发送和收件箱中。同一 Message-ID 在**不同文件夹**中出现是正常的，应保持分别导入

> **参考标准：**IMAP 迁移的基础协议为 RFC 3501（IMAP4rev1）。IMAP 扩展机制参见 RFC 8478（Zimbra 反向代理扩展），IMAP ACL 权限模型参见 RFC 4314，SMTP 传输协议参见 RFC 5321。邮件消息格式中的 Message-ID 定义参见 RFC 5322 Section 3.6.4。

### 11.3 迁移工具选型参考

迁移工具的选型取决于组织的技术栈和数据量：

* **开源工具**：`imapsync`（Perl 实现，支持 IMAP 到 IMAP 的完整同步，社区活跃，单机迁移速率约 1–5 GB/小时/用户）——适合中小规模和定制化需求
* **EWS 迁移工具**：基于 Exchange Web Services（EWS）协议的工具可实现更高的迁移速度（多线程并发、MAPI 属性完整保留），适合大规模企业迁移
* **运维后台内置工具**：目标邮件系统运维后台通常提供内置迁移模块，集成度高、运维友好，推荐作为首选方案

## 十二、常见问题与对策

### 12.1 迁移速度慢

**现象：**单用户迁移速率低于 1 GB/小时，全量迁移预计耗时数月。

**原因分析：**

* Exchange IMAP 服务的连接数或速率被限制（默认策略较保守）
* 网络链路带宽不足或延迟高（跨地域迁移）
* 目标系统的邮件索引写入成为瓶颈
* 大量小邮件（< 10 KB）——每封邮件的 IMAP 命令开销（FETCH + APPEND）远大于数据传输

**对策：**

* 调整 Exchange IMAP 连接限制策略：提高 `MaxConnections` 和 `MaxCommandSize`
* 为迁移流量分配独立网卡或 VLAN，避免与生产流量竞争
* 在目标系统中临时降低邮件索引优先级或暂停非核心索引任务，迁移完成后再全量重建
* 对大邮件用户（如 50 GB+）使用 EWS 协议替代 IMAP，减少协议开销

### 12.2 大附件迁移失败

**现象：**含大于 30 MB 附件的[邮件迁移](/kb/category/migration-ecosystem.html)失败或超时。

**对策：**

* 调整 IMAP 消息大小限制（Exchange 端 `MaxReceiveSize`、目标系统端 `message_size_limit`）
* 实施附件外链化策略：超过阈值（如 10 MB）的附件转为可共享链接，邮件正文仅包含下载链接（参考 RFC 6570 URI Template、RFC 8187 MIME 参数字符集）
* 对超大附件使用分段传输（IMAP LITERAL+ 扩展，RFC 2088）

### 12.3 字符编码乱码

**现象：**迁移后部分邮件主题或正文中文乱码。

**原因：**Exchange 中部分历史邮件使用了非标准字符编码（如 GB2312 而非 UTF-8），或 MIME 头中的编码声明与实际不符。

**对策：**

* 在迁移工具中启用字符集自动检测（chardet 库）作为 MIME 声明的补充
* 对检测失败的邮件，以 UTF-8 作为回退编码并记录在异常日志中
* 对识别为 GBK/GB2312 的邮件，显式转换为 UTF-8 后导入（RFC 3629 UTF-8 标准）

### 12.4 用户密码问题

**现象：**IMAP 迁移需用户密码，但安全策略不允许收集密码。

**对策：**

* 使用 `ApplicationImpersonation` 角色授权迁移专用管理员账号（EWS 方式），无需用户密码即可访问所有用户邮箱
* 或使用 Kerberos 委派（对于 AD 环境）实现服务到服务的无密码认证
* 若必须使用 IMAP，可通过 Exchange 管理角色临时重置用户密码为随机值，迁移完成后强制用户首次登录改密（体验差，不推荐）

### 12.5 迁移后邮件顺序错乱

**现象：**目标系统中某文件夹的邮件排序与原系统不同。

**原因：**邮件的 `INTERNALDATE`（IMAP 内部日期）在迁移过程中未正确保留。

**对策：**

* IMAP APPEND 命令可携带日期参数：`APPEND INBOX "15-Jul-2023 10:30:00 +0800" {size}`
* 确保迁移工具在导入时使用源邮件的 `INTERNALDATE` 而非导入时的当前时间
* 对于已按错误日期导入的邮件，批量更新内部日期（根据 `Date:` 邮件头更正）

### 📖 推荐阅读

[🔄 Exchange 替代方案全流程指南
[🔄 Exchange替代方案指南

从 Exchange 到国产邮件系统的完整替代路径](/exchange-replacement.html)

Exchange 2016/2019 EOL 背景下的三大替代路径对比、技术评估维度与六阶段迁移框架](/exchange-replacement.html)
[📧 邮件迁移技术指南

IMAP 迁移、PST 导入、DNS 切换与回退预案 — 邮件系统迁移的完整操作手册](/email-migration.html)
[🛠️ 邮件服务器搭建与选型指南

从域名到DKIM：自建邮件服务器7步搭建教程与配置优化](/mail-server.html)
[🏗️ 自建邮件系统技术选型

自建邮件系统的架构选择：Postfix vs Exim vs 商业方案全面对比](/mail-server.html)

📦 邮件归档技术与合规指南

邮件归档策略、不可变存储与合规审计实践（专题建设中）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/exchange-data-migration-procedure.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
