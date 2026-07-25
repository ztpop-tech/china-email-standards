---
title: "EWS退役时间线与迁移指南：从Exchange Web Services到Microsoft Graph"
source: "https://ztpop.net/kb/exchange-ews-retirement-migration.html"
license: CC-BY 4.0
---

# EWS退役时间线与迁移指南：从Exchange Web Services到Microsoft Graph

## 摘要

Exchange Web Services（EWS）作为 Exchange Online 的核心 API 层已服役近二十年。Microsoft 已于 2025 年 9 月正式宣布 EWS 的分阶段退役计划[1]：2026年10月1日起，所有未经显式注册的 EWS 请求将被阻止；至 2027 年 4 月，EWS 将完全关闭，所有请求一律拒绝。本文基于 Microsoft 官方公告与迁移文档[1][2][4]，系统阐述退役时间线与影响范围，并提供从 EWS 到 Microsoft Graph API 的完整迁移路线图，帮助依赖 EWS 的组织在截止日期前完成应用重构与过渡。

## 一、EWS 退役时间线与阶段划分

EWS 的退役并非突然关闭，而是分三个阶段逐步实施[1]。理解每个阶段的时间节点和影响范围，是制定迁移计划的起点。

### 1.1 阶段一：新租户默认阻止（已实施）

自 2025 年起，新创建的 Exchange Online 租户默认禁用 EWS 访问[1]。如果新租户需要启用 EWS，管理员必须通过 Exchange Online PowerShell 显式申请允许。这一阶段的目的是防止新部署的应用继续依赖即将淘汰的协议栈。

### 1.2 阶段二：仅允许白名单应用（2026年10月1日）

从 2026 年 10 月 1 日起，所有 Exchange Online 租户的 EWS 请求将被默认禁用[1]。唯一的例外是已在 `EWSAllowedAppIDs` 白名单中注册的应用程序。未注册的任何应用——包括第三方邮件客户端、归档工具、CRM/ERP 集成组件——将无法通过 EWS 访问 Exchange Online 数据。

此阶段可被视为"缓冲期"：允许组织在继续使用关键 EWS 依赖应用的同时，完成向 Microsoft Graph API 的代码迁移。但必须注意，`EWSAllowedAppIDs` 仅是一个临时过渡机制，而非永久解决方案[1]。

### 1.3 阶段三：EWS 完全关闭（2027年4月）

2027 年 4 月，EWS 服务将完全关闭[1]。届时，无论是否在 `EWSAllowedAppIDs` 中注册，所有 EWS 请求均将被 Exchange Online 拒绝。这意味着：

* 所有基于 EWS 的应用程序将停止工作，无一例外
* 在阶段二注册的白名单失去效力
* EWS Managed API 和 EWS Java API 同步失效[2]

### 退役阶段汇总表

退役阶段汇总表

| 阶段 | 时间节点 | EWS 状态 | 关键操作 |
| --- | --- | --- | --- |
| 阶段一 | 已实施 | 新租户默认禁用，可申请启用 | 新部署应直接使用 Graph API |
| 阶段二 | 2026年10月1日 | 仅白名单应用可访问 EWS | 注册 EWSAllowedAppIDs；启动代码迁移 |
| 阶段三 | 2027年4月 | EWS 完全关闭 | 所有应用必须完成 Graph API 迁移 |

## 二、受影响的应用与场景

EWS 退役的影响面远超许多 IT 管理者的预期。以下列出所有通过 EWS 访问 Exchange Online 的应用类型与集成场景[1][2]：

### 2.1 直接受影响的组件

* **第三方邮件客户端：**通过 EWS 协议连接 Exchange Online 的自定义邮件客户端、Outlook Mac 2011 及更早版本[1]
* **邮件归档工具：**使用 EWS 拉取或同步邮件数据进行归档的第三方归档解决方案
* **CRM/ERP 集成：**通过 EWS API 在客户关系管理或企业资源规划系统中获取邮件/日历数据的集成模块
* **自定义集成应用：**任何使用 EWS Managed API（.NET）或 EWS Java API[2] 自行开发的企业应用
* **自动化脚本：**使用 EWS 端点执行邮箱管理、邮件发送或数据提取的 PowerShell 脚本

### 2.2 不受影响的协议（重要区分）

以下协议和客户端 **不** 受 EWS 退役影响[1]：

* **MAPI/HTTP：**Outlook（Windows 2016+、Mac 2016+）使用的原生协议，不受 EWS 退役影响
* **REST API：**Microsoft Graph 及其他 RESTful API 正常运行
* **IMAP/POP3/SMTP Auth：**标准邮件协议独立于 EWS，不受本次退役影响
* **Exchange ActiveSync（EAS）：**移动设备的同步协议，不依赖 EWS

## 三、替代方案：Microsoft Graph API

Microsoft Graph API 是 Microsoft 官方推荐、也是事实上唯一的 EWS 替代方案[2][3]。Graph API 是一套统一的 RESTful API，基于 OAuth 2.0 认证，提供对 Microsoft 365 全系数据（邮件、日历、联系人、任务、用户、组、文件等）的编程访问。

### 3.1 Graph API 核心优势

* **现代认证体系：**基于 OAuth 2.0 和 Azure AD（Microsoft Entra ID），支持委派权限与应用权限两种授权模式[5]。与 EWS 的 Basic Auth 相比，安全性显著提升
* **统一端点：**所有资源通过单一端点 `https://graph.microsoft.com` 访问，无需为不同工作负载维护不同的 URL
* **丰富的数据覆盖：**除邮件/日历/联系人外，Graph API 还可访问 Teams 消息、SharePoint 文件、OneDrive、用户与组管理、设备管理等 Microsoft 365 生态系统数据[3]
* **现代化开发体验：**提供多语言 SDK（.NET、Java、Python、JavaScript/TypeScript、Go、PHP），支持增量查询、变更通知（Webhook）、批量请求、分页与节流控制

### 3.2 核心端点映射：EWS → Graph API

3.2 核心端点映射：EWS → Graph API

| 功能 | EWS 操作 | Graph API 端点 |
| --- | --- | --- |
| 获取邮件列表 | FindItem | `GET /me/messages` |
| 读取单封邮件 | GetItem | `GET /me/messages/{id}` |
| 发送邮件 | CreateItem + SendItem | `POST /me/sendMail` |
| 获取日历事件 | FindItem (CalendarView) | `GET /me/events` |
| 创建日历事件 | CreateItem (Calendar) | `POST /me/events` |
| 获取联系人 | FindItem (Contacts) | `GET /me/contacts` |
| 获取文件夹列表 | FindFolder | `GET /me/mailFolders` |
| 获取邮箱设置 | GetUserConfiguration | `GET /me/mailboxSettings` |
| 获取可用时间 | GetUserAvailability | `POST /me/findMeetingTimes` |
| 搜索邮件 | FindItem (QueryString) | `GET /me/messages?$search="keyword"` |
| 订阅通知 | Subscribe (Streaming/Pull/Push) | `POST /subscriptions`（Webhook） |

### 3.3 代码迁移示例：EWS 到 Graph API

以下对比展示了从 EWS Managed API 迁移到 Microsoft Graph .NET SDK 的典型模式变化：

```
// === EWS Managed API (即将退役) ===
var service = new ExchangeService(ExchangeVersion.Exchange2013_SP1);
service.Credentials = new WebCredentials("user@contoso.com", "password");
service.Url = new Uri("https://outlook.office365.com/EWS/Exchange.asmx");

var view = new ItemView(10);
var results = service.FindItems(WellKnownFolderName.Inbox, view);
foreach (var item in results) {
    Console.WriteLine(item.Subject);
}

// === Microsoft Graph API (.NET SDK) ===
var client = new GraphServiceClient(credential);
var messages = await client.Me.Messages
    .Request()
    .Top(10)
    .GetAsync();
foreach (var message in messages) {
    Console.WriteLine(message.Subject);
}
```

## 四、迁移实施五步法

从 EWS 迁移到 Microsoft Graph API 是一项系统工程，需要从审计、评估到验证的完整闭环。以下是经过验证的五步迁移方法论[1][4]：

### 步骤一：审计当前 EWS 使用情况

在迁移开始前，必须全面了解组织中哪些应用和用户在调用 EWS。推荐通过以下渠道收集信息：

* **Azure AD / Entra ID 登录日志：**在 Azure 门户中查询登录日志，筛选客户端应用（Client App）字段中标识为 EWS 的记录。重点关注应用名称、调用频率、请求的权限范围
* **Exchange Online 管理控制台：**使用 `Get-User -ResultSize Unlimited | Where {$_.EWSEnabled -eq $true}` 确认启用了 EWS 的邮箱
* **第三方应用清单：**与各业务部门确认是否有定制的邮件集成工具，或由外部供应商提供的 EWS 依赖组件

### 步骤二：识别与分类 EWS 依赖

将审计发现的所有 EWS 依赖按以下维度分类：

步骤二：识别与分类 EWS 依赖

| 分类维度 | 示例 | 迁移优先级 |
| --- | --- | --- |
| 商业第三方产品 | 邮件归档工具、CRM 插件、签名服务器 | 联系供应商获取 Graph API 版本或确认替代方案 |
| 自研企业应用 | 内部邮件报表系统、自动化审批邮件网关 | 启动内部 Graph API 重构项目 |
| 运维脚本与自动化 | 批量邮箱管理 PowerShell 脚本 | 逐脚本重写，使用 Graph PowerShell SDK |
| 遗留客户端 | Outlook Mac 2011、自定义 IMAP/EWS 混合客户端 | 升级客户端或替换为标准 IMAP/SMTP 方案 |

### 步骤三：注册 EWSAllowedAppIDs（临时过渡）

对于无法在 2026 年 10 月 1 日前完成迁移的关键应用，可通过 Exchange Online PowerShell 将其注册到白名单中，确保业务连续性[1]：

```
# 设置 EWS 访问策略为强制白名单
Set-OrganizationConfig -EwsApplicationAccessPolicy EnforceAllowList

# 将应用 ID 添加到允许列表
Set-OrganizationConfig -EwsAllowList @{Add="AppID1","AppID2"}

# 验证当前配置
Get-OrganizationConfig | Format-List EwsApplicationAccessPolicy,EwsAllowList
```

需要向应用供应商或自研团队索取 Azure AD 中注册的应用程序 ID（Application ID / Client ID）。注意：此措施仅为过渡方案，2027 年 4 月全部失效[1]。

### 步骤四：将 EWS 代码迁移到 Microsoft Graph API

代码迁移是工作量最大的环节。以下为关键注意事项：

* **认证迁移：**从 EWS 的 Basic Auth / WebCredentials 迁移到基于 OAuth 2.0 的 Microsoft Entra ID 认证[5]。选择合适的权限模型：委派权限（Delegated，用户上下文）或应用权限（Application，后台服务）
* **API 映射：**对照 Microsoft 官方提供的《Migrating from EWS to Microsoft Graph》[4] 文档，逐个映射 EWS 操作到 Graph API 端点。注意处理 Graph API 中不存在直接 1:1 映射的高级 EWS 操作
* **数据模型差异：**EWS 使用 SOAP XML 响应格式，Graph API 使用 JSON。邮件的属性名称、日期时间格式、附件处理方式均有差异，需逐项适配
* **错误处理与重试：**Graph API 的限流策略（HTTP 429）与 EWS 不同。应用需实现指数退避重试逻辑，并处理 Graph API 特有的错误码
* **增量同步与变更通知：**Graph API 提供 Delta Query（增量查询）和 Webhook（变更通知）[3] 作为 EWS 同步文件夹和通知订阅的替代方案

### 步骤五：验证与停用 EWS 依赖

迁移完成后，必须在生产环境中进行全面验证：

1. **功能验证：**对照 EWS 版本，逐项验证 Graph API 版本的功能完整性（邮件收发、日历操作、联系人管理、文件夹同步）
2. **性能基准测试：**在典型负载下比较 Graph API 版本的响应时间和吞吐量，确认无性能回退
3. **并行运行期：**在阶段二期间（2026.10.1 - 2027.4），保持 Graph API 版本与 EWS 版本并行运行，通过日志比对确保数据一致性
4. **停用 EWS 配置：**确认所有应用稳定运行后，从 `EWSAllowList` 中移除对应应用 ID，并监控是否有异常
5. **最终验证：**在阶段三（2027年4月）到来前，确认所有应用的 EWS 依赖已完全移除，仅通过 Graph API 运行

## 五、风险评估与缓解策略

### 5.1 核心风险矩阵

5.1 核心风险矩阵

| 风险 | 可能性 | 影响 | 缓解措施 |
| --- | --- | --- | --- |
| 未识别隐藏的 EWS 依赖导致应用在阶段二断连 | 中 | 高 | 全量审计 Azure AD 登录日志；与所有业务部门逐一确认集成交互；阶段二前注册 EWSAllowedAppIDs 兜底 |
| 第三方应用供应商未及时提供 Graph API 版本 | 高 | 高 | 立即联系所有 EWS 依赖的供应商，获取迁移时间表或替代方案；对于无迁移计划的应用，寻找替代产品 |
| 自研应用迁移工作量低估导致错过截止日期 | 高 | 高 | 尽早启动代码审计与工作量评估；使用 EWSAllowedAppIDs 争取缓冲时间；分批迁移，先迁移关键路径 |
| Graph API 不支持特定 EWS 高级操作 | 低 | 中 | 查阅 Microsoft Graph 功能覆盖文档[4]；对于 Graph API 未覆盖的边缘操作，评估改用 Exchange Online PowerShell 或评估功能替代方案 |
| OAuth 2.0 认证配置错误导致应用无法连接 | 中 | 中 | 在测试租户中先行配置和验证 OAuth 流程；准备详细的 Entra ID 应用注册与权限配置文档 |
| IMAP/POP3/SMTP Auth 被误认为受 EWS 退役影响而恐慌迁移 | 低 | 低 | 明确沟通：标准邮件协议（IMAP/POP3/SMTP Auth）不受 EWS 退役影响[1] |

### 5.2 EWSAllowedAppIDs 的局限性

`EWSAllowedAppIDs` 是一个有明确生命周期的过渡机制，使用时需注意以下限制[1]：

* 仅在阶段二有效（2026.10.1 至 2027.4），阶段三起完全失效
* 每个租户的白名单条目数存在上限，需合理规划注册应用数量
* 注册仅保证 EWS 请求不被阻止，但不能解决 EWS API 功能冻结的问题——EWS 不会获得新功能或改进
* 此机制不应被视为"迁移可以推迟到 2027 年"的信号——将迁移压力堆积到最后一刻会急剧放大风险

## 六、对国产邮件系统生态的启示

EWS 的退役不仅是 Microsoft 365/Exchange Online 用户面临的问题，对于整个邮件行业也具有深远的信号意义。EWS 作为基于 SOAP 的私有协议 API，其退役标志着邮件行业从私有协议 API 向标准化 RESTful API 的范式转变。

对于计划从 Exchange 迁移至国产邮件系统的组织而言，当前是审视应用架构的良机：将邮件集成层从 EWS 私有协议解耦，转而使用跨平台标准协议（IMAP/SMTP）或目标邮件系统提供的标准化 REST API，可以从根本上消除单一厂商的 API 锁定风险。在国产邮件系统的选型中，是否提供完善的 RESTful API 以及是否基于标准协议（而非私有封装）进行集成，应作为重要的评估维度。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/exchange-ews-retirement-migration.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
