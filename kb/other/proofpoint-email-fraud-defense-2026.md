---
title: "Proofpoint Email Fraud Defense 如何防御域名欺骗与供应商邮件欺诈？"
source: "https://ztpop.net/kb/proofpoint-email-fraud-defense-2026.html"
license: CC-BY 4.0
---

# Proofpoint Email Fraud Defense 如何防御域名欺骗与供应商邮件欺诈？

1
Proofpoint Email Fraud Defense 如何防御域名欺骗与供应商邮件欺诈？
▼

**要解决的两类欺骗**

Proofpoint 官方文档把 BEC 的常见战术归为两类：**域名欺骗**（直接冒用可信域，如 `Company <person@company.com>`）与**近似域名欺骗**（注册形似域，如把 m 拆成 rn 的 `Company <person@c0rnpany.com>`）。前者可由 DMARC 强制解决，后者则完全绕开 DMARC——因为攻击者用的是自己合法拥有的域，认证会正常通过。此外，邮件欺诈（impostor email）通常**不携带恶意附件或恶意 URL**，因而对以载荷检测为核心的防御是「隐形」的。这三点共同决定了单一手段不足，需要认证、域名情报与内容/关系分析叠加。

**DMARC 落地与托管认证服务**

产品的第一层是把 DMARC 从「难以推进」变为可交付：由专属顾问提供可定制的项目计划与引导式工作流，帮助**识别全部合法发件人（含第三方与影子 IT）**并确保其正确认证，按邮件量与主要发件人排定任务优先级，最终发布 `p=reject` 策略而不阻断有效邮件。配套的托管认证服务包括：**Hosted SPF**——突破 SPF 传统的 10 次 DNS 查询上限、实时更新并做语法校验、通过混淆发送基础设施提升安全性、便于批量管理共用同一发送设施的多个域；**Hosted DKIM**——简化选择器与密钥管理，支持委派/非委派两种托管方式，支持 DNSSEC，可简单导入既有选择器与公钥；**Hosted DMARC**——四个地理分布的区域数据中心保障可靠性，提供近乎即时的 DNS 更新。产品还会展示托管在 Microsoft 365 上的自有域的 DMARC 通过率。

**仿冒域发现与供应商风险**

针对 DMARC 覆盖不到的近似域名，Proofpoint 使用高可扩展的域名监控与检测系统，**持续分析超过 6.5 亿个域名**并结合 WHOIS 数据源，把注册数据与自有的邮件活动及攻击数据关联，动态识别由组织外部人员注册的、仿冒你品牌的域名，并展示**攻击者尝试劫持了你的哪些域**，可通过 Virtual Takedown Service 主动处置。更进一步是 **Supplier Risk Explorer**：自动识别你的供应商，查看来自供应商域名仿冒者的消息量与投递情况，评估并排序各供应商对你构成的风险（冒名威胁、钓鱼、恶意软件、垃圾邮件）。这直接对应供应链邮件欺诈——攻击者不攻你，而是冒充或攻陷你的供应商来改收款账户。

**与网关联动及配套能力**

Proofpoint 称其是唯一在**邮件认证与安全邮件网关之间提供真正集成**的厂商，由此可以：对入站流量强制 DMARC 以缓解冒名威胁；校验特定域的 DMARC 信誉，降低误拦合法邮件的风险；为有效邮件创建覆盖策略而不削弱整体安全态势。在网关侧，Email Protection 提供预置的反欺骗规则与主题标记；动态的 **Impostor Classifier** 以机器学习分析邮件内容、发件人信誉与邮件地址操纵痕迹，输出**可配置的 Impostor Email Score**。出站方向则由 Email DLP 自动发现、分类并阻断与邮件欺诈相关的外发通信，保护税务信息、员工档案与电汇指令等关键数据。相关方案 **Secure Email Relay** 用于保护来自内部应用及 ServiceNow、Salesforce、Workday 等第三方 SaaS 的应用邮件，提供反病毒/反垃圾扫描与中继消息的 DKIM 签名以支撑 DMARC 合规，并对应用邮件做载荷加密与 DLP。

参考：Proofpoint 官方产品页《Email Fraud Defense》：<https://www.proofpoint.com/uk/products/email-protection/email-fraud-defense>；Proofpoint 官方数据表《Proofpoint Email Fraud Defense》：<https://www.proofpoint.com/sites/default/files/data-sheets/pfpt-us-ds-efd360.pdf>

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/proofpoint-email-fraud-defense-2026.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
