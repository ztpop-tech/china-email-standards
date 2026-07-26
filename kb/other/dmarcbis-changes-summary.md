---
title: "DMARCbis 变更总结：DMARC 协议升级为 IETF 标准轨道"
source: "https://ztpop.net/kb/dmarcbis-changes-summary.html"
license: CC-BY 4.0
---

# DMARCbis 变更总结：DMARC 协议升级为 IETF 标准轨道

IETF 的 [DMARC 工作组](https://datatracker.ietf.org/wg/dmarc/about/)已向 RFC Editor 提交了更新 DMARC 协议的文档。本文对此次更新引入的变更进行高层概述，供技术社区参考。

## 信息性 RFC → 标准轨道（Informational ⇨ Standards Track）

此次更新最重大的变化在于：更新后的 DMARC 协议已被移入 **IETF 标准轨道（Standards Track）**，从而成为正式的互联网标准（Internet Standard），而非仅仅是一份信息性 RFC（Informational RFC）。这意味着 DMARC 如今拥有了完整的 IETF 标准流程背书，具备更强的规范性和权威性。

## 公共后缀列表（PSL）被 DNS Tree Walk 与公共后缀域名（PSD）取代

对 **公共后缀列表（Public Suffix List，PSL）**的依赖已被移除。取而代之的是，邮箱提供商现在可以通过基于 DNS 的"**树遍历（Tree Walk）**"方法进行发现，或者依赖 **公共后缀域名（Public Suffix Domain，PSD）**概念。这一变更解决了长期存在的关于 PSL 作为单一维护点和潜在操纵风险的问题。

## 多个标签被废弃：pct=、rf=、ri=、np=

### pct=（百分比）— 已移除

当策略标签存在时，DMARC 策略现在应用于 100% 的邮件。这简化了 DMARC 记录，不再需要百分比灰度控制。

### rf=（报告格式）— 已移除

目前失败报告仅使用 AFRF（鉴权失败报告格式，Authentication Failure Reporting Format）格式，因此不再需要指定格式。

### ri=（报告间隔）— 已移除

报告间隔现在固定为推荐值，简化了 DMARC 记录。

### np=（非对齐子域策略）— 已移除

其功能已被更细粒度的 sp= 标签取代。

## 新标签与新特性

### sp=（子域策略，Subdomain Policy）

正式从原始 DMARC 规范中采纳，现为标准标签。

### fo=（失败报告选项，Failure Reporting Options）

现为标准标签。

### t=（TLS/安全需求）

用于指定与 DMARC 报告相关的 TLS 要求的新标签。

### 新的失败报告类型

提供了更细粒度的失败报告能力。

### DKIM 对齐的澄清

更新后的规范澄清了 DKIM 对齐的工作方式，尤其是针对子域场景。

### 聚合报告 Schema 改进

聚合报告格式已更新，增加了新字段并改善了清晰度。

## 更强的子域处理能力

更新后的规范对 DMARC 策略如何应用于子域提供了更清晰的指导，包括：

* sp= 标签如何与组织域（Organizational Domain）交互
* 基于 DNS 的子域发现机制的工作原理
* 子域发件方如何确定对齐（Alignment）

## 互操作性提升

多项澄清和错误修复改善了不同 DMARC 实现之间的互操作性，降低了 DMARC 评估中的误报（false positive）和漏报（false negative）风险。

## 过渡期

DMARC 工作组为实施方制定了更新系统的过渡期。在此过渡期内，基于旧版 RFC 7489 的 DMARC 将继续获得支持，但鼓励运营方尽快采用更新后的规范。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/dmarcbis-changes-summary.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
