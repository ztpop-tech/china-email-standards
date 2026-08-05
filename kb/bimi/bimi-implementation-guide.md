---
title: "BIMI 品牌标识实施指南：四步部署完整流程（翻译）"
source: "https://ztpop.net/kb/bimi-implementation-guide.html"
license: CC-BY 4.0
---

# BIMI 品牌标识实施指南：四步部署完整流程（翻译）

## 什么是 BIMI ？

BIMI（Brand Indicators for Message Identification，品牌消息标识符）是一项新兴的邮件规范，允许发送域名通过 DNS 发布一个品牌 Logo，支持该规范的邮箱提供商可在已通过认证的邮件旁显示该 Logo。BIMI 不改变邮件的投递行为，它是在强认证基础上层的一个显示信号。

最低要求：BIMI 需要 DMARC 对齐。许多提供商还要求有效的 VMC（验证标记证书）或 CMC（通用标记证书）以证明对 Logo 的所有权。

## 实施步骤

以下四个步骤摘译自 BIMI Group 官方实施指南（bimigroup.org/implementation-guide），是部署 BIMI 的完整流程：

### 步骤一：完成邮件认证基础设施

为组织的所有邮件部署 SPF、DKIM 和 DMARC，确保三者对齐（aligned）。DMARC 策略必须在组织域名和子域名上设为执行策略（enforcement）：

* **隔离**（p=quarantine; sp=quarantine）
* **拒绝**（p=reject; sp=reject）
* 注意：p=none 或 pct 低于 100% 不被接受

```
# DMARC 记录示例（p=reject）
_dmarc.example.com. IN TXT "v=DMARC1; p=reject; sp=reject; rua=mailto:dmarc@example.com; pct=100"
```

详细配置指导可参考 KB 文章 [DMARC 策略部署与监控指南](/kb/dmarc-policy-enforcement-escalation.html)。

### 步骤二：制作 SVG Tiny PS 格式的官方 Logo

SVG Tiny PS（Portable/Secure）是一种最小化的 SVG 子集规范，专为 BIMI 设计。BIMI Group 提供 SVG 转换工具和验证器辅助完成此步骤。

* SVG 必须托管在稳定的 HTTPS URL 上，Content-Type 为 `image/svg+xml`
* 推荐使用 BIMI SVG Assistant Tool 检验格式合规性

### 步骤三：申请验证标记证书（VMC）或通用标记证书（CMC）

强烈建议但暂时可选。VMC 用于验证组织对 Logo 的商标所有权，CMC 则适用于非商标化 Logo（如允许季节性颜色调整）。目前 VMC 和 CMC 由 Mark Verifying Authorities（MVA）签发。

注意：自断言（self-asserted）BIMI 记录在各邮箱提供商中的支持有限。

### 步骤四：在 DNS 中发布 BIMI 记录

```
default._bimi.example.com. IN TXT "v=BIMI1; l=https://cdn.example.com/logo.svg; a=https://cdn.example.com/cert.pem"
```

参数说明：

* `v=BIMI1`：固定版本标识
* `l=`：SVG Logo 的 HTTPS URL
* `a=`：VMC/CMC 证书的 PEM URL（可选但强烈推荐）

## 运营要点

* BIMI 不改变邮件投递行为，它是显示信号而非投递信号
* 各支持 BIMI 的邮箱提供商有自己的 Logo 展示标准
* DMARC 策略必须在执行状态（quarantine 或 reject），且 pct=100%
* 国内邮箱提供商目前对 BIMI 的支持仍在发展中，建议先从海外收件方开始部署

## BIMI 与反滥用的关系

BIMI 建立在 DMARC 之上，激励正确的认证对齐和可信任的品牌可视化。由于 Logo 只在邮件通过认证时显示（在某些提供商处还需通过证书验证），视觉伪造变得更加困难，提高了冒充者的攻击门槛。

### 相关主题

* [DMARC 实施指南：从监控到强制执行的完整路径](/kb/dmarc-guide.html)
* [BIMI 品牌标识消息识别标准解读](/kb/bimi-guide.html)
* [邮件 DNS 一键诊断](/tools/dns-check.html)：检测 BIMI 及 SPF/DKIM/DMARC/MX/PTR/MTA-STS/TLS-RPT 等十项记录

本文涉及的关键技术领域：邮件认证、DMARC

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/bimi-implementation-guide.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
