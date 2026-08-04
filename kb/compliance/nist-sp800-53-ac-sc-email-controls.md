---
title: "NIST SP 800-53 中哪些控制项直接约束电子邮件安全？"
source: "https://ztpop.net/kb/nist-sp800-53-ac-sc-email-controls.html"
license: CC-BY 4.0
---

# NIST SP 800-53 中哪些控制项直接约束电子邮件安全？

1
NIST SP 800-53 中哪些控制项直接约束电子邮件安全？
▼

**传输与会话保护（SC 族）**

**SC-8 传输保密性与完整性**要求对邮件等传输中的信息保密并防篡改，落地即全链路 TLS（STARTTLS/隐式 TLS）并禁用明文；**SC-8(1) 密码学保护**进一步要求采用经批准的密码算法。 **SC-23 会话真实性**保护邮件会话不被劫持（如绑定 TLS 会话、抗中间人），与防 AITM/会话劫持钓鱼直接相关。

**垃圾邮件与内容完整性（SI 族）**

**SI-8 垃圾邮件防护**是 SP 800-53 中直接针对邮件的控制项，要求识别并处置垃圾/钓鱼邮件（含网关过滤、用户报告机制与处置流程）。 **SI-4 系统监控**要求对邮件网关与邮箱行为做持续监测，发现异常发信与外泄迹象。

**身份与账户（AC / IA 族）**

**AC-2 账户管理**约束邮箱账号的开通、复核、停用与回收，防止幽灵账号被用于发信。 **IA-2 身份鉴别（组织用户）**要求对访问邮箱/Web 邮件的用户做鉴别，结合防钓鱼 MFA（参见 SP 800-63B AAL3）提升抗钓鱼能力。 **SC-7 边界保护**约束邮件网关与边界，限制非授权连接。

**审计与可追溯（AU 族）**

**AU-12 审计记录生成**要求对邮件系统的关键事件（登录、转发规则变更、大量下载、DMARC 失败处置）生成审计记录，配合 AU-2/AU-6 形成可追溯证据链，满足 FISMA、BOD 23-01 与事件响应（IR 族）的取证要求。上述控制共同构成邮件系统满足联邦合规的基线。

参考：NIST SP 800-53 Rev.5《Security and Privacy Controls for Information Systems and Organizations》(https://doi.org/10.6028/NIST.SP.800-53r5；2020-09)，控制族 AC/IA/SC/AU/SI

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/nist-sp800-53-ac-sc-email-controls.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
