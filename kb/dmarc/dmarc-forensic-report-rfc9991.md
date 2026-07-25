---
title: "DMARC Forensic Report 深度解读 · RFC 9991"
source: "https://ztpop.net/kb/dmarc-forensic-report-rfc9991.html"
mirror_date: 2026-07-25
license: CC-BY 4.0
---

# DMARC Forensic Report 深度解读 · RFC 9991

## 一、引言

2026 年 5 月正式发布的 RFC 9991 是 DMARC 标准发展的重要里程碑。它替代了 RFC 7489，并将 **Forensic Report（故障报告）**作为独立规范进行标准化。Forensic Report（也称 Failure Report）与聚合报告（Aggregate Report）不同，它针对每一封认证失败的邮件生成详细的个体报告，包含完整的邮件头部甚至部分内容。

RFC 9991 由 DMARC.org 工作组编辑完成，同时更新了 RFC 6591（AFRF 格式规范），使其格式协议能够承载 DMARC 故障报告。本文将深入解读 Forensic Report 的格式、部署与隐私考量。

## 二、Forensic Report vs Aggregate Report

| 对比维度 | Aggregate Report（聚合报告） | Forensic Report（故障报告） |
| --- | --- | --- |
| 数据粒度 | 按域、按时间段汇总 | 每封失败邮件逐条报告 |
| 典型发送频率 | 每日一次 | 实时或近实时 |
| 是否包含邮件内容 | 否（仅统计数据） | 是（按策略包含头部/全文） |
| 隐私风险 | 低 | 高（可能泄露用户通信内容） |
| 协议格式 | XML（RFC 7489/指定schema） | AFRF（RFC 6591 / RFC 9991） |

## 三、Forensic Report 的格式定义

### 3.1 AFRF 格式基础

RFC 9991 第 4 节定义了如何使用 **Abuse Feedback Report Format (AFRF)** 封装 DMARC 故障报告。AFRF 最初由 RFC 5965 标准化，后经 RFC 6591 扩展以支持 DKIM/DMARC 反馈。RFC 9991 进一步扩展以支持 SPF 对齐失败等情况。

标准 Forensic Report 的 MIME 结构为：

* **第一部分（text/plain 或 text/html）** — 人类可读的故障摘要。
* **第二部分（message/feedback-report）** — 结构化反馈字段集合，包括：  
  `Feedback-Type: dmarc-failure`  
  `User-Agent: dmarc-failure/1.0`  
  `Version: 1.0`  
  `Original-Mail-From: <>`  
  `Arrival-Date: Tue, 21 Jul 2026 02:15:00 +0800`
* **可选内容部分** — 原始邮件的头部或部分正文。

### 3.2 新增字段（RFC 9991）

RFC 9991 引入或明确了以下字段：

* `Authentication-Results` — 接收 MTA 执行 SPF/DKIM/DMARC 认证的详细结果。
* `Original-Envelope-Id` — 投递信封标识，用于关联邮件投递日志。
* `DKIM-Domain` / `DKIM-Identity` — 指示 DKIM 签名的域名和身份。
* `SPF-Domain` / `SPF-Result` — 指示 SPF 检查的域名和结果。

## 四、DNS 发布与接收配置

### 4.1 DMARC 记录中的 ruaf 标签

RFC 9991 第 6.2 节定义了 `ruaf` 标签，用于指定 Forensic Report 的接收 URI。与聚合报告的 `rua` 不同，`ruaf` 是可选的——域所有者可以选择不接收 Forensic Report 以避免隐私风险。

示例 DMARC DNS 记录：

```
v=DMARC1; p=reject; rua=mailto:dmarc-aggregate@example.com;
ruaf=mailto:dmarc-forensic@example.com; fo=1
```

### 4.2 fo 标签的细化

`fo`（Failure Reporting Option）标签控制何时发送 Forensic Report。RFC 9991 第 6.3 节明确了可取值：

* `0` — 所有认证检查都失败时才发送（默认）。
* `1` — 任一认证检查失败即发送。
* `d` — 仅 DKIM 失败时发送。
* `s` — 仅 SPF 失败时发送。
* 值可组合，如 `fo=1:s` 表示 SPF 失败或任一检查失败时发送。

## 五、隐私与安全考量

RFC 9991 第 10 节用大量篇幅讨论了 Forensic Report 的隐私风险。由于报告可能包含原始邮件的头部甚至正文，接收报告的一方可能泄露用户隐私。M3AAWG 的《DMARC Forensic Report Handling Best Practices》建议：

* 仅在 `p=quarantine` 或 `p=reject` 策略下启用 Forensic Report。
* 对报告接收邮箱实施严格的访问控制与审计。
* 考虑在 RET 策略中使用 `HDRS` 而不是 `FULL`（类比 [DSN 的 RET 参数](/kb/smtp-dsn-rfc3461.html)）。
* 使用 TLS 加密传输 Forensic Report（MTA-STS 或 DANE 强制）。

## 六、运维建议

在实际运维中，大规模部署 Forensic Report 可能面临报告量巨大的挑战。建议：

* 先使用 `fo=1` 进行短期试点，观察报告量后再调整。
* 使用专用的 Forensic Report 解析工具（如 OpenDMARC 或第三方服务）自动化处理。
* 结合 [DMARC Aggregate Report 分析](/kb/dmarc-aggregate-reporting.html)，优先解决聚合报告中显示的高频失败域。

### 相关文章

* [DMARC 配置指南](/kb/dmarc-guide.html)
* [DMARC 聚合报告解读](/kb/dmarc-aggregate-reporting.html)
* [邮件认证与报告体系](/kb/email-auth-reporting.html)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/dmarc-forensic-report-rfc9991.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
