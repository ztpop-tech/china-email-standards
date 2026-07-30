---
title: "邮件头分析与取证：Received 链、SPF/DKIM/DMARC 认证结果解析与伪造识别"
source: "https://ztpop.net/kb/email-header-analysis-full-guide.html"
license: CC-BY 4.0
---

# 邮件头分析与取证：Received 链、SPF/DKIM/DMARC 认证结果解析与伪造识别

参考 RFC 5321、RFC 5322 及邮件取证最佳实践

邮件头（Email Header）是邮件取证的基础数据源。每封邮件从发件人终端到收件人服务器，经过的每一跳 MTA 都会在邮件头中添加 Received 字段，形成完整的投递路径。通过分析邮件头，可以追溯邮件的真实来源、识别伪造邮件的异常特征。

## 邮件头结构

### 关键字段解析

| 字段 | 含义 | 重要性 |
| --- | --- | --- |
| Received | 投递路径中的每一跳记录 | ★★★★★ |
| Authentication-Results | SPF/DKIM/DMARC 认证结果 | ★★★★★ |
| DKIM-Signature | DKIM 签名头部 | ★★★★★ |
| ARC-Seal/ARC-Message-Signature | AR 链（认证转发链） | ★★★★ |
| Received-SPF | SPF 检查结果 | ★★★★ |
| Return-Path | 退信地址（信封 From） | ★★★★ |
| From | 发件人显示地址 | ★★★★ |
| Reply-To | 回复地址 | ★★★ |
| Message-ID | 邮件唯一标识 | ★★★ |
| Date | 发件时间戳 | ★★★ |

## Received 链分析

Received 字段从最底下一行（第一跳）到最上边一行（最后一跳）的顺序记录了邮件的完整传输路径。分析 Received 链时，需要重点关注：

### 时间戳一致性检查

每跳 Received 的时间戳应处于递增状态，且不能出现不合理的时间跳跃。如果某跳的时间戳比前一跳更早，或两跳之间间隔极短（如 1 秒内跨越两个城市的服务器），则可能存在邮件头伪造。

### IP 地址检查

每个 Received 字段的 from/by 中的数据来源 IP 应可追溯至邮件的实际传输路径。检查 IP 是否属于已知的邮件服务商，是否与预期发件人的 IP 段一致。使用 WHOIS 或 DNS 反向查询 Received IP 的所有者。

### Return-Path vs From 不一致检测

发件人伪造通常表现为 Return-Path（信封发件人）与 From 头（显示发件人）使用不同的域。虽然合法的邮件转发也会产生这种不一致，但结合 SPF 认证结果可以判断是否为攻击。

## SPF/DKIM/DMARC 认证结果分析

### Authentication-Results 字段

接收方服务器在每个 Received 字段之后附加 SPF/DKIM/DMARC 的认证结果。这些结果的格式由 RFC 8601 定义，格式为：

```
Authentication-Results: mx.example.com;
       spf=pass (sender IP is 203.0.113.5) smtp.mailfrom=sender.com;
       dkim=pass (1024-bit key) header.d=sender.com header.i=@sender.com;
       dmarc=pass (p=reject) header.from=sender.com
```

### ARC 链分析

ARC（Authenticated Received Chain, RFC 8617）允许在邮件转发过程中保留原始认证结果。如果一封邮件经过转发后 SPF 失败但 ARC 链完整，可以信任原始认证结果。

## 典型邮件头伪造识别

### 显示名欺骗

攻击者将 From 字段的显示名设置为受害者熟悉的人名（如 "CEO Zhang San"），但实际邮件地址是攻击者控制的域。这种攻击可能通过 SPF/DKIM 认证（因为攻击者控制自己的域），但 From 域与预期不符。

### 时间戳异常

邮件头的 Date 字段与实际 Received 链时间戳相差数天或数小时，可能是攻击者为隐藏真实时间而伪造的。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-header-analysis-full-guide.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
