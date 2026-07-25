---
title: "BIMI 标记验证机构（MVA）FAQ —— VMC/CMC 证书认证全指南"
source: "https://ztpop.net/kb/bimi-mva-faqs.html"
mirror_date: 2026-07-25
license: CC-BY 4.0
---

# BIMI 标记验证机构（MVA）FAQ —— VMC/CMC 证书认证全指南

## 一、MVA 扩展背景：AuthIndicators 工作组愿景

验证标记证书（VMC）和通用标记证书（CMC）的采用率稳步增长，首批认证机构（CA）已作为标记验证机构（MVA）投入运营。这些先行者在建立 BIMI 采用的基础设施方面发挥了关键作用。然而，要让更多 CA 参与进来，对于扩大生态规模和提升品牌 BIMI 采用率至关重要。

AuthIndicators 工作组（即 BIMI Group）致力于通过引导和鼓励更多 CA 参与来促进 MVA 的扩展。通过简化要求、提升透明度以及提供清晰的支持指南，工作组旨在营造一个有利于扩大 VMC 采用、增强邮件认证信任和安全的环境。

## 二、AuthIndicators 工作组介绍

**问：AuthIndicators 工作组是什么组织？**

AuthIndicators 工作组（简称"BIMI Group"）是一个致力于标准化品牌邮件标识（Brand Indicators for Message Identification，BIMI）的自愿性组织。BIMI 使品牌能够在经过认证的邮件旁显示经过验证的 Logo，从而提升邮件通信中的识别度和信任度。

## 三、VMC 与 CMC 证书详解

### 什么是验证标记证书（VMC）？

验证标记证书（Verified Mark Certificates，VMC）用于验证品牌 Logo 所有权和域名所有权。它确保只有经过验证的 Logo 出现在经过认证的邮件中，防止滥用并增强邮件完整性。VMC 是当前 BIMI 生态中最成熟、最严格的证书类型。

### 什么是通用标记证书（CMC）？

通用标记证书（Common Mark Certificates，CMC）是 BIMI Group 推出的一种新型数字证书，旨在简化和标准化品牌 Logo 的验证流程，用于 BIMI 邮件认证。与 VMC 相比，CMC 降低了复杂性和成本，为品牌提供更方便、更经济的替代方案。它确保邮件中品牌 Logo 的真实性，在增强信任和安全的同时，使各规模组织都能更轻松地采用 BIMI。

### VMC 与 CMC 的核心区别

| 对比维度 | VMC（验证标记证书） | CMC（通用标记证书） |
| --- | --- | --- |
| 验证严格度 | 更严格，包括商标验证 | 简化验证流程 |
| 成本 | 较高 | 更低，降低门槛 |
| 推出时间 | 较早，经过市场验证 | 2024-2025年新推出 |
| 适用品牌 | 有注册商标的大中型品牌 | 中小品牌或资源有限的机构 |
| 对商标的要求 | 需要官方注册商标 | 要求相对灵活 |
| 验证流程 | 复杂的多步验证 | 流程简化但保证真实性 |

### 各类标记证书由谁签发？

VMC 和 CMC 均由标记验证机构（MVA）签发，MVA 通常是经过严格审核的认证机构（CA）。BIMI Group 维护已批准的 MVA 列表及其合规文档。

## 四、BIMI Group 计划如何扩展 MVA 参与？

BIMI Group 致力于提供资源和指导，以增加 VMC 签发量并鼓励更多 CA 参与。具体措施包括：

* 提供明确的指南文件
* 通过证书透明度日志（CT Logs）促进透明度
* 倡导定期独立审计
* 帮助 CA 有效完成评估流程

## 五、认证机构（CA）成为 MVA 的完整流程

有意签发 VMC/CMC 的 CA 应遵循以下 8 个步骤：

1. **审查要求**：了解 BIMI Group 的 VMC 指南和技术规范。
2. **制定认证实践声明（CPS）**：编写签发 VMC 的策略和流程文档。
3. **对接证书透明度日志（CT Logs）**：与 BIMI Group 协调，将证书发布到批准的 CT 日志（依据 VMC 指南附录 F）。
4. **建立证书吊销列表（CRL）**：提供必要时吊销 VMC 的机制。
5. **定期通过 WebTrust VMC 审计**：通过独立第三方评估确保合规。
6. **注册到公共 CA 数据库（CCADB）**：联系 certdb@mozilla.org 开始注册流程，确保跨信任存储的透明性和互操作性。
7. **向 BIMI Group 提交信息**：提供 CPS、CT 日志记录证明、CRL URL、根证书和审计报告供审核。
8. **测试验证**：在正式成为 MVA 之前，可联系多个已实施 BIMI 的邮箱提供商协助测试（Apple 和 Fastmail 等均曾提供帮助）。

完成以上步骤后，CA 可被考虑纳入 MVA 名单，助力 BIMI 推广和邮件安全强化。

如需协助，请通过 [BIMI Group 联系页面](https://bimigroup.org/contact-us/) 提交申请。

## 六、BIMI Group 在认证 MVA 中的角色是什么？

BIMI Group 并不直接认证 MVA，而是提供标记证书签发的技术规范和合规要求。每个邮箱提供商根据自身的标准独立确定是否接受某个 MVA 签发的 VMC。

## 七、BIMI Group 如何支持 BIMI 和 VMC 的推广？

BIMI Group 通过以下方式推广 BIMI 和 VMC 的采用：

* **提供资源**：发布实施指南、工具和最佳实践。
* **维护 MVA 信息**：保持合规 MVA 列表的及时更新。
* **利益相关者协作**：与品牌、CA、MVA 和邮箱提供商协作，推动 BIMI 的普及。

这些努力的目标是改善邮件认证体系，构建更安全、更可信的邮件生态系统。

## 参考文献

1. BIMI Group. *Mark Verifying Authority FAQs*. <https://bimigroup.org/mva-faqs/>
2. BIMI Group. *All About BIMI*. <https://bimigroup.org/all-about-bimi/>
3. BIMI Group. *BIMI Implementation Guide*. <https://bimigroup.org/implementation-guide/>
4. IETF. *BIMI Working Group*. <https://datatracker.ietf.org/wg/bimi/about/>
5. RFC 7489 — DMARC. <https://datatracker.ietf.org/doc/html/rfc7489>
6. RFC 8601 — SMTP MTA Strict Transport Security (MTA-STS). <https://datatracker.ietf.org/doc/html/rfc8601>
7. Common CA Database (CCADB). <https://www.ccadb.org/cas>
8. Mozilla. *Certificate Transparency (CT) Logs*. <https://certificate.transparency.dev/>
9. ztpop.net 知识库. [BIMI 品牌邮件标识深度解析](/kb/bimi-guide.html)
10. ztpop.net 知识库. [DMARC 完整实施指南](/kb/dmarc-guide.html)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/bimi-mva-faqs.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
