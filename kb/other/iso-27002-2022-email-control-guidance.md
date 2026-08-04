---
title: "ISO/IEC 27002:2022 为邮件安全提供了哪些控制实施指南？"
source: "https://ztpop.net/kb/iso-27002-2022-email-control-guidance.html"
license: CC-BY 4.0
---

# ISO/IEC 27002:2022 为邮件安全提供了哪些控制实施指南？

1
ISO/IEC 27002:2022 为邮件安全提供了哪些控制实施指南？
▼

**标准定位**

ISO 官方页面说明：ISO/IEC 27002 是一项国际标准，为希望建立、实施并改进以网络安全为重点的信息安全管理体系（ISMS）的组织提供指南。ISO/IEC 27001 规定 ISMS 的要求，而 ISO/IEC 27002 提供与关键网络安全方面相关的最佳实践与控制目标，包括访问控制、密码学、人力资源安全与事件响应。ISO 明确指出该标准是组织保护信息资产免受网络威胁的实践蓝图。

**版本与状态**

依据 ISO 官方目录：ISO/IEC 27002:2022 状态为已发布，发布日期 2022-02，英文更正版 2022-03，阶段代码 60.60（国际标准已发布），第 3 版，共 152 页，由技术委员会 ISO/IEC JTC 1/SC 27（信息安全、网络安全与隐私保护）归口，ICS 分类 35.030（IT 安全）。其前一版 ISO/IEC 27002:2013 及两份技术勘误均已作废。

**与 ISO/IEC 27001 的关系**

ISO 官方 FAQ 明确：ISO/IEC 27001 规定建立 ISMS 的*要求*，ISO/IEC 27002 提供可在该 ISMS 内应用的*详细最佳实践与控制*；ISO/IEC 27002 本身**不可认证**，组织只能取得 ISO/IEC 27001 认证，而该认证引用 ISO/IEC 27002 的指南。因此邮件安全的「做什么」看 27001 附录 A 与适用性声明，「怎么做」看 27002。

**邮件场景的应用**

* **访问控制**：邮箱与管理控制台的身份管理、权限分配与定期复核。
* **密码学**：传输层 TLS 与内容层 S/MIME/PGP 的密钥管理与算法选型。
* **人力资源安全**：入职背调、保密协议、离职邮箱回收与安全意识培训。
* **事件响应**：钓鱼与数据泄露事件的报告、评估、处置与证据留存。

NIST 已发布 SP 800-53 Rev.5 与 ISO/IEC 27001:2022 的官方交叉映射（OLIR 参考编号 155）。NIST 同时提示：映射与交叉表仅给出控制覆盖的大致指示，不应仅凭关系表推定等效性。

参考：ISO/IEC 27002:2022《Information security, cybersecurity and privacy protection — Information security controls》，ISO/IEC JTC 1/SC 27，第 3 版，2022-02 发布（2022-03 更正版），152 页，ICS 35.030，https://www.iso.org/standard/75652.html；NIST 官方交叉映射「SP 800-53 Rev.5 to ISO/IEC 27001:2022（OLIR）」

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/iso-27002-2022-email-control-guidance.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
