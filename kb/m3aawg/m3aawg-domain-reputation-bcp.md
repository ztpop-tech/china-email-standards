---
title: "M3AAWG 域名声誉管理最佳实践：维护发信域可信度"
source: "https://ztpop.net/kb/m3aawg-domain-reputation-bcp.html"
license: CC-BY 4.0
---

# M3AAWG 域名声誉管理最佳实践：维护发信域可信度

## 概述

即便 SPF/DKIM/DMARC 全配齐，邮件仍可能进垃圾箱——因为接收方还看"声誉"。M3AAWG 域名声誉管理 BCP 说明：声誉是接收方基于历史行为对发信域/IP 的信任评分，由认证状态、投诉率、列表卫生、内容质量、发送规律共同决定。维护声誉是投递率工程的核心。

## 声誉的构成信号

| 信号 | 正向 | 负向 |
| --- | --- | --- |
| 认证 | SPF/DKIM/DMARC 对齐 | 无认证/伪造 |
| 投诉率 | <0.10% | ≥0.30%（Gmail 红线） |
| 列表卫生 | opt-in、活跃 | 购买名单、休眠 |
| 发送规律 | 稳定 IP/From | 突发高峰、IP 漂移 |
| 内容 | 合规 HTML、无误导 | 隐藏内容、欺骗主题 |

## 监控与工具

应定期查：Google Postmaster Tools、Microsoft SNDS 的域名/IP 声誉与投诉曲线；Spamhaus/SpamCop 黑名单状态；DMARC 聚合报告（rua）中的认证失败源。把"声誉下降"设为告警，先于用户投诉发现。

## 新域/IP 的预热

全新发信域或 IP 没有历史声誉，直接海量发送会被限流（如 Gmail 的 `4.7.28`）。应低速起步、随声誉提升逐步增量，并固定 From 与 IP 映射，避免频繁更换。

## 对信创邮件与政企的启示

政企对外发通知/账单时，应把"声誉"纳入邮件运维：独立子域发不同性质邮件（事务 vs 营销）、保持列表卫生、监控 Postmaster/SNDS、对 DMARC 报告做周度复盘。这直接决定重要邮件能否抵达用户。

### 相关主题

* [邮件送达率工程](/kb/email-deliverability-engineering.html)：声誉与认证协同
* [Gmail 送达率工程](/kb/gmail-deliverability-engineering.html)：Postmaster Tools 实战
* [Google Postmaster Tools 指南](/kb/google-postmaster-tools-guide.html)：声誉监控
* [Microsoft SNDS 发件人声誉](/kb/microsoft-snds-sender-reputation.html)：IP 信誉查询
* [DMARC 聚合报告](/kb/dmarc-aggregate-reporting.html)：rua 报告解读

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/m3aawg-domain-reputation-bcp.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
