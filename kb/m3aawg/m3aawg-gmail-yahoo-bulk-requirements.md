---
title: "M3AAWG《面向 Gmail/Yahoo 批量发件新规》：2024「无认证不进入」时代"
source: "https://ztpop.net/kb/m3aawg-gmail-yahoo-bulk-requirements.html"
license: CC-BY 4.0
---

# M3AAWG《面向 Gmail/Yahoo 批量发件新规》：2024「无认证不进入」时代

## 概述

2023 年 10 月 3 日，M3AAWG 成员公司 Google 与 Yahoo 双双发布公告：**2024 年起，「无认证不进入（No Auth, No Entry）」将成为向这两大邮箱提供方发送批量邮件的硬性规则**。两家均将"发件人验证"视为本次政策变更的核心——正如 Yahoo 所言，大量批量发件人未能正确加固与配置系统，使恶意行为者能在不被察觉的情况下滥用其资源；而依托邮件认证标准验证发件人身份，是破局关键。M3AAWG 长期将 SPF/DKIM/DMARC 视为最佳实践，此次公告把这些实践正式"法典化"。

## 批量发件人最低要求（逐项）

| 要求 | 说明 |
| --- | --- |
| 同时实现 SPF 与 DKIM | 邮件必须使用带 SPF 记录的 Return-Path 域发送，且消息须经 DKIM 签名 |
| 启用 DMARC | 邮件可见 From 域必须在 DNS 中存在 DMARC 策略记录；当前要求为 `p=none` |
| 对齐的 From 域 | 可见 From 域须与 DKIM 签名域或 SPF 域（或两者）对齐；**强烈建议对齐 DKIM 签名域**以缓解 SPF 升级攻击 |
| 正向/反向 DNS 一致（FCrDNS） | 发送 IP 须有有效 PTR 记录，且 PTR 解析回的域名能解析回原 IP（Forward-Confirmed Reverse DNS） |
| 一键退订 | 商业邮件须具备 RFC 8058 定义的"一键退订"能力 |
| 低垃圾率 | 用户举报垃圾率须低于 **0.3%** 阈值 |

## Google 同步升级 gmail.com 的 DMARC

另一项影响深远但关注度较低的变化：2024 年 Google 将 `gmail.com` 的 DMARC 策略从 `p=none` 升级到 `p=quarantine`。当前所有在 Google 平台之外、以 gmail.com 为 From 域发送的邮件本就未通过 DMARC 校验，但在 `p=none` 下影响有限；一旦改为 `p=quarantine`，这些邮件在任何尊重 DMARC 策略的域都会被送入垃圾箱。这进一步印证了"无认证不进入"的不可逆趋势。

## 对政企发件人的启示

对政府、金融、央企等大量发送**通知类邮件（账单、验证码、安全告警、召回通知）**的组织，新规直接关系到关键邮件能否送达。若发件域未对齐 DKIM、未配置 FCrDNS 或垃圾率偏高，重要通知将被静默丢入垃圾箱。建议在信创邮件替换或 Exchange 迁移时，把"DMARC 对齐 + DKIM 全量签名 + FCrDNS"作为邮件网关上线的前置验收项。

## 发件人自检清单

1. Return-Path 域有 SPF，且消息经 DKIM 签名；
2. 可见 From 域存在 DMARC 记录（至少 `p=none`，目标 `p=reject`）；
3. From 域与 DKIM 签名域对齐；
4. 发送 IP 配置 PTR 且 FCrDNS 闭环；
5. 商业邮件实现 RFC 8058 一键退订；
6. 持续监控用户举报垃圾率，控制在 0.3% 以下。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/m3aawg-gmail-yahoo-bulk-requirements.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
