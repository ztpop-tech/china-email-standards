---
title: "Exchange Server 生命周期完全时间线：2013/2016/2019 EOL 对邮件架构的影响"
source: "https://ztpop.net/kb/exchange-eol-complete-timeline.html"
license: CC-BY 4.0
---

# Exchange Server 生命周期完全时间线：2013/2016/2019 EOL 对邮件架构的影响

## 摘要

Exchange Server 2013 于 2023 年 4 月终止扩展支持，Exchange 2016 与 2019 于 2025 年 10 月同步终止扩展支持，标志着持续十余年的传统 Exchange 部署模式正式结束。本文系统梳理三个版本的生命周期时间线、累积更新（CU）与安全更新（SU）发布节奏，分析终止支持后的架构风险与迁移窗口期，并对比 Exchange Server SE 的新服务模型。全文基于 Microsoft 生命周期策略、Exchange Team Blog 官方公告及 NIST SP 800-45 邮件安全指南编写。

## 1. Exchange Server 生命周期模型概述

Microsoft 对 Exchange Server 实行固定生命周期策略（Fixed Lifecycle Policy），分为两个阶段：

* **主流支持（Mainstream Support）：** 提供功能更新、安全补丁与非安全修补程序，持续至少 5 年。
* **扩展支持（Extended Support）：** 仅提供安全更新，不再提供功能增强与非安全修复，持续 5 年。

自 2021 年起，Exchange 累积更新发布节奏从季度改为半年一次（H1/H2 CU），安全更新改为每月"补丁星期二"发布。2025 年 10 月 14 日后，Exchange 2016 与 2019 同时终止扩展支持，不再接收常规安全更新。已购买 ESU（Extended Security Update）的组织可继续获取安全更新至特定截止日期。

## 2. 各版本完整时间线

### 2.1 Exchange Server 2013

2.1 Exchange Server 2013

| 里程碑 | 日期 | 说明 |
| RTM | 2012-10-09 | 初始发布，引入 CAS/MBX 双角色架构 |
| CU1 | 2013-04-02 | 首个累积更新 |
| SP1 (CU4) | 2014-02-25 | 首个 Service Pack 级更新 |
| 最终 CU (CU23) | 2019-06-18 | 最后一个累积更新，版本 15.0.1497.2 |
| 主流支持终止 | 2018-04-10 | 不再提供功能更新 |
| 扩展支持终止 | 2023-04-11 | 不再提供安全更新，彻底 EOL |

Exchange 2013 在 CU23 后进入仅安全更新阶段，最后一个安全更新于 2023 年 4 月发布。至此，Exchange 2013 完全退出支持生命周期。

### 2.2 Exchange Server 2016

2.2 Exchange Server 2016

| 里程碑 | 日期 | 说明 |
| RTM | 2015-10-01 | 合并 CAS/MBX 角色为单一 Mailbox 角色 |
| CU1 | 2016-03-15 | 首个累积更新 |
| 最终 CU (CU23) | 2022-10-20 | 最后一个累积更新，版本 15.1.2507.6 |
| 主流支持终止 | 2020-10-13 | 不再提供功能与非安全修复 |
| 扩展支持终止 | 2025-10-14 | 不再提供安全更新 |

Exchange 2016 在 CU23 后仅接收每月安全更新，2025 年 10 月起仅 ESU 订户可继续获取安全更新。

### 2.3 Exchange Server 2019

2.3 Exchange Server 2019

| 里程碑 | 日期 | 说明 |
| RTM | 2018-10-22 | 要求 Windows Server 2019，支持最多 48 核 / 256 GB 内存 |
| CU15 最终 CU | 2024-03-12 | 最后一个累积更新，版本 15.2.1544.4 |
| 主流支持终止 | 2024-01-09 | 不再提供功能与非安全修复 |
| 扩展支持终止 | 2025-10-14 | 不再提供安全更新 |

Exchange 2019 CU15 是最后一个累积更新，后续仅发布安全更新与热修复。Exchange 2019 与 2016 在同一天（2025-10-14）终止扩展支持。

## 3. Windows Server 依赖关系

Exchange Server 各版本对底层 Windows Server 操作系统有严格的版本依赖关系：

3. Windows Server 依赖关系

| Exchange 版本 | 支持的 Windows Server 版本 | 备注 |
| 2013 | 2008 R2 SP1, 2012, 2012 R2 | 不支持 Windows Server 2016+ |
| 2016 | 2012 R2, 2016 | CU3 起支持 Windows Server 2016 |
| 2019 | 2019, 2022 | 推荐 Server Core 安装 |
| SE (订阅版) | 2022, 2025 | RTM 基于 2019 CU15 代码，从 SE CU1 起引入变更 |

Windows Server 操作系统本身也有独立的生命周期。例如 Windows Server 2012 R2 扩展支持于 2023 年 10 月终止，进一步限缩了 Exchange 2016 在旧平台上的合规运行空间。

## 4. CU 与 SU 发布节奏演变

Exchange Server 的更新模型经历三次重大调整：

* **2012-2020（季度 CU 模型）：** Exchange 2013/2016 每季度发布一次累积更新，包含安全与非安全修复。Exchange 2016 CU 期间从 CU1（2016-03）到 CU23（2022-10）共发布 23 个 CU。
* **2021-2025（半年 CU + 月 SU 模型）：** 2021 年起改为半年发布累积更新（H1/H2），安全修复通过每月独立 SU 交付。此模型允许管理员在不升级 CU 的情况下安装安全更新。
* **2025 年起（SE 订阅模型）：** Exchange Server SE 采用订阅式更新流，每年 2 次 CU 功能更新加每月安全更新，与 Exchange Online 更新节奏对齐。

以下命令查询当前 Exchange 构建版本号：

```
# Exchange Management Shell
Get-ExchangeServer | Format-List Name, AdminDisplayVersion

# 或使用 HealthChecker 脚本（推荐）
.\HealthChecker.ps1 -Server MBX01
```

## 5. Exchange Server SE 路线对比

Exchange Server SE（订阅版）于 2025 年 10 月发布 RTM，代码等价于 Exchange 2019 CU15。关键区别：

* **升级路径：** Exchange 2019 CU14/CU15 可直接就地升级至 SE。Exchange 2016 必须先升级至 2019 CU14/CU15，再迁移至 SE。
* **许可模型：** SE 采用订阅许可，不再提供永久授权。未续订的组织停止接收安全更新。
* **维护节奏：** SE CU1 起开始引入新功能变更；RTM 阶段仅等同于 2019 CU15 的重标记版本。
* **共存支持：** SE 支持与 Exchange 2019 共存（同组织内），但不支持与 2016 或更早版本共存。

## 6. EOL 后的迁移窗口期评估

对运行 Exchange 2016/2019 的组织而言，2025 年 10 月后的选择如下：

6. EOL 后的迁移窗口期评估

| 方案 | 适合场景 | 风险等级 |
| 购买 ESU，原地保留 | 短期过渡（1-2 年），需维持现有环境 | 中 — ESU 到期后无安全更新 |
| 就地升级至 SE | 运行 Exchange 2019 CU14+ 的组织 | 低 — 官方支持的升级路径 |
| 迁移至替代邮件系统 | 不再需要 Exchange 特性栈的组织 | 中 — 需规划数据迁移与共存 |
| 构建全新 SE 环境并迁移 | Exchange 2016 用户，无法就地升级 | 中 — 需要新硬件与共存期 |

NGINX 反向代理/SMTP 网关层的配置无需因后端 Exchange 版本变更而大幅修改，这降低了架构过渡的复杂度。关键在于 Active Directory 架构扩展与证书规划的提前执行。

## 7. 生命周期终止的安全影响要点

扩展支持终止后，以下风险显著上升：

* 未修补的远程代码执行（RCE）漏洞将永远存在可利用窗口。2021 年 ProxyLogon（CVE-2021-26855）事件表明，Exchange Server 漏洞的价值与利用速度极高。
* 未购买 ESU 的组织在 2025 年 10 月 14 日后将不接收任何安全更新，包括关键 CVSS ≥ 9.0 漏洞。
* 合规性要求（如等保 2.0、NIST SP 800-53）通常要求运行在支持周期内的软件版本。

详细安全分析见本系列文章《Exchange Server EOL 后的安全态势：漏洞管理、补丁策略与加固方案》。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/exchange-eol-complete-timeline.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
