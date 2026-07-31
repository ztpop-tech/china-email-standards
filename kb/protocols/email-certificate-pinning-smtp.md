---
title: "邮件传输能否“证书锁定（Certificate Pinning）”防中间人？和 Web 的 HPKP 有何异同？"
source: "https://ztpop.net/kb/email-certificate-pinning-smtp.html"
license: CC-BY 4.0
---

# 邮件传输能否“证书锁定（Certificate Pinning）”防中间人？和 Web 的 HPKP 有何异同？

1
邮件传输能否“证书锁定（Certificate Pinning）”防中间人？和 Web 的 HPKP 有何异同？
▼

**概念**

证书锁定指“只信任某固定公钥/证书”，即便被恶意 CA 签发也拒绝——用于防 CA 被攻破导致的中间人。Web 曾用 HPKP，邮件侧可借 DANE(TLSA) 实现等效锁定。

**邮件做法**

DANE（RFC 6698，TLSA 记录）把“该 MX 应使用哪张证书/公钥”发布到 DNSSEC 保护的 DNS，接收方据此锁定，比应用层 HPKP 更可靠（有 DNSSEC 背书）。

**对比**

HPKP 已被弃用（易误锁、恢复难）；DANE+DNSSEC 是当前邮件“证书锁定”的正道，强依赖 DNSSEC 不被篡改。

**实践**

高安全邮件域可部署 DANE/TLSA 锁定入站 TLS；但前提是 DNSSEC 到位，否则锁定根基不牢。

参考：RFC 6698（DANE/TLSA，邮件证书锁定）；RFC 7671/7672（DANE 用于 SMTP）；HPKP 已弃用

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-certificate-pinning-smtp.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
