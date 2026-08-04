---
title: "NIST SP 800-161 Rev.1 如何指导邮件系统的供应链风险管理（C-SCRM）？"
source: "https://ztpop.net/kb/nist-sp800-161r1-email-supply-chain-risk.html"
license: CC-BY 4.0
---

# NIST SP 800-161 Rev.1 如何指导邮件系统的供应链风险管理（C-SCRM）？

1
NIST SP 800-161 Rev.1 如何指导邮件系统的供应链风险管理（C-SCRM）？
▼

**标准要解决的问题**

SP 800-161 Rev.1 官方摘要指出：组织担忧的是所采购产品与服务可能内含恶意功能、属于假冒品，或因供应链中制造与开发实践不良而存在脆弱性。这些风险源于企业对所采购技术如何被开发、集成与部署，以及对用于保证产品服务安全性、韧性、可靠性、安全、完整性与质量的流程、程序、标准与实践缺乏可见性与理解。该版本发布于 2022 年 5 月，取代 2015 年版。

**多层级 C-SCRM 方法**

摘要说明：本出版物为组织在其各层级识别、评估与缓解整条供应链上的网络安全风险提供指南，通过采用多层级、C-SCRM 专用的方法把网络安全供应链风险管理融入风险管理活动，包括 C-SCRM 战略实施计划、C-SCRM 政策、C-SCRM 计划以及针对产品与服务的风险评估的制定指南。落到邮件场景，即从企业层战略、任务/业务流程层，直到具体邮件系统层逐级展开。

**邮件系统的供应链风险面**

* **邮件网关与反垃圾引擎**：规则库与特征库的更新通道被污染即等同于旁路防护。
* **托管邮件与 SaaS 代发**：第三方持有 DKIM 私钥或代表本域发信，其被攻陷会直接损害本域信誉。
* **MTA 开源组件**：Postfix、Dovecot、Roundcube 等依赖链中的漏洞需可追溯的物料清单。
* **邮件安全插件与浏览器扩展**：具备读取全部邮件的权限，是高价值供应链目标。

**落地做法**

把 C-SCRM 要求写入采购合同：要求供应商提供软件物料清单（SBOM）、漏洞披露流程与安全事件通报时限；对代发第三方使用独立 DKIM 选择器并可单独吊销；对邮件安全组件的更新通道做完整性校验与灰度发布。SP 800-161 Rev.1 与 SP 800-53 Rev.5 的 SR（供应链风险管理）控制族配套使用，并回应了第 14028 号行政令关于软件供应链安全的要求。

参考：NIST SP 800-161 Rev. 1《Cybersecurity Supply Chain Risk Management Practices for Systems and Organizations》，Boyens、Smith、Bartol、Winkler、Holbrook、Fallon，2022 年 5 月发布，DOI 10.6028/NIST.SP.800-161r1，https://csrc.nist.gov/pubs/sp/800/161/r1/final

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/nist-sp800-161r1-email-supply-chain-risk.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
