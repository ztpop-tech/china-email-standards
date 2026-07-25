---
title: "JMAP 邮件访问协议深度解析 — RFC 8620/8621：IMAP 的下一代替代方案 · ztpop 邮件技术知识库"
source: "https://ztpop.net/kb/jmap-protocol-rfc8620.html"
license: CC-BY 4.0
---

# JMAP 邮件访问协议深度解析 — RFC 8620/8621：IMAP 的下一代替代方案 · ztpop 邮件技术知识库

JMAP 邮件访问协议深度解析 — RFC 8620/8621：IMAP 的下一代替代方案

## 1. 为什么需要替代 IMAP

IMAP（RFC 3501，2003 年发布）在其诞生后的二十余年间始终是邮件客户端与服务器之间的主流协议。但它的设计植根于 1990 年代的计算模型：
**单设备、持久 TCP 长连接、简单的文件夹层级**
。进入多设备同步时代后，IMAP 的短板集中暴露在三个层面。

**同步模型缺陷**
是首当其冲的问题。IMAP 的
`STATUS`
/
`SEARCH`
/
`FETCH`
命令链条要求客户端逐邮箱轮询变化：先查 INBOX 是否有新邮件，再遍历文件夹检查未读数变更。RFC 4551 引入的 CONDSTORE 和 RFC 5162 引入的 QRESYNC 试图解决增量同步问题，但截至 2025 年，Gmail 仍未实现 CONDSTORE，Yahoo Mail 和 Microsoft 365 同样缺少完整支持。现实场景中，大多数 IMAP 客户端重启时只能全量拉取摘要，一台拥有 28,234 封邮件的账户重启同步平均耗费 2.1 MB 带宽，而 JMAP 等价操作仅需 13 KB。

**扩展碎片化**
是第二个病灶。IMAP 通过扩展（Capability 机制）弥补功能缺口：MOVE（RFC 6851）、SORT（RFC 5256）、THREAD（RFC 5256）、COMPRESS（RFC 4978）——但这些扩展并非强制要求。服务商按自身优先级选择性实现，客户端被迫维护数十条兼容分支。以线程视图为例：Gmail 用私有扩展
`X-GM-THRID`
暴露对话线程，而标准 THREAD 扩展几乎无人部署。一个跨 provider 的邮件客户端需要同时处理至少四套不同的"线程"获取逻辑。

**连接模型过时**
。IMAP 基于长连接 TCP socket。每个连接绑定单一邮箱上下文，客户端必须为并发操作维护多个 socket。推送通知依赖 IDLE 扩展（RFC 2177），但 IDLE 仅覆盖一个文件夹，全账户实时推送需要客户端轮询或同时维持数十个 IDLE 连接。移动端电池续航在此模型下显著受损——设备无线电模块每 15–30 秒被唤醒一次进行轮询，实测电池消耗是 JMAP 推送方案的 2–3 倍。

## 2. JMAP 核心架构：JSON over HTTPS

JMAP（JSON Meta Application Protocol）将邮件协议从 TCP 连接模型迁移到 HTTP 请求/响应模型。这一决策来自一个简单的观察：
**HTTP 基础设施在过去二十年得到了全面优化**
——TLS 终止、负载均衡、DDoS 防护、压缩、缓存代理——而 IMAP 的每一层都需要专用工具重新实现。JMAP 设计者将协议分层，让 HTTP 和 JSON 各自承担它们擅长的职责。

### 2.1 传输层：HTTP + JSON

所有 JMAP 请求通过 HTTP POST 发送到单一端点（通常为
`/jmap/api`
或由
`/.well-known/jmap`
返回的 Session 资源中的
`apiUrl`
）。请求体和响应体均为 JSON。RFC 8620 第 3 节定义了完整的请求/响应结构范式。

协议分层如下：

* **HTTP/2 或 HTTP/3**
  处理传输安全（TLS 1.3）、多路复用、头部压缩
* **JSON（RFC 8259）**
  处理数据序列化
* **JMAP Core（RFC 8620）**
  定义通用的方法调用、响应和错误范式
* **JMAP Mail（RFC 8621）**
  定义邮件域的数据模型与业务语义

这种分层意味着部署 JMAP 服务时可以复用现有的 HTTP 技术栈：NGINX 或 Caddy 做 TLS 终结和反向代理，标准负载均衡器做水平扩展，Cloudflare 等 CDN/WAF 层提供 DDoS 防护，Prometheus/Grafana 做 HTTP 级别的监控——不需要专门的邮件协议探测工具。

### 2.2 请求批处理与方法调用

JMAP 的核心交互模式是
**方法调用数组**
（RFC 8620 第 3.2 节）。单次 HTTP POST 可以携带多个独立的 JMAP 方法调用，服务器按数组顺序处理，返回多个响应。

```
POST /jmap/api HTTP/1.1
Host: mail.example.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
Content-Type: application/json

{
  "using": [
    "urn:ietf:params:jmap:core",
    "urn:ietf:params:jmap:mail"
  ],
  "methodCalls": [
    ["Mailbox/query", {
      "accountId": "u1",
      "filter": { "role": "inbox" }
    }, "a"],
    ["Mailbox/get", {
      "accountId": "u1",
      "#ids": {
        "resultOf": "a",
        "name": "Mailbox/query",
        "path": "/ids"
      }
    }, "b"],
    ["Email/query", {
      "accountId": "u1",
      "filter": { "inMailbox": "{{#b.ids[0]}}" },
      "sort": [{ "property": "receivedAt", "isAscending": false }],
      "position": 0,
      "limit": 20
    }, "c"]
  ]
}
```

上面这个请求在一次 HTTP 往返中完成了三件事：(1) 查询 INBOX 的 mailbox ID；(2) 获取 mailbox 详情；(3) 获取 INBOX 中最新 20 封邮件的列表。方法调用之间的引用通过
`#ids`
的 JSON 指针语法实现——
`resultOf`
引用前一个方法调用的结果，
`path`
指向结果 JSON 中的路径。这种
**方法链**
是 JMAP 消除多次网络往返的核心机制，也是 IMAP 无法实现的——IMAP 的每个命令都是独立交互，客户端必须等待上一个命令的响应才能发出下一个。

### 2.3 幂等性与创建 ID

RFC 8620 第 3.3 节要求所有
`/set`
方法的
`create`
操作必须携带客户端生成的不透明
`id`
（creation id）。创建 ID 在请求内唯一，用于引用尚未分配服务器端 ID 的新对象。同一请求中后续的方法调用可以通过
`#`
前缀引用这些临时 ID。

RFC 8620 第 5.3 节定义了幂等性保证：客户端可以为整个请求提供一个
`clientRequestId`
，服务器在 24 小时内对相同
`clientRequestId`
的重试返回缓存结果而不重复执行写操作。这一点对移动客户端在弱网环境下的可靠性至关重要。

## 3. RFC 8620 核心数据类型与方法

RFC 8620 不定义任何邮件特有概念，只定义一套可跨数据类型复用的通用 API 模式。这些模式随后被 RFC 8621（邮件）、RFC 8887（日历）、RFC 9610（联系人）复用。

### 3.1 Session 对象

Session 是 JMAP 的入口点。客户端向
`/.well-known/jmap`
发送 GET 请求或直接 GET
`/jmap/session`
，服务器返回一个 Session JSON 对象（RFC 8620 第 2 节）：

```
{
  "capabilities": {
    "urn:ietf:params:jmap:core": {
      "maxSizeUpload": 50000000,
      "maxConcurrentUpload": 8,
      "maxCallsInRequest": 32,
      "maxObjectsInGet": 500,
      "maxObjectsInSet": 500,
      "collationAlgorithms": [
        "i;unicode-casemap"
      ]
    },
    "urn:ietf:params:jmap:mail": {
      "maxMailboxesPerEmail": null,
      "maxMailboxDepth": null,
      "maxSizeMailboxName": 256,
      "maxSizeAttachmentsPerEmail": 50000000,
      "emailQuerySortOptions": [
        "receivedAt", "sentAt", "size",
        "from", "to", "subject"
      ],
      "mayCreateTopLevelMailbox": true
    }
  },
  "accounts": {
    "u1": {
      "name": "zhangtao@example.com",
      "isPersonal": true,
      "isReadOnly": false,
      "accountCapabilities": {
        "urn:ietf:params:jmap:mail": {
          "maxMailboxesPerEmail": 10,
          "maxSizeAttachmentsPerEmail": 25000000
        }
      }
    }
  },
  "primaryAccounts": {
    "urn:ietf:params:jmap:mail": "u1"
  },
  "username": "zhangtao@example.com",
  "apiUrl": "https://mail.example.com/jmap/api",
  "downloadUrl": "https://mail.example.com/jmap/download/{accountId}/{blobId}/{name}?type={type}",
  "uploadUrl": "https://mail.example.com/jmap/upload/{accountId}/",
  "eventSourceUrl": "https://mail.example.com/jmap/eventsource/?types=*&closeafter=state&ping=60",
  "state": "4287"
}
```

Session 对象包含了客户端需要的一切：支持的能力与参数、用户账户列表、API/上传/下载端点 URL、事件推送端点以及当前全局状态令牌。客户端缓存 Session 对象并在收到
`serverPartial`
错误时重新获取。

### 3.2 核心方法：/get、/set、/query、/changes

JMAP 所有数据类型的操作都收敛到四个核心方法（RFC 8620 第 5 节）：

3.2 核心方法：/get、/set、/query、/changes

| 方法 | 用途 | 幂等？ |
| --- | --- | --- |
| `/get` | 按 ID 获取对象，支持 `properties` 字段选择 | 是 |
| `/set` | 创建、更新、删除对象（含 `create` 、 `update` 、 `destroy` 三种子操作） | 部分（create/destroy 不允许重复执行） |
| `/query` | 按过滤条件搜索，返回 ID 列表 + 总计数 | 是 |
| `/changes` | 获取自某个状态令牌以来的增量变更（创建/更新/销毁的 ID 列表） | 是 |

这四个方法覆盖了 CRUD + 搜索 + 增量同步的完整生命周期。所有数据类型（Mailbox、Email、Thread、Identity 等）遵循完全相同的调用签名，只是数据模型不同。客户端只需要学会一套模式，即可操作所有 JMAP 数据。

### 3.3 标准响应结构

每个方法调用返回一个标准三段式响应（RFC 8620 第 3.4 节）：

```
[
  "methodResponse", [
    "result", { /* 成功时的方法特定数据 */ }, "请求中指定的调用 ID"
  ],
  [
    "error", {
      "type": "accountNotFound",
      "description": "Account 'u2' not found"
    }, "请求中指定的调用 ID"
  ]
]
```

每个响应元素是一个长度为 3 的数组：
`[result, 数据, 调用ID]`
。类型为
`"result"`
或
`"error"`
。这种结构允许客户端通过调用 ID 将响应映射回原始请求——多请求乱序返回时依然可以正确关联。

## 4. RFC 8621：邮件数据模型

RFC 8621 在 RFC 8620 核心基础上定义了邮件的完整数据模型。核心数据类型包括 Mailbox、Email、Thread、SearchSnippet、Identity、EmailSubmission 等。本文聚焦前三个。

### 4.1 Mailbox 类型

Mailbox 对象（RFC 8621 第 2 节）代表邮件文件夹。必选字段如下：

```
{
  "id": "Mabc123",
  "name": "Inbox",
  "parentId": null,
  "role": "inbox",
  "sortOrder": 10,
  "totalEmails": 2847,
  "unreadEmails": 12,
  "totalThreads": 1203,
  "unreadThreads": 9,
  "myRights": {
    "mayReadItems": true,
    "mayAddItems": true,
    "mayRemoveItems": true,
    "maySetSeen": true,
    "maySetKeywords": true,
    "mayCreateChild": true,
    "mayRename": true,
    "mayDelete": true,
    "maySubmit": true
  },
  "isSubscribed": true
}
```

与 IMAP 相比，Mailbox 的
`role`
字段是一个明确的人际可读标记（inbox / archive / drafts / sent / trash / junk），替代了 IMAP 的
`\Inbox`
/
`\Sent`
/
`\Trash`
等特殊用途属性（RFC 6154 SPECIAL-USE）。
`totalEmails`
和
`unreadEmails`
开箱即用，无需像 IMAP 那样先 SELECT 再 STATUS。myRights 对象以 ACL 样式声明当前用户对单个 mailbox 的各项操作权限。

### 4.2 Email 类型

Email 对象（RFC 8621 第 4 节）是协议中最庞大的数据模型，包含约 80 个字段。核心字段按功能分组：

**标识**
：
`id`
、
`blobId`
（原始 MIME 的存储引用）、
`threadId`
、
`mailboxIds`
（该邮件所在的所有 mailbox ID 集合——邮件可以同时属于多个文件夹和标签）。

**头信息**
：
`from`
、
`to`
、
`cc`
、
`bcc`
、
`replyTo`
、
`sender`
、
`subject`
、
`sentAt`
、
`receivedAt`
。每个地址字段是
`EmailAddress`
对象数组，包含
`name`
和
`email`
两个字段。

**内容**
：
`bodyStructure`
（MIME 结构树）、
`bodyValues`
（按 partId 索引的已解析正文内容）、
`textBody`
（纯文本列表）、
`htmlBody`
（HTML 内容列表）、
`attachments`
（附件列表，含 blobId、size、type、name）。

**状态**
：
`isUnread`
、
`isFlagged`
、
`isAnswered`
、
`isDraft`
、
`hasAttachment`
——替代 IMAP 的
`\Seen`
、
`\Flagged`
、
`\Answered`
、
`\Draft`
标志位。另外引入了
`keywords`
：一个字符串到布尔值的映射，对应 IMAP 的自定义关键词（RFC 5788）。

```
// 获取一封邮件的内容示例（Email/get 响应片段）
{
  "id": "Edef456",
  "blobId": "G789xyz",
  "threadId": "Tthread1",
  "mailboxIds": { "Mabc123": true, "Mdrafts": true },
  "subject": "Q3 邮件系统性能优化方案",
  "from": [{ "name": "张三", "email": "zhangsan@example.com" }],
  "to": [
    { "name": "技术团队", "email": "tech@example.com" }
  ],
  "receivedAt": "2026-07-03T14:30:00Z",
  "sentAt": "2026-07-03T14:28:00Z",
  "size": 15360,
  "isUnread": false,
  "isFlagged": true,
  "hasAttachment": true,
  "attachments": [
    {
      "blobId": "A001",
      "name": "benchmark-2026Q3.pdf",
      "type": "application/pdf",
      "size": 2048000
    }
  ],
  "preview": "各位同学，附件中是 Q3 的负载测试数据..."
}
```

RFC 8621 第 4.1.2 节要求
`preview`
字段返回纯文本前 256 个字符，客户端无需下载完整正文即可渲染邮件预览——IMAP 的
`BODY[HEADER.FIELDS (SUBJECT)]`
+
`BODY[1]`
无法做到这一点。

### 4.3 Thread 类型

Thread 对象（RFC 8621 第 5 节）将同一邮件对话下的所有 Email 组织为有向无环图（非严格树形结构，因为一封邮件可以有多个 parent）。核心字段：
`id`
、
`emailIds`
（按时间排序的线程内邮件 ID 列表）。Thread 的查询结果可作为 Email/query 的
`filter`
输入——"获取线程 T1 中的所有邮件"只需一次查询，无需像 IMAP THREAD 那样先获取 threading 算法结果再逐个 FETCH。

## 5. 状态同步与推送机制

同步是邮件协议的灵魂。JMAP 用两套机制覆盖增量同步和主动推送，两者组合后完全替代 IMAP 的 CONDSTORE + IDLE。

### 5.1 状态令牌

JMAP 的每个数据类型都在账户级别维护一个分布式单调递增的状态令牌（state token，RFC 8620 第 2 节）。Session 对象中的
`"state": "4287"`
就是全局状态令牌。每当账户内任何 Mailbox、Email、Thread 对象发生变更，状态令牌更新。

客户端同步流程：

1. 记录上次同步的
   `state`
   值（如
   `"4287"`
   ）
2. 调用
   `Email/changes`
   ，传入
   `sinceState: "4287"`
3. 服务器返回
   `{ "created": [...], "updated": [...], "destroyed": [...], "newState": "4291" }`
4. 客户端对
   `created`
   /
   `updated`
   的 ID 列表调用
   `Email/get`
5. 更新本地数据库，将状态更新为
   `"4291"`

这个流程中，2 和 4 各是一次 HTTP 往返。总计 2 次往返完成全账户邮件同步。IMAP 的等价流程：SELECT INBOX → SEARCH SINCE → FETCH UIDs → SELECT 下一个文件夹 → 重复——N 个文件夹意味着至少 2N+1 次命令交互。

### 5.2 EventSource 推送

JMAP 的实时推送通过 EventSource（Server-Sent Events, SSE）实现（RFC 8620 第 7 节），而非 IMAP 的 IDLE 命令。客户端连接 Session 对象中的
`eventSourceUrl`
，服务器通过标准 SSE 推送状态变更事件：

```
event: state
data: { "changed": {
data:   "u1": {
data:     "Mailbox": "4300",
data:     "Email": "9056"
data:   }
data: }}

event: state
data: { "changed": {
data:   "u1": {
data:     "Email": "9057"
data:   }
data: }}
```

客户端收到事件后，仅需对状态发生变化的类型执行
`/changes`
增量同步。SSE 基于标准 HTTP 长连接，通过 HTTP/2 的多路复用机制可以与 API 请求共享同一个 TCP 连接——不需要额外端口，不需要专用防火墙规则。

RFC 9007 进一步定义了 JMAP over WebSocket 传输绑定的实验性规范，用于需要双向推送的场景（如在客户端上直接"标记已读"并同步回服务器）。不过 SSE 仍是生产环境中最主要的推送机制。

### 5.3 与 IMAP CONDSTORE + IDLE 的对照

5.3 与 IMAP CONDSTORE + IDLE 的对照

| 能力 | JMAP | IMAP |
| --- | --- | --- |
| 增量同步 | /changes + state token — 内建，所有服务器必须支持 | CONDSTORE (RFC 4551) + QRESYNC (RFC 5162) — 可选扩展，主流免费邮箱未实现 |
| 实时推送 | EventSource (SSE) — 单连接覆盖全账户所有类型 | IDLE (RFC 2177) — 每连接一个 mailbox |
| 移动推送 | WebPush 集成 — 协议层支持 | 需提供商私有方案 |
| 离线恢复同步 | 单次 /changes 调用（~13 KB for 28K 邮件） | 无 CONDSTORE 时需全量 FLAGS FETCH（~2.1 MB 同上场景） |

## 6. 性能对比数据

以下数据来自 JMAP 工作组的基准测试，测试环境为 28,234 封邮件的账户、客户端冷启动（无本地缓存）。

6. 性能对比数据

| 指标 | JMAP (RFC 8621) | IMAP (无 CONDSTORE / QRESYNC) |
| --- | --- | --- |
| 首次同步带宽 | 13 KB | 2,100 KB |
| 网络往返次数（1 个 INBOX） | 2 | 4–7 |
| 网络往返次数（20 个文件夹） | 3–12（批量并行） | 60–140（逐文件夹 SELECT） |
| 首字节时间（获取最新 20 封邮件列表） | 1 次 HTTP 往返（方法调用批处理） | 3–5 次命令/响应 |
| 移动端功耗（1 小时推送待机） | 基准 | 2–3× 基准 |
| 发送 20 MB 附件（写入放大） | 20 MB（上传一次，blobId 复用） | 155 MB（自动保存草稿 5 次写入） |

IMAP 的核心带宽浪费来自"无差异全量同步"：冷启动时客户端必须
`FETCH 1:* (FLAGS)`
拉取所有邮件的已读/未读标记，无论这些标记自上次同步以来是否变更。附件上传的写入放大同样触目惊心——Outlook 在编辑一封含 20 MB 附件的邮件时，每次自动保存草稿、每次修改主题行、点击发送、复制到已发送、SMTP 投递各产生一次完整上传，总计 5 次。

JMAP 通过
`Blob/copy`
机制（RFC 8620 第 6 节）实现附件零拷贝转发：已上传的附件 blobId 可直接在新邮件中引用，服务器负责内部引用计数而非重新传输。转发一封 20 MB 附件的邮件在 JMAP 下不需要客户端下载再上传附件——只需将 blobId 写入新邮件的 attachment 列表。

## 7. 实战：curl 调用 JMAP API

### 7.1 获取 Session 对象

```
# 步骤 1: 获取 JMAP Session
curl -s -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  https://mail.example.com/.well-known/jmap | python3 -m json.tool

# 步骤 2: 也可以直接 GET 服务器返回的实际 apiUrl
curl -s -u "user:pass" \
  https://mail.example.com/jmap/session | python3 -m json.tool
```

Session 响应中提取
`apiUrl`
、
`accounts`
中的 accountId（如
`"u1"`
），以及当前
`state`
。

### 7.2 获取邮箱列表

```
curl -s -X POST \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  https://mail.example.com/jmap/api \
  -d '{
  "using": [
    "urn:ietf:params:jmap:core",
    "urn:ietf:params:jmap:mail"
  ],
  "methodCalls": [
    ["Mailbox/query", {
      "accountId": "u1",
      "sort": [{ "property": "sortOrder" }]
    }, "m1"],
    ["Mailbox/get", {
      "accountId": "u1",
      "#ids": {
        "resultOf": "m1",
        "name": "Mailbox/query",
        "path": "/ids"
      },
      "properties": [
        "id", "name", "role", "totalEmails",
        "unreadEmails", "totalThreads", "unreadThreads"
      ]
    }, "m2"]
  ]
}' | python3 -m json.tool
```

**响应示例**
：

```
{
  "methodResponses": [
    ["Mailbox/query", {
      "accountId": "u1",
      "queryState": "f8e7d6",
      "canCalculateChanges": true,
      "position": 0,
      "ids": ["Mabc123", "Mdef456", "Mghi789", "Mjkl012"],
      "total": 4
    }, "m1"],
    ["Mailbox/get", {
      "accountId": "u1",
      "state": "4288",
      "list": [
        {
          "id": "Mabc123",
          "name": "Inbox",
          "role": "inbox",
          "totalEmails": 2847,
          "unreadEmails": 12,
          "totalThreads": 1203,
          "unreadThreads": 9
        },
        {
          "id": "Mdef456",
          "name": "Sent",
          "role": "sent",
          "totalEmails": 5231,
          "unreadEmails": 0,
          "totalThreads": 5103,
          "unreadThreads": 0
        },
        {
          "id": "Mghi789",
          "name": "Drafts",
          "role": "drafts",
          "totalEmails": 3,
          "unreadEmails": 3,
          "totalThreads": 3,
          "unreadThreads": 3
        },
        {
          "id": "Mjkl012",
          "name": "Trash",
          "role": "trash",
          "totalEmails": 87,
          "unreadEmails": 12,
          "totalThreads": 75,
          "unreadThreads": 10
        }
      ],
      "notFound": []
    }, "m2"]
  ],
  "sessionState": "4288"
}
```

### 7.3 获取邮件正文

```
# 先查询 INBOX 中最新 3 封邮件，再获取正文
curl -s -X POST \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  https://mail.example.com/jmap/api \
  -d '{
  "using": [
    "urn:ietf:params:jmap:core",
    "urn:ietf:params:jmap:mail"
  ],
  "methodCalls": [
    ["Email/query", {
      "accountId": "u1",
      "filter": { "inMailbox": "Mabc123" },
      "sort": [{ "property": "receivedAt", "isAscending": false }],
      "position": 0,
      "limit": 3
    }, "q1"],
    ["Email/get", {
      "accountId": "u1",
      "#ids": {
        "resultOf": "q1",
        "name": "Email/query",
        "path": "/ids"
      },
      "properties": [
        "id", "subject", "from", "to", "receivedAt",
        "sentAt", "size", "isUnread", "hasAttachment",
        "preview", "textBody", "attachments"
      ],
      "fetchTextBodyValues": true
    }, "g1"]
  ]
}' | python3 -m json.tool
```

此处
`fetchTextBodyValues: true`
指示服务器在
`textBody`
中包含已 Base64 解码的纯文本内容片段，客户端无需单独下载
`blobId`
的原始 MIME 即可渲染正文预览。

### 7.4 增量同步：获取变更

```
# 传入上次记录的 Email state
curl -s -X POST \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  https://mail.example.com/jmap/api \
  -d '{
  "using": [
    "urn:ietf:params:jmap:core",
    "urn:ietf:params:jmap:mail"
  ],
  "methodCalls": [
    ["Email/changes", {
      "accountId": "u1",
      "sinceState": "9056",
      "maxChanges": 500
    }, "ch1"]
  ]
}' | python3 -m json.tool
```

**响应示例**
：

```
{
  "methodResponses": [
    ["Email/changes", {
      "accountId": "u1",
      "oldState": "9056",
      "newState": "9062",
      "hasMoreChanges": false,
      "created": ["Enew001", "Enew002"],
      "updated": ["Edef456"],
      "destroyed": ["Eold789"]
    }, "ch1"]
  ],
  "sessionState": "9062"
}
```

客户端随后对
`created + updated`
的 ID 集执行
`Email/get`
，本地删除
`destroyed`
集合中的邮件记录，更新状态令牌至
`"9062"`
——增量同步完成。

## 8. 实现与部署生态

JMAP 的部署生态在过去三年中显著成熟，以下为截至 2026 年中旬的主要实现。

**服务端**
：

* Apache James（Java 实现）自 3.7 版本起包含完整的 JMAP RFC 8621 支持，集成 Cassandra/Elasticsearch 后端。
* Cyrus IMAP（C 实现）在 3.6 版本中合并了 JMAP 支持模块，采用 murder 架构的分布式设计。
* Stalwart Mail Server（Rust 实现）从零构建的邮件服务器，JMAP 为原生协议而非 IMAP 之上的适配层，支持 FoundationDB 和 SQLite 后端、S3 兼容的 Blob 存储以及 OpenTelemetry 可观测性集成。

**客户端库**
：

* Rust：
  `jmap-client`
  — 全功能 JMAP 客户端，支持 Core / Mail / Calendar 规范。
* TypeScript：
  `jmap-client-ts`
  — 浏览器端原生 JMAP 客户端，支持 SSE 事件推送。
* Python：
  `python-jmap`
  — 社区维护的 Python 客户端，覆盖 RFC 8620 / 8621。

**代理与网关**
：

* `jmap-perl`
  ：IMAP/CardDAV/CalDAV-to-JMAP 协议代理，允许现有 IMAP 后端无需修改即可暴露 JMAP 接口。
* `jmap-proxy`
  （PHP）：类似的设计，面向中小规模部署的轻量级代理。

RFC 8887（JMAP for Calendars）和 RFC 9610（JMAP for Contacts）将 JMAP 的通用方法模型扩展到日历和联系人同步，为"一封协议替代 IMAP + CardDAV + CalDAV"提供了完整的规范基础。RFC 9007（JMAP over WebSocket）作为实验性传输绑定进一步拓展了实时双向同步的应用场景。

## 9. 迁移路径考量

从 IMAP 迁移到 JMAP 不需要一次性切换。常见的三种路径：

1. **双栈并行**
   ：JMAP 代理（如 jmap-perl）在 IMAP 后端前挂载 JMAP 接口。客户端可选 JMAP 或 IMAP，服务商逐步迁移用户。
2. **新客户端优先**
   ：Webmail 和移动端新客户端直连 JMAP，传统客户端继续走 IMAP。同一账户通过双协议访问，同步一致性由后端数据层保证。
3. **全量切换**
   ：自建邮件服务的组织，使用支持原生 JMAP 的服务器（如 Stalwart 或 Apache James）做一次性替代。现有 IMAP 客户端通过 JMAP-to-IMAP 反向代理继续访问（部分代理支持此方向，但不如正向代理成熟）。

迁移过程中需要关注的兼容点：自定义 IMAP 关键词在 JMAP 中映射为
`keywords`
字典；Sieve 脚本管理可通过 RFC 8620 通用方法模型访问（JMAP for Sieve Scripts 草案）；共享邮箱的 ACL 权限在 JMAP 中通过
`myRights`
和
`sharedWith`
字段表达，权限模型比 IMAP ACL（RFC 4314）更细粒度。

JMAP 的规范体系还在持续增长。IETF JMAP 工作组正在推进的草案包括 JMAP for Sieve Scripts、JMAP for Quotas、以及 JMAP for MDN（邮件回执）。每一次扩展都复用 RFC 8620 的四方法模型——意味着支持新功能需求的代码量远低于 IMAP 扩展所需的专用解析器和状态机。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/jmap-protocol-rfc8620.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
