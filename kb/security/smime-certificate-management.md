---
title: "S/MIME 证书如何“分发与吊销”？邮件系统怎样让用户免手工配置就能加密？"
source: "https://ztpop.net/kb/smime-certificate-management.html"
license: CC-BY 4.0
---

# S/MIME 证书如何“分发与吊销”？邮件系统怎样让用户免手工配置就能加密？

1
S/MIME 证书如何“分发与吊销”？邮件系统怎样让用户免手工配置就能加密？
▼

**分发**

S/MIME 用 X.509 证书（含公钥）；收件人公钥可通过 目录服务（LDAP/AD）、企业证书门户、或“对方来信已签名则自动提取证书”获得，免去手动交换。

**吊销**

证书过期/离职须吊销，靠 CRL（证书吊销列表）或 OCSP 实时查询；邮件客户端验签时应检查吊销状态，避免用已废密钥加密。

**生命周期**

企业内部可由自有 CA（或公共 CA）签发用户邮件证书，集中注册到目录；员工入职发证书、离职吊销，与账号体系联动。

**实践**

邮件系统对接目录/LDAP 自动发布用户证书，客户端据此“发现对方公钥”加密；这是企业内 S/MIME 可用性的关键（见 S/MIME+PGP 基础）。

参考：RFC 8550/8551（S/MIME 证书与消息规范）；X.509 / CRL / OCSP

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/smime-certificate-management.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
