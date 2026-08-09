---
title: "Microsoft 批量发件人要求（2025-05-05 生效）：Outlook.com 5,000 封/日阈值与 SPF/DKIM/DMARC 强制 · ztpop 邮件技术知识库"
source: "https://ztpop.net/kb/microsoft-bulk-sender-requirements.html"
license: CC-BY 4.0
---

# Microsoft 批量发件人要求（2025-05-05 生效）：Outlook.com 5,000 封/日阈值与 SPF/DKIM/DMARC 强制 · ztpop 邮件技术知识库

## 一、背景：第三家强制方

继 Google 与 Yahoo 于 2024 年推出批量发件人要求后，微软于 2025 年 4 月 2 日在 Microsoft Defender for Office 365 Blog 发布官方公告《Strengthening Email Ecosystem: Outlook's New Requirements for High-Volume Senders》，宣布对日发送量超过 **5,000 封**至 Outlook.com 消费者域（含 hotmail.com、live.com、outlook.com）的批量发件人实施强制认证要求，**2025 年 5 月 5 日起正式执行**。这是继 Google、Yahoo 之后第三家实施此类强制政策的大型邮箱服务商。

适用范围：仅针对发送至 Outlook.com 消费者邮箱（个人免费账户）的邮件；Exchange Online 企业邮箱另有独立的发件人策略。

## 二、强制要求清单（官方公告）

| 要求 | 官方表述 | 对应标准 |
| --- | --- | --- |
| **SPF 必须通过** | Must Pass for the sending domain；域名 DNS 记录应准确列出授权 IP/主机 | RFC 7208 |
| **DKIM 必须通过** | Must Pass to validate email integrity and authenticity | RFC 6376 |
| **DMARC 至少 p=none** | At least p=none，且与 SPF 或 DKIM 对齐（preferably both） | RFC 9989（原 RFC 7489） |
| **传输加密** | 建议使用 TLS 传输邮件（官方 FAQ 引用） | RFC 8461 / RFC 7672 |
| **正反向 DNS（FCrDNS）** | 发送 IP 的 PTR 记录应匹配其正向 DNS | RFC 1912 |
| **退订链接** | 营销/批量邮件必须提供清晰可用退订链接 | RFC 8058 |
| **垃圾投诉率** | 保持低垃圾投诉率，建议通过 JMRP 监控 | — |

## 三、执行时间线与动作

1. **2025-04-02**：微软发布官方公告，鼓励批量发件人审查并更新 SPF/DKIM/DMARC 记录。
2. **2025-05-05 起**：不合规邮件先被路由至**垃圾箱（Junk）**，给发件人整改机会。
3. **后续（日期另行公告）**：不合规邮件将被**拒绝**，SMTP 错误码：`550; 5.7.515 Access denied, sending domain [SendingDomain] does not meet the required authentication level`。

官方 2025-04-29 更新说明：曾讨论过直接拒绝，但最终决定 5 月 5 日先执行「入垃圾箱」，拒绝动作另行宣布，避免收件人与发件人困惑。

## 四、DMARC 对齐要求解读

微软要求 DMARC 记录至少为 `p=none`，且 SPF 或 DKIM 认证域与 RFC5322.From 域对齐（relaxed 或 strict 均可）。这意味着：

* 仅通过 SPF 认证时，MAIL FROM 域须与 From 域对齐。
* 仅通过 DKIM 认证时，d= 域须与 From 域对齐。
* SPF+DKIM 双认证（且至少一个对齐）为最稳妥方案——官方「preferably both」。

官方 FAQ 特别提醒：**转发/邮件列表会破坏 DMARC 对齐**（SPF 在转发后通常失败），推荐使用 ARC（RFC 8617）保留原始认证结果，防止合法转发邮件被误判。

## 五、与 Google/Yahoo 要求的对比

| 维度 | Google（Gmail） | Yahoo | Microsoft（Outlook.com） |
| --- | --- | --- | --- |
| 生效时间 | 2024-02/06 | 2024-02/06 | 2025-05-05 |
| 日发送阈值 | ≥5,000 封 | ≥5,000 封 | >5,000 封 |
| SPF | 必须（或 DKIM） | 必须（或 DKIM） | 必须通过 |
| DKIM | 批量必须 | 批量必须 | 必须通过 |
| DMARC | 批量必须，建议 p=quarantine/reject | 批量必须 | 至少 p=none + 对齐 |
| 投诉率 | <0.30% | <0.30% | 建议监控（JMRP） |
| 一键退订 | 强制（RFC 8058） | 强制 | 强制（退订链接） |
| TLS | 强制 | 强制 | 建议 |
| 不合规后果 | 入垃圾箱/拒收（5.7.26） | 入垃圾箱/拒收 | 先垃圾箱，后 550 5.7.515 |

## 六、合规检查清单

1. 确认外发量：每日是否发送 >5,000 封至 Outlook.com/Hotmail.com/Live.com 收件人。
2. SPF 记录：DNS 中正确列出所有发送 IP，查询 ≤10 次，必要时展平。
3. DKIM：为发送域配置密钥（d= 域与 From 域对齐）。
4. DMARC：发布 `v=DMARC1; p=none; rua=...` 起步，确认对齐后逐步升级。
5. 退订：营销邮件实现 RFC 8058 一键退订。
6. 监控：注册 JMRP 监控投诉；定期清理列表。
7. 转发场景：配置 ARC（RFC 8617）或使用 SRS 重写 MAIL FROM。

## 七、对中国发件方与信创系统的启示

* 面向海外 Outlook.com 收件人的系统，应将微软要求纳入发信合规基线——Google/Yahoo/Microsoft 三家认证要求基本一致，一套 SPF/DKIM/DMARC 配置即可同时满足。
* 重点检查 DMARC 对齐：国内「网关代发」场景（From 为自有域、实际经第三方网关发送）必须确保网关配置了与 From 域对齐的 DKIM 签名。
* 550 5.7.515 是微软专属拒收码，收到该错误应优先检查 SPF/DKIM/DMARC 记录。
* 对海外订阅邮件须实现 RFC 8058 一键退订。

## 八、官方信息来源

* 微软官方公告（2025-04-02，Microsoft Defender for Office 365 Blog）：《Strengthening Email Ecosystem: Outlook's New Requirements for High-Volume Senders》（含 2025-04-29 更新说明）。
* Outlook.com Postmaster 官方站点：sendersupport.olc.protection.outlook.com/pm/，Announcements 页确认 2025-05-05 执行日期。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/microsoft-bulk-sender-requirements.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
