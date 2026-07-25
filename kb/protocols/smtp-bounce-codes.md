---
title: "IETF RFC 5321 / RFC 3463 / RFC 6647 · 运维必读"
source: "https://ztpop.net/kb/smtp-bounce-codes.html"
license: CC-BY 4.0
---

# IETF RFC 5321 / RFC 3463 / RFC 6647 · 运维必读

## 摘要

SMTP 应答码是邮件投递过程中接收方 MTA 返回的状态信号。正确理解应答码的类别、分组与增强状态码体系（RFC 3463），是诊断邮件投递故障的基础能力。本文系统梳理 4xx 临时失败与 5xx 永久失败两个大类，涵盖最常见的 421、450、451、550、554 等代码的具体含义、典型场景与排查路径。

## 1. SMTP 应答码结构

### 1.1 三位数字编码

SMTP 协议使用三位数字作为应答码（RFC 5321 §4.2），每位数字编码特定含义：

* **第 1 位（类别）**
  ：2=成功，3=需要更多信息，4=临时失败，5=永久失败
* **第 2 位（主题分组）**
  ：0=语法，1=信息，2=连接，3=未使用，4=未使用，5=邮件系统
* **第 3 位（精确分类）**
  ：同组内的细化区分

### 1.2 增强状态码

RFC 3463 在三位数字码之上增加了
`X.Y.Z`
格式的增强状态码。例如
`550 5.7.1 Delivery not authorized`
中：

* **X**
  = 类别（4/5）
* **Y**
  = 主题（0=未定义, 1=寻址, 2=邮箱, 3=邮件系统, 7=安全策略）
* **Z**
  = 具体细节

## 2. 临时失败（4xx）

### 2.1 421 服务暂时不可用

**语义**
：接收方服务器当前无法继续提供服务，通常与连接频率限制或资源耗尽相关。

**常见场景**
：

* 连接频率超限：接收方限制了单 IP 的并发连接数或每分钟连接数
* 服务维护中：MTA 正在经历计划内重启
* 系统资源耗尽：磁盘、内存不足导致无法接收新邮件

**处置**
：降低发信并发数（建议 ≤ 5 个并发连接），减小每批次发送量。MTA 应自动按指数退避策略重试。

### 2.2 450 邮箱暂时不可用

**语义**
：请求的邮箱当前不可用，最常见原因是灰名单（Greylisting）。

**灰名单机制（RFC 6647）**
：接收方 MTA 对新出现的发信三元组（IP + MAIL FROM + RCPT TO）首次连接返回 450 临时拒绝，要求发信方延迟后重试。合法 MTA 会按要求重试，而多数垃圾邮件发送软件不会维护重试队列。

**配置建议**
：MTA 初始重试间隔建议 1-5 分钟，逐步递增。不应立即重发，否则可能被视为行为异常。

国内常见的 450 场景还包括：腾讯企业邮箱返回
`450 4.7.1 Client host rejected`
（无 PTR 记录）；网易邮箱返回
`450 DT:SPM`
（内容触发反垃圾规则）。

### 2.3 451 / 452 资源临时不足

**451**
：请求操作因本地处理错误中止。可能为 MTA 内部错误，通常无需发信方干预，接收方会自动恢复。

**452**
：系统存储空间不足。接收方磁盘已满或者达到存储配额上限。出现此代码说明接收方服务器存在运维问题，而非发信方问题。

## 3. 永久失败（5xx）

### 3.1 550 请求操作未执行

550 是使用范围最广的永久失败代码，其具体含义由接收方附加的文本描述决定。

3.1 550 请求操作未执行

| 增强状态码 | 文本描述 | 含义 |
| `550 5.1.1` | Mailbox unavailable | 收件邮箱不存在或已禁用 |
| `550 5.1.8` | Access denied, bad outbound sender | 发信账户被标记（Exchange Online 受限用户） |
| `550 5.7.1` | Relay denied | 客户端未通过 SMTP 认证尝试中继转发 |
| `550 5.7.0` | Message rejected due to content | 邮件内容命中反垃圾策略 |
| `550 5.7.25` | No PTR record | 发信 IP 缺少 PTR 反向解析（Gmail） |
| `550 5.7.26` | Not authenticated | 未通过 SPF 或 DKIM 认证（Gmail） |
| `550 5.7.708` | Traffic not accepted | IP 信誉过低（Exchange Online） |

### 3.2 554 交易失败

**语义**
：交易被拒绝，通常与反垃圾邮件策略相关。

**典型场景**
：

* `554 No SMTP service`
  — Hotmail/Outlook.com 对无 PTR 记录 IP 的标准拒绝（RFC 1912 §2.1）
* `554 Bad DNS PTR resource record`
  — PTR 存在但无法正向解析闭环
* `554 5.7.1 Blocked using Spamhaus`
  — IP 或域名在 Spamhaus 数据库中（RFC 5782 DNSBL）
* `554 5.7.1 Blocked using Barracuda Reputation`
  — IP 在 Barracuda BRBL 中
* `554 Message rejected for policy reasons`
  — 接收方自定义策略拒绝（如禁止特定国家/地区的 IP）

### 3.3 552 超出大小限制

**语义**
：邮件体积超过接收方允许的最大值。Google 限制为 25MB（编码后），Exchange Online 默认 35MB。

需注意 SMTP 传输中的 Base64 编码会导致体积膨胀约 33%。

## 4. 排查方法论

收到退信后，按以下优先级排查：

1. **阅读退信邮件正文**
   ：接收方附加的文本描述（如 "KB930521 MSExchange" 等内部参考编号）比泛化的三位代码更有诊断价值。
2. **区分临时失败 vs 永久失败**
   ：4xx 通常不需要人工干预，等待 MTA 自动重试；5xx 需要定位并修复根因。
3. **检查 Authentication-Results 头**
   ：如果原本能发但突然退信，提取退信邮件头中的
   `Authentication-Results`
   行，确认 SPF/DKIM/DMARC 仍处于 pass 状态。
4. **查询黑名单**
   ：用 mxtoolbox.com 或 spamhaus.org 查询发信 IP。554 + "blocked" 关键词几乎一定指向 DNSBL 拦截。
5. **验证 DNS 记录完整性**
   ：MX、SPF、DKIM、PTR（via
   `dig -x`
   ）四项全部确认无误。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/smtp-bounce-codes.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
