---
title: "BIMI Mark Verifying Authority (MVA) 参与指南 — AuthIndicators 工作组扩展方案与 FAQ（翻译）"
source: "https://ztpop.net/kb/bimi-mva-faqs.html"
license: CC-BY 4.0
---

# BIMI Mark Verifying Authority (MVA) 参与指南 — AuthIndicators 工作组扩展方案与 FAQ（翻译）

BIMI（Brand Indicators for Message Identification）的采纳正在稳步增长，签发 VMC（Verified Mark Certificate）和 CMC（Common Mark Certificate）的认证机构（CA）作为 Mark Verifying Authority（MVA）构成了 BIMI 信任链的基础层。然而，目前仅有少数 CA 作为 MVA 参与其中——扩大 MVA 参与范围是 BIMI 生态规模化的关键瓶颈。

AuthIndicators Working Group（即 BIMI Group）于 2025 年 7 月发布本 FAQ（V1.0），阐明扩展 MVA 参与的路线图：通过简化认证要求、增强流程透明度、提供清晰的支持指南，鼓励更多 CA 加入 MVA 体系，从而加速 VMC/CMC 的普及，强化邮件认证生态的可信度与安全性。

本文基于 [bimigroup.org/mva-faqs/](https://bimigroup.org/mva-faqs/) 全文翻译，各问答标题与回答均忠实于原文。

## AuthIndicators Working Group 是什么？

AuthIndicators Working Group（"BIMIGroup"）是一个志愿性组织，致力于标准化 Brand Indicators for Message Identification（BIMI）。BIMI 使品牌能够在经过认证的邮件旁显示经过验证的品牌 Logo，从而提升邮件通讯中的识别度与可信度。

## 什么是 Verified Mark Certificate（VMC）？

Verified Mark Certificate（VMC）用于验证品牌 Logo 的所有权及域名所有权。它确保只有经过验证的品牌 Logo 才能出现在经过认证的邮件中，防止滥用并增强邮件完整性。

## 什么是 Common Mark Certificate（CMC）？

Common Mark Certificate（CMC）是 BIMI Group 推出的一种新型数字证书，旨在简化和标准化品牌 Logo 的验证流程，使其更易于在邮件认证（特别是 BIMI）中使用。CMC 通过降低复杂度和成本，为 VMC 提供了一种更经济的替代方案。CMC 确保品牌 Logo 在邮件中的真实性，提升信任与安全性，同时降低组织采纳 BIMI 的门槛。

## 各类 Mark Certificate 由谁签发？

VMC 和 CMC 由 Mark Verifying Authority（MVA）签发，通常为经过严格验证的认证机构（CA）。BIMIGroup 维护一份经批准的 MVA 列表及其合规文档。

## VMC 与 CMC 的核心区别是什么？

| 维度 | VMC（验证标记证书） | CMC（通用标记证书） |
| --- | --- | --- |
| 成熟度 | 成熟、早已确立的证书类型 | BIMI Group 新近推出的简化方案 |
| 验证深度 | 严格验证，含商标验证 | 简化验证流程，仍在保证 Logo 真实性 |
| 复杂度 | 较高（需要详尽的 CPS 文档） | 较低（流程精简） |
| 成本 | 较高 | 较低，适合预算有限的品牌 |
| 适用场景 | 已注册商标的品牌 | 非商标化 Logo 或较小品牌，如允许季节性颜色调整的场景 |

## BIMIGroup 计划如何扩展 MVA 参与？

BIMIGroup 通过提供资源和指南来增加 VMC 的签发量并鼓励更多 CA 参与。具体措施包括：提供清晰的指南、通过 Certificate Transparency（CT）日志增强透明度、推动定期审计。通过这些举措，BIMIGroup 旨在支持可信 Mark Certificate 提供商的成长，帮助其有效完成流程。

## 认证机构如何才能成为 MVA？

有兴趣签发 VMC/CMC 的认证机构应遵循以下流程：

1. **审阅要求：**了解 BIMIGroup 的 VMC 指南和技术规范。
2. **编写 CPS（认证实践声明）：**记录签发 VMC 的策略和流程。
3. **证书透明度（CT）日志：**与 BIMI Group 协调，将证书发布至经批准的 CT 日志（依据 VMC 指南附录 F）。
4. **建立 CRL（证书吊销列表）：**提供必要的证书吊销机制。
5. **接受定期的 WebTrust VMC 审计：**通过独立的第三方评估确保合规。
6. **注册至 CCADB：**确保纳入 Common CA Database（[ccadb.org/cas](https://www.ccadb.org/cas)），以促进信任存储库间的透明度和互操作性。联系 certdb@mozilla.org 启动注册流程。
7. **向 BIMIGroup 提交信息：**提供 CPS、CT 日志证明、CRL URL、根证书及审计报告供审查。
8. **测试验证：**在成为正式 MVA 之前，可与实施 BIMI 的邮箱提供商（如 Apple 和 Fastmail，历史上曾提供此类支持）进行测试。联系 BIMIGroup（[bimigroup.org/contact-us](https://bimigroup.org/contact-us)）寻求协助。

完成以上步骤后，CA 即可被纳入 MVA 名单，从而为 BIMI 的采纳贡献信任基础并增强邮件安全性。

## BIMIGroup 在认证 MVA 中的角色是什么？

BIMIGroup 不直接认证 MVA，而是提供 Mark Certificate 签发的技术规范和认证要求。各邮箱提供商可根据自身标准和验证流程，独立决定是否接受某一 MVA 签发的 VMC。

## BIMIGroup 如何支持 BIMI 与 VMC 的采纳？

BIMIGroup 通过以下方式推动 BIMI 与 VMC 的普及：

* **提供资源：**发布实施指南、工具与最佳实践。
* **维护 MVA 信息：**持续更新合规 MVA 列表。
* **对接利益相关方：**与品牌、CA、MVA 及邮箱提供商协作推进 BIMI 采纳。

这些努力旨在改善邮件认证水平，推动更安全、更可信的邮件生态建设。

本文档版本 V1.0，最后更新于 2025 年 7 月。原文来源：[bimigroup.org/mva-faqs/](https://bimigroup.org/mva-faqs/)。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/bimi-mva-faqs.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
