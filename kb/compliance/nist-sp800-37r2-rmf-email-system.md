---
title: "如何用 NIST SP 800-37 Rev.2 风险管理框架（RMF）管理邮件系统？"
source: "https://ztpop.net/kb/nist-sp800-37r2-rmf-email-system.html"
license: CC-BY 4.0
---

# 如何用 NIST SP 800-37 Rev.2 风险管理框架（RMF）管理邮件系统？

1
如何用 NIST SP 800-37 Rev.2 风险管理框架（RMF）管理邮件系统？
▼

**RMF 是什么**

SP 800-37 Rev.2 官方摘要写明：本出版物描述风险管理框架（RMF）并给出将 RMF 应用于信息系统与组织的指南。RMF 为管理安全与隐私风险提供有纪律、结构化且灵活的流程，涵盖信息安全分类；控制的选择、实施与评估；系统授权与共用控制授权；以及持续监控。该版本发布于 2018 年 12 月，取代 Rev.1 与 CSWP 3。

**邮件系统的 RMF 执行要点**

* **准备**：明确邮件系统边界（MTA、MDA、Webmail、网关、归档），指定系统属主与授权官。
* **分类**：依据邮件承载数据的机密性、完整性、可用性影响定级。
* **选择**：从 SP 800-53 目录裁剪 AC/IA/SC/SI/AU 等控制并形成基线。
* **实施**：落地 TLS、SPF/DKIM/DMARC、MFA、日志集中等技术措施。
* **评估**：由控制评估员出具安全与隐私评估报告。
* **授权**：授权官基于剩余风险签发运行授权（ATO）或使用授权。
* **监控**：以持续监控替代周期性重认证，支撑持续授权。

**为什么邮件系统适合 RMF**

摘要指出 RMF 的目标之一是推动近实时风险管理与通过持续监控实现系统与共用控制的持续授权，并把安全与隐私融入系统开发生命周期。邮件系统面对的钓鱼、账号接管、配置漂移变化极快，一次性认证难以反映真实风险，持续监控更契合其威胁节奏。

**组织级与系统级的衔接**

官方摘要强调：执行 RMF 任务把系统层的风险管理流程与组织层的风险管理流程连接起来，并为组织信息系统中实施的控制、以及被其他系统继承的控制建立责任与问责。对邮件而言，反垃圾网关、身份认证平台等常作为「共用控制」被多个系统继承，须单独授权并明确责任主体，避免继承方误以为控制已覆盖。

参考：NIST SP 800-37 Rev. 2《Risk Management Framework for Information Systems and Organizations: A System Life Cycle Approach for Security and Privacy》，Joint Task Force，2018 年 12 月发布，DOI 10.6028/NIST.SP.800-37r2，https://csrc.nist.gov/pubs/sp/800/37/r2/final

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/nist-sp800-37r2-rmf-email-system.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
