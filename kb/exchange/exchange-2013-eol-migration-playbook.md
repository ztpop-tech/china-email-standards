---
title: "Exchange 2013 2026年停服迁移实战指南：应急方案与完整迁移检查清单"
source: "https://ztpop.net/kb/exchange-2013-eol-migration-playbook.html"
license: CC-BY 4.0
---

# Exchange 2013 2026年停服迁移实战指南：应急方案与完整迁移检查清单

## 一、Exchange 2013 ESU 停服时间线与影响评估

Exchange 2013 的 Mainstream Support 已于 2018 年 4 月结束，Extended Support 于 2023 年 4 月到期，微软随后提供了为期三年的 Extended Security Updates（ESU）作为付费扩展安全覆盖。根据 Microsoft 产品生命周期公告，Exchange 2013 ESU 的最后支付年度将于 2026 年 8 月截止 [1]。这意味着：

此后微软将不再发布任何 Exchange 2013 安全更新，包括 Critical 级别的远程执行漏洞（RCE）补丁。参考 Exchange 2021 年 Hafnium 攻击事件（CVE-2021-26855 等四个 0day 漏洞，影响全球约 10 万台 Exchange 服务器），运行不受支持软件的服务器在漏洞曝光后数小时内即面临被主动攻击的风险 [4]。

对于拥有数百或数千邮箱的组织，一次性全量迁移的窗口期可能长达数周。以下是基于组织规模的典型迁移耗时估算：

对于超过 5000 邮箱的组织，建议将 ESU 到期日作为最终死线（hard deadline），实际迁移完成时间应至少提前 3 个月，以留出测试与回滚余量。

## 二、环境评估与迁移方案选择

在启动迁移之前，必须对源端 Exchange 2013 环境进行完整审计。关键检查项包括：

* **Exchange 版本与累积更新（CU）**：Exchange 2013 的最后一个累积更新为 CU23（2021 年发布）。确认 CU 版本直接决定 EWS（Exchange Web Services）接口的行为特性。如果 CU 版本低于 CU21，建议先升级至 CU23 再启动迁移，否则 EWS 连接稳定性可能不达标。
* **邮箱数据库（EDB）大小统计**：通过 `Get-MailboxDatabase -Status | fl Name,DatabaseSize` 命令获取每个 EDB 的物理大小，估算全量迁移的网络传输量。对于超大规模数据库（>500GB），考虑分步或 PST 离线迁移。
* **AD 用户与 Exchange 属性同步**：Exchange 2013 深度依赖 Active Directory。通过 `Get-Mailbox -ResultSize Unlimited | Export-Csv mailbox-inventory.csv` 导出完整邮箱清单，包含 SMTP 地址、邮箱类型（用户邮箱/共享邮箱/资源邮箱）、配额信息。
* **邮件流拓扑记录**：使用 `Get-SendConnector | fl Name,AddressSpaces,DNSRoutingEnabled,SmartHosts` 和 `Get-ReceiveConnector | fl Name,Bindings,RemoteIPRanges` 记录发送/接收连接器配置，为后续邮件流重建提供依据。
* **证书与身份验证配置**：确认当前的 TLS 证书、SMTP 证书以及 OWA/EAC 证书的到期日期。Exchange 2013 对 TLS 1.0/1.1 的默认启用应考虑禁用（符合 PCI DSS 和 NIST SP 800-52 要求）。

基于以上审计结果，选择最适合的迁移模式。主要路径包括：

1. **IMAP 协议迁移**：适用于旧版 Exchange 或 EWS 不稳定的场景，基于 RFC 3501 IMAP4rev1 协议逐箱同步邮件数据。兼容性最佳但功能覆盖有限（不支持日历/会议的自动同步）[6]。
2. **EWS 接口迁移**：Exchange 2013 的原生 API，支持邮件、日历、联系人、任务的完整读写。通过 EWS Managed API 或 REST API 进行逐箱迁移，功能覆盖最完整 [5]。
3. **PST 离线迁移**：使用 `New-MailboxExportRequest` cmdlet 将邮箱导出为 PST 文件，再通过目标平台的 PST 导入工具装入。适用于网络带宽受限的场景，但需要额外的存储空间和手动操作 [2]。

## 三、共存方案：Exchange 2013 与目标邮件系统并行

在分阶段迁移场景中，Exchage 2013 需要与目标邮件系统在共存期内并行运行。共存的核心理念是「邮件流不中断，用户感知最小化」。以下为标准共存架构：

```
[Internet] --- MX ---> [SMTP Relay/Gateway]
                         |
                    +----+----+
                    |         |
            Exchange 2013    国产邮件系统
            (迁移源)        (迁移目标)
                    |         |
                    +----+----+
                         |
                    Edge Transport
                  (邮件路由决策点)
```

**邮件流路由策略：**

* **入站邮件**：在 SMTP 网关或前端连接器上设置分发列表（dynamic distribution group），根据收件人的所属域或迁移状态将邮件路由至 Exchange 2013 或目标平台。可通过 `Get-Recipient` 命令筛选未迁移信箱的收件人，动态更新路由规则。
* **出站邮件**：Exchange 2013 的 Send Connector 配置不变，新平台通过 SMTP relay 指向原有出站网关。出站邮件统一经 Exchange 2013 或独立 SMTP 网关（如 Postfix MTA）外发 [7]。
* **目录同步**：通过 AD LDS（Active Directory Lightweight Directory Services）或 LDAP 同步工具维护两端用户目录的一致性。Exchange 2013 的离线地址簿（OAB）与目标平台的地址簿之间的同步需要额外的中间件支持。

## 四、数据迁移操作流程

### 4.1 IMAP 协议迁移

IMAP 迁移是最通用的兼容路径，几乎所有邮件系统都支持。操作步骤：

1. 在 Exchange 2013 上启用 IMAP：`Set-CASMailbox -Identity user@domain.com -ImapEnabled $true`，并确认 IMAP 服务端口（993/TCP）可访问。
2. 在目标邮件系统的迁移工具中配置源端 IMAP 连接参数：服务器地址、端口（143 STARTTLS 或 993 SSL/TLS）、认证方式（Plain/Login）。
3. 执行全量同步。建议先同步少量测试账户验证配置正确性，再批量执行。
4. 同步完成后进行差异检查：对比源端与目标端的邮件总数、最近 30 天邮件数、收件箱文件夹大小。

**⚠️ 注意：**IMAP 协议不传输邮件的已读/未读状态（FLAGS）和文件夹结构中的特殊标签（如 \Archive、\Junk）。部分目标平台的 IMAP 迁移工具会尝试通过 IDLE 或自定义扩展补全这些属性，但不保证完全一致。涉及日历和联系人数据的同步需使用额外的工具或 EWS 接口。

### 4.2 EWS 接口迁移

Exchange 2013 的 EWS（Exchange Web Services）提供了对邮箱数据的完整访问权限。基于 EWS 的迁移可以实现日历、联系人、任务与邮件的无损传输。

```
# Exchange 2013 端确认 EWS 可用性
Get-WebServicesVirtualDirectory | fl Server,InternalUrl,ExternalUrl

# 确认 OAuth 或基本认证配置
Get-AuthenticationPolicy | fl *
```

EWS 迁移的典型流程：在迁移工具中配置 EWS URL（通常为 https://mail.domain.com/EWS/Exchange.asmx）、认证凭据。EWS 支持 `FindItem`/`GetItem` 操作读取邮件，`FindFolder` 枚举文件夹结构，`FindAppointment`/`GetAppointment` 处理日历项目。对于日历和会议，建议在迁移前取消所有未确认的会议邀请，以避免双重预订。

### 4.3 PST 离线迁移

对于网络传输受限或数据量超大的场景，PST 导出是可行的补充方案。

```
# Exchange 2013 命令行管理程序
# 授予 Mailbox Import/Export 角色权限
New-ManagementRoleAssignment -Role "Mailbox Import Export" -User "Administrator"

# 导出特定邮箱为 PST
New-MailboxExportRequest -Mailbox user@domain.com -FilePath "\\SERVER\Exports\user@domain.com.pst"

# 检查导出状态
Get-MailboxExportRequest | Get-MailboxExportRequestStatistics
```

导出完成后，将 PST 文件传输至目标平台服务器，使用导入工具或 IMAP 上传方式进行装载。注意：PST 文件中的 S/MIME 加密邮件和 IRM（Information Rights Management）保护内容在导出/导入过程中可能会丢失保护属性。

## 五、割接切换流程

割接（Cutover）是整个迁移工程的高潮环节，应当在非工作时间（如周五晚至周一早的窗口期）执行。标准割接流程：

1. **最终增量同步**：在割接窗口开启前执行一次全量增量同步，确保已迁移用户的最新邮件到达目标平台。
2. **邮件流切换**：修改 DNS MX 记录，使入站邮件从 Exchange 2013 切换至目标邮件系统。注意 MX TTL 设置——若不降低 TTL（建议提前 48 小时改为 300 秒），DNS 传播延迟可能导致部分邮件继续发送到旧系统。
3. **最后同步**：MX 切换完成后，Exchange 2013 继续接收的残余邮件在 30 分钟后再次同步至目标平台。
4. **自动回复/转发配置**：在 Exchange 2013 上对已迁移用户设置自动转发至目标邮箱（可选）。通过 `Set-Mailbox -Identity user@domain.com -ForwardingAddress target@newdomain.com -DeliverToMailboxAndForward $false` 实现。
5. **功能验证**：收发测试（内部→内部、内部→外部、外部→内部）、日历邀请收发测试、地址簿查询测试。
6. **旧系统下线**：观察至少 7 天，确认无异常后在 Exchange 2013 上卸载邮箱数据库（Unmount-Database），保留服务器以备回滚。

## 六、迁移后验证与检查清单

**完整迁移检查清单：**

| 类别 | 检查项 | 验证方式 |
| --- | --- | --- |
| 数据完整性 | 已迁移邮箱邮件数与源端一致 | 对比 IMAP SUBSCRIBED mailbox LIST 计数 |
| 数据完整性 | 最近 90 天邮件全部到达 | 抽样检查发送/接收时间跨度的连续性 |
| 日历 | 未来会议邀请正常显示 | OWA/WebMail 打开日历视图 |
| 联系人 | 全局地址簿（GAL）包含所有用户 | LDAP 查询或地址簿搜索测试 |
| 邮件流 | 收发正常到达且延迟 < 30 秒 | 发送测试邮件，查看邮件头时间戳 |
| 认证 | SMTP/IMAP/OWA 认证均正常 | 分别测试各协议端口 |
| 安全 | TLS 1.2+ 配置、SPF/DKIM/DMARC 正确 | dig 查询 DNS 记录、SSL Labs 测试 |
| 备份 | Exchange 2013 EDB 已完整归档 | 确认 EDB 文件备份存在 |

建议保留 Exchange 2013 服务器至少 30 天，之后可降级回收。保留期间定期检查事件日志中的邮件流异常。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/exchange-2013-eol-migration-playbook.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
