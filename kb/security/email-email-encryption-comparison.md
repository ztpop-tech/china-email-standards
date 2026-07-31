---
title: "端到端加密该怎么选：S/MIME 还是 PGP（OpenPGP）？两者有何取舍？"
source: "https://ztpop.net/kb/email-email-encryption-comparison.html"
license: CC-BY 4.0
---

# 端到端加密该怎么选：S/MIME 还是 PGP（OpenPGP）？两者有何取舍？

1
端到端加密该怎么选：S/MIME 还是 PGP（OpenPGP）？两者有何取舍？
▼

**S/MIME**

基于 X.509 证书体系（与 PKI/企业 CA 契合），证书可经目录/LDAP 分发（见证书管理篇），适合“企业集中管控、与账号体系联动”。

**PGP/OpenPGP**

基于“信任网（Web of Trust）”而非中心 CA，密钥可经 WKD（见 WKD 篇）自动发现，适合“去中心、跨组织个人间”加密。

**取舍**

S/MIME 易与企业目录/合规集成但需 CA；PGP 更灵活、无需 CA 但密钥发现/信任建立更繁琐；两者都提供签名+加密。

**实践**

企业内部/合规场景偏 S/MIME；跨组织/隐私敏感个人通信偏 PGP；邮件系统可同时支持，让用户按对象选择。

参考：RFC 8550/8551（S/MIME）；RFC 4880（OpenPGP）；RFC 7929（WKD）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-email-encryption-comparison.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
