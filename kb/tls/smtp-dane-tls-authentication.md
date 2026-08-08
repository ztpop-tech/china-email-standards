---
title: "SMTP DANE 是怎么用 DNSSEC 给收件服务器证书「钉死」来防劫持的？"
source: "https://ztpop.net/kb/smtp-dane-tls-authentication.html"
license: CC-BY 4.0
---

# SMTP DANE 是怎么用 DNSSEC 给收件服务器证书「钉死」来防劫持的？

1
SMTP DANE 是怎么用 DNSSEC 给收件服务器证书「钉死」来防劫持的？
▼

普通 SMTP 的 STARTTLS 是「机会性」的：只要握手成功就发送，攻击者可在中间**剥离或替换证书**而发送方无感知。

#### 一、DANE 的核心思路

SMTP DANE（RFC 7672）在 DNSSEC 保护的区域里发布 `TLSA` 记录，把收件 MX 的证书（或其公钥哈希）与域名**绑定**。发送方先经 DNSSEC 验证 TLSA 真实，再比对对端出示的证书——不一致直接拒绝，无需盲信公共 CA。

#### 二、两种强度

* **机会型（opportunistic）**：有 TLSA 就强制校验，无则仍可降级发送。
* **强制型（enforced）**：缺失或校验失败即不投递，提供最强保护。

#### 三、前提与收益

DANE 的信任锚是**DNSSEC**，因此要求收发双方域名均部署 DNSSEC。它的价值在于把「信任 CA 体系」替换为「域名自己声明证书」，有效防御针对 SMTP 的主动中间人劫持与证书替换。

参考：https://www.rfc-editor.org/rfc/rfc7672

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/smtp-dane-tls-authentication.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
