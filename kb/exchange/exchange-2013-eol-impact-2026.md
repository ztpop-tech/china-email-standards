---
title: "Exchange 2013 EOL 影响与迁移路径 · 2026 年全面分析"
source: "https://ztpop.net/kb/exchange-2013-eol-impact-2026.html"
license: CC-BY 4.0
---

# Exchange 2013 EOL 影响与迁移路径 · 2026 年全面分析

## 一、背景

Microsoft Exchange Server 2013 于 2013 年 1 月发布，其主流支持于 2018 年 4 月结束，扩展支持（Extended Support）于 **2023 年 4 月 11 日**正式终止。到 2026 年 7 月，Exchange 2013 已经结束所有官方安全更新超过 3 年（三年 EOL）。这意味着运行 Exchange 2013 的组织自 2023 年 4 月起就不再收到安全补丁——包括关键级别的远程代码执行漏洞。

根据微软官方生命周期政策，Exchange Server 遵循固定生命周期策略，没有为 Exchange 2013 提供付费的扩展安全更新（ESU）。这与 Exchange 2010（已于 2020 年 10 月 EOL）、Exchange 2007 的情况一致。

## 二、持续运行 Exchange 2013 的风险

### 2.1 安全风险

Exchange Server 是攻击者的高价值目标。2021 年的 ProxyLogon（CVE-2021-26855 等）和后续的 ProxyShell（CVE-2021-34473 等）漏洞揭示了针对 Exchange 的攻击面之大。EOL 后的 Exchange 2013 面临：

* **无补丁的 0-day 漏洞** — 微软不再发布任何安全更新。
* **合规风险** — 等保 2.0、GB/T 22239-2019 等标准要求系统在支持周期内运行。
* **数据泄露风险** — EOL 系统上继续承载邮件数据将大幅增加泄露可能性。

### 2.2 互操作性衰退

随着外部邮件服务商（如 Gmail、Outlook.com）逐步提升 TLS 要求（最低 TLS 1.2），Exchange 2013 默认配置的操作系统（Windows Server 2012 R2，其扩展支持已于 2023 年 10 月结束）和 .NET 版本可能无法满足最新的加密协议要求。
[TLS 1.3](/kb/tls-1-3-mta-sts-impact.html) 在 2026 年已成为 SMTP 传输的主流，Exchange 2013 不支持 TLS 1.3，这将导致发送到强制要求 TLS 1.3 的接收方时出现投递失败。

## 三、迁移路径

### 3.1 迁移到 Exchange Online（Microsoft 365）

对于已采用或计划采用 Microsoft 365 的组织，可使用混合迁移或完全迁移方式：

* **混合迁移** — 使用 HCW（Hybrid Configuration Wizard）建立 Exchange 2013 → Exchange Online 的混合部署，共享命名空间和空闲忙信息。注意：Exchange 2013 的混合最小版本要求是 CU23（2019 年 6 月发布），但 CU23 本身也已超出支持范围。
* **直接迁移** — 使用 IMAP 或 cutover 迁移将邮箱批量迁移到 Exchange Online。此方法不保留日历代理等高级混合特性。

### 3.2 迁移到 Exchange 2019 或 Exchange SE

Exchange 2019 是目前最新的本地部署版本，Exchange Server Subscription Edition（SE）预计将作为订阅制版本推出。迁移路径：

* 需先部署 Exchange 2019 组织，建立共存关系。
* Exchange 2013 和 Exchange 2019 之间支持 SMTP 邮件流共存和日历代理。
* 邮箱逐批从 2013 数据库移动到 2019 数据库。
* 参考[Exchange 共存与互操作](/kb/exchange-coexistence-interop.html)的详细说明。

### 3.3 迁移到信创邮件系统

对于中国市场的党政机关和关键基础设施企业，**信创迁移**是政策驱动的优先选项。从 Exchange 2013 迁移到信创邮件系统的标准路径：

* **方案一：双栈并行** — 部署信创邮件系统（如昆仑邮件系统），与 Exchange 2013 并行运行，通过 SMTP 双向路由同步邮件流，逐步将用户从 Exchange 转移到信创系统。
* **方案二：IMAP 迁移** — 使用 IMAP 协议将 Exchange 2013 邮箱中的邮件拉取到信创系统。适合用户较少、对日历不敏感的场景。[IMAP 并发性能优化](/kb/imap-concurrency-optimization.html)在此类迁移中至关重要。
* **方案三：增量同步方案** — 通过 IMAP IDLE 或第三方迁移工具实现增量同步，先将历史邮件批量导入，再持续同步增量。详见[邮件迁移指南](/kb/email-migration-guide.html)。

## 四、时间线建议

| 阶段 | 时间 | 行动项 |
| --- | --- | --- |
| 评估 | 2026 Q3 | 清点 Exchange 2013 服务器、邮箱数、数据库大小；安全审计 |
| 选型 | 2026 Q3 | 确定目标平台：Exchange Online / Exchange SE / 信创系统 |
| 小规模试迁移 | 2026 Q4 | 选择非关键用户试点迁移，观察邮件流和客户端兼容性 |
| 全面迁移 | 2027 H1 | 分批迁移全部邮箱，停用 Exchange 2013 服务器 |
| 下线 | 2027 Q2 | 彻底卸载 Exchange 2013，移除 DNS MX/A 记录 |

## 五、总结

Exchange 2013 的 EOL 已经超过三年，持续运行的安全和合规风险不可接受。企业应在 2026 年内启动迁移评估，根据自身情况选择最合适的迁移路径。对于中国的党政机关和信创试点单位，迁移到合规的信创邮件系统是最符合政策和安全要求的长期方案。

### 相关文章

* [邮件迁移指南](/kb/email-migration-guide.html)
* [Exchange EOL 迁移规划](/kb/exchange-eol-migration-guide.html)
* [从 Exchange 迁移到信创邮件系统](/kb/xinchuang-email-migration-from-exchange.html)
* [Exchange 共存与互操作](/kb/exchange-coexistence-interop.html)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/exchange-2013-eol-impact-2026.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
