---
title: "FISMA 对联邦邮件系统提出了哪些安全要求？"
source: "https://ztpop.net/kb/fisma-email-security-requirements.html"
license: CC-BY 4.0
---

# FISMA 对联邦邮件系统提出了哪些安全要求？

1
FISMA 对联邦邮件系统提出了哪些安全要求？
▼

**FISMA 的法定要求**

FISMA（Federal Information Security Modernization Act，2002 立法、2014 现代化修订）要求每个联邦机构建立、成文并实施覆盖全机构的信息安全项目，以保护政府信息系统与信息。CISA 提供运行指导并协调联邦网络安全，OMB 负责总体监督；机构须每年向 OMB 与国会报告安全项目状况。

**风险定级与基线控制**

机构须按 **FIPS 199** 以机密性/完整性/可用性（CIA）潜在影响把系统定为 Low、Moderate 或 High 三级；随后从 **NIST SP 800-53** 选取并实施与级别匹配的安全与隐私控制。邮件系统作为处理政务与公民数据的系统，同样须定级并满足对应基线（如 Moderate 通常要求传输加密、强认证、审计等）。

**RMF 与授权运行（ATO）**

落地遵循 **NIST SP 800-37** 的风险管理框架（RMF）：分类→选型→实施→评估→授权→持续监控。系统在上线前须由授权官员签发 ATO（Authorization to Operate）；邮件系统也须以系统安全计划（SSP）、安全评估报告（SAR）与持续监控证据支撑授权。

**持续监控与年度报告**

FISMA 2014 修订把重点从「一次性合规」转向**持续监控**：持续感知漏洞、威胁与安全态势，定期评估控制有效性。机构还须配合 DHS/CyberScope 等渠道报送指标，并接受监察长（IG）年度独立评估，邮件安全指标亦纳入其中。

参考：《联邦信息安全管理现代化法》(FISMA, 44 U.S.C. § 3551 等；2014 修订)、NIST SP 800-53 Rev.5 (https://doi.org/10.6028/NIST.SP.800-53r5)、NIST SP 800-37 RMF、FIPS 199

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/fisma-email-security-requirements.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
