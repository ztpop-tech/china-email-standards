---
title: "SOC 2 审计中邮件系统需要满足哪些信任服务准则？"
source: "https://ztpop.net/kb/soc2-trust-services-criteria-email-controls.html"
license: CC-BY 4.0
---

# SOC 2 审计中邮件系统需要满足哪些信任服务准则？

1
SOC 2 审计中邮件系统需要满足哪些信任服务准则？
▼

**SOC 2 与信任服务准则**

AICPA 官方资料说明：SOC（System and Organization Controls）是注册会计师可提供的一套服务，涉及服务组织的系统级控制或其他组织的实体级控制。SOC 2 指南的正式名称为《对服务组织中与安全性、可用性、处理完整性、保密性或隐私相关的控制进行检查的报告》。《2017 年信任服务准则（含 2022 年修订关注点）》由 AICPA 鉴证服务执行委员会（ASEC）制定，用于鉴证或咨询业务中评价并报告用于提供产品或服务的信息与系统在上述五类上的控制。

**五类准则与邮件的对应**

* **安全性（Security）**：邮箱访问鉴别、MFA、边界防护、变更与漏洞管理——所有 SOC 2 审计的必选类别。
* **可用性（Availability）**：邮件服务 SLA、备份 MX、灾备切换与容量监控。
* **处理完整性（Processing Integrity）**：投递链路完整、无静默丢信、退信与队列可核对。
* **保密性（Confidentiality）**：邮件加密传输与存储、DLP 外发管控、归档访问限制。
* **隐私（Privacy）**：邮件中个人信息的收集、留存、使用与销毁符合承诺。

**Type 1 与 Type 2**

AICPA 官方资源库分别提供 SOC 2 Type 1 与 SOC 2 Type 2 的示范管理层声明函，说明两种报告类型并存。此外还提供《2018 SOC 2 描述准则（含 2022 年修订实施指南）》与含系统描述的示范 SOC 2 报告，供服务组织编制系统描述时对照。邮件相关控制通常需要覆盖整个审计期间的运行有效性证据，而非仅某一时点的设计。

**准备审计的邮件证据**

常见需归集的证据：邮箱账号开通/变更/回收工单与审批记录；MFA 与遗留协议禁用的配置截图；SMTP/IMAP 强制 TLS 的配置与握手日志；DMARC 策略与汇总报告；邮件网关拦截与放行的策略变更审计；离职人员邮箱处置记录；邮件归档的留存期与访问日志。AICPA 另提供信任服务准则与其他框架的官方映射文档，可用于复用 ISO 27001 或 NIST SP 800-53 的既有证据，减少重复取证。

参考：AICPA & CIMA《2017 Trust Services Criteria for Security, Availability, Processing Integrity, Confidentiality, and Privacy (With Revised Points of Focus — 2022)》，由 AICPA 鉴证服务执行委员会（ASEC）制定；AICPA《SOC 2® Guide: Reporting on an Examination of Controls at a Service Organization Relevant to Security, Availability, Processing Integrity, Confidentiality, or Privacy》，https://www.aicpa-cima.com/resources/landing/system-and-organization-controls-soc-suite-of-services

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/soc2-trust-services-criteria-email-controls.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
