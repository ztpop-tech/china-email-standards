---
title: "NIST SP 800-53 Rev.5 的 20 个控制族如何覆盖邮件系统？"
source: "https://ztpop.net/kb/nist-sp800-53r5-control-families-email.html"
license: CC-BY 4.0
---

# NIST SP 800-53 Rev.5 的 20 个控制族如何覆盖邮件系统？

1
NIST SP 800-53 Rev.5 的 20 个控制族如何覆盖邮件系统？
▼

**标准定位与版本**

NIST SP 800-53 Rev.5 由 Joint Task Force 编写，NIST 官方页面标注发布日期为 2020 年 9 月（含 2020 年 12 月 10 日更新）。其官方摘要说明：该出版物提供一份面向信息系统与组织的安全与隐私控制目录，用以保护组织运营与资产、个人、其他组织及国家，抵御包括敌对攻击、人为错误、自然灾害、结构性失效、外国情报实体与隐私风险在内的多样威胁。NIST 另于 2025 年 8 月 27 日发布 5.2.0 小版本，新增 SA-15(13)、SA-24、SI-02(07) 等控制项。

**20 个控制族**

NIST 官方页面列出的控制族为：访问控制（AC）、意识与培训（AT）、审计与问责（AU）、评估授权与监控（CA）、配置管理（CM）、应急计划（CP）、标识与鉴别（IA）、事件响应（IR）、维护（MA）、介质保护（MP）、物理与环境保护（PE）、规划（PL）、项目管理（PM）、人员安全（PS）、PII 处理与透明度（PT）、风险评估（RA）、系统与服务采购（SA）、系统与通信保护（SC）、系统与信息完整性（SI）、供应链风险管理（SR）。

**邮件系统的控制族映射**

* **AC / IA**：邮箱账号最小权限、遗留协议禁用、多因素鉴别与令牌生命周期。
* **SC**：SMTP/IMAP/POP 传输加密、边界保护、信息流强制。
* **SI**：反垃圾反钓鱼、恶意代码防护、系统监控与告警。
* **AU**：投递、认证、管理操作日志的生成、留存与审阅。
* **IR**：钓鱼与账号接管事件的处置与上报流程。
* **SR**：邮件网关、反垃圾引擎、托管服务的供应链风险管理。

**裁剪与落地**

控制目录本身是灵活可裁剪的：SP 800-53 强调控制作为组织级风险管理流程的一部分实施，需结合使命业务需要、法律法规与政策派生的要求进行选择。基线选择参见配套的 SP 800-53B，评估方法参见 SP 800-53A Rev.5。NIST 同时提供与 CSF、隐私框架及 ISO/IEC 27001:2022 的官方映射与 OSCAL 机读版本，便于把邮件系统控制项自动化纳入合规工具链。

参考：NIST SP 800-53 Rev. 5《Security and Privacy Controls for Information Systems and Organizations》，Joint Task Force，2020 年 9 月发布（含 2020-12-10 更新），DOI 10.6028/NIST.SP.800-53r5，https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/nist-sp800-53r5-control-families-email.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
