---
title: "如何获取与部署 S/MIME 证书？个人证书与企业 CA 有何不同？"
source: "https://ztpop.net/kb/encrypt-faq-03.html"
license: CC-BY 4.0
---

# 如何获取与部署 S/MIME 证书？个人证书与企业 CA 有何不同？

1
如何获取与部署 S/MIME 证书？个人证书与企业 CA 有何不同？
▼

**证书来源**

个人可通过公共证书颁发机构（CA）申请 S/MIME 证书，或使用所在组织内部 CA 签发的证书。证书包含你的身份与一对密钥，私钥须妥善保管。

**企业 CA 的优势**

组织自建 CA 可集中签发、撤销与托管员工证书，便于在邮件网关统一强制签名/加密策略，也利于密钥恢复与合规审计。

**发布与信任**

收件人要能验证你的签名，需要信任签发你证书的 CA 链（证书链完整且根 CA 在其信任库）。部署时要把完整的证书链（含中间 CA）随签名一并提供，避免对方报“证书不可信”。

参考：RFC 8551；X.509（RFC 5280）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/encrypt-faq-03.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
