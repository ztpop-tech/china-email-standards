---
title: "Google 批量发件方指南（2024）：SPF/DKIM/DMARC 强制与 0.30% 投诉红线"
source: "https://ztpop.net/kb/google-email-sender-guidelines-2024.html"
license: CC-BY 4.0
---

# Google 批量发件方指南（2024）：SPF/DKIM/DMARC 强制与 0.30% 投诉红线

## 概述

Google 自 2024 年起对个人 Gmail 实施更严格的发件要求，核心针对**日发送量 ≥5,000 封**的批量发件方。这套要求与 Yahoo 同步（见 M3AAWG 汇总），是任何对外群发系统（含信创邮件、企业通知）必须对齐的合规基线。未达标者将面临进入垃圾箱甚至拒收（`5.7.26`）。

## 认证三件套（强制）

* **SPF 或 DKIM**：所有发件方必备。
* **SPF + DKIM + DMARC**：批量发件方必须三者齐全。
* **DMARC 对齐**：认证域须与 `From:` 组织域一致（组织级对齐），建议开启 rua/ruf 报告。
* **DKIM 密钥**：向 Gmail 发送需 ≥1024 位，推荐 2048 位（见 RFC 8301）。

## 投诉率红线

通过 Postmaster Tools 监控域名投诉率：**推荐维持在 <0.10%，绝对不得超过 0.30%**。达到或高于 0.30% 将严重影响送达，且改善后需时间才能恢复。这与 M3AAWG 域名声誉管理完全一致。

## 一键退订（RFC 8058）

营销/订阅类邮件必须支持一键退订，信头同时包含：

```
List-Unsubscribe-Post: List-Unsubscribe=One-Click
List-Unsubscribe: <https://example.com/u?token=xyz>
```

用户点击后发件方收到 POST 即完成退订，传统"访问网页退订"不可替代。这对应本站 RFC 8058 专文。

## 格式与列表卫生

* `From:` 仅一个地址；单实例头只出现一次；每封含有效 `Message-ID`。
* 禁用误导主题/显示名（假 `Re:/Fwd:`）、隐藏内容。
* 必须 opt-in（双重确认最佳）、定期重确认、清理不活跃用户；禁购名单、禁默认勾选。
* 发送 IP 必须有 PTR 且正反向 DNS 匹配；同类型邮件固定 From 与 IP，慢速提量。
* 传输须用 TLS（2023-12 起强制）。

## 对信创邮件与政企的启示

政企用信创邮件系统向客户/会员群发通知时，应将上述要求写入发信规范：独立子域、DMARC p=quarantine/reject、RFC 8058 退订、Postmaster 监控投诉率。未达标会直接损害对外沟通效果。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/google-email-sender-guidelines-2024.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
