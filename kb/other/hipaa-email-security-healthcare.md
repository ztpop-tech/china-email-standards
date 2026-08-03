---
title: "HIPAA 下医疗行业邮件安全有哪些专项要求？"
source: "https://ztpop.net/kb/hipaa-email-security-healthcare.html"
license: CC-BY 4.0
---

# HIPAA 下医疗行业邮件安全有哪些专项要求？

1
HIPAA 下医疗行业邮件安全有哪些专项要求？
▼

**受保护健康信息（ePHI）的界定**

HIPAA Security Rule 适用于通过电子形式创建、接收、维护或传输的**受保护健康信息（ePHI）**。凡邮件正文或附件含患者姓名、病历号、诊断、医保号等标识信息，即落入监管范围。医疗机构与处理 ePHI 的邮件服务商之间必须签订**业务伙伴协议（BAA）**。

**传输与静态安全（技术 safeguard）**

Security Rule 的「传输安全」要求对电子传输中的 ePHI 实施保护措施：对外发邮件强制 **TLS 加密**，对不支持 TLS 的对端应阻止或改用加密附件。对 ePHI 附件应采用密码学加密（如 S/MIME 或加密 ZIP 并带外传送口令）。访问控制和审计控制要求对邮件系统实施最小权限与操作留痕。

**管理性与物理性 safeguard**

管理性 safeguard 要求制定安全策略、人员培训、风险评估与事件响应流程；物理性 safeguard 要求对承载邮件系统的服务器机房与终端做物理访问控制。应至少每年开展一次安全风险评估，对识别的漏洞落实整改，并保留「最小必要」原则的使用限制。

**泄露通报时间线**

HIPAA Breach Notification Rule 要求：涉及 500 人以上 ePHI 泄露须于 **60 日内**通报 HHS 并通知媒体；少于 500 人须按年汇总通报。个体须在不合理延迟内（通常 60 日）获通知。是否构成「泄露」取决于是否存在「安全港」下的低风险例外（如加密后的信息丢失）。

参考：HIPAA Privacy Rule 与 Security Rule（45 CFR Part 160/164）、Security Rule 技术/管理/物理 safeguard、Breach Notification Rule（§164.404–410）；NIST SP 800-66《HIPAA 安全规则实施指引》、NIST CSF 2.0。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/hipaa-email-security-healthcare.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
