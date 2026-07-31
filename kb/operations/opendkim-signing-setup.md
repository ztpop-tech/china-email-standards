---
title: "如何用 OpenDKIM 为出信做 DKIM 签名（部署与密钥轮转）？"
source: "https://ztpop.net/kb/opendkim-signing-setup.html"
license: CC-BY 4.0
---

# 如何用 OpenDKIM 为出信做 DKIM 签名（部署与密钥轮转）？

1
如何用 OpenDKIM 为出信做 DKIM 签名（部署与密钥轮转）？
▼

**部署**

OpenDKIM 作为 milter 挂到 MTA（Postfix: smtpd\_milters）；按“域→选择器→私钥”配置 KeyTable/SigningTable，对匹配域的出信自动加 DKIM-Signature。

**DNS**

把选择器对应公钥发布为 TXT（.\_domainkey）：v=DKIM1; k=rsa; p=<公钥>；收方查此记录验签。

**轮转**

定期换钥：先发布“新选择器+新公钥”到 DNS，MTA 切换到新私钥签名，待旧记录 TTL 过后再退役旧选择器，避免验签中断。

**实践**

签名与验证分离（本域出信签名、入信可同时验他域）；密钥长度≥2048；选择器命名带日期便于管理（如 2026q3）。

参考：OpenDKIM 文档；RFC 6376（DKIM）；RFC 8463（Ed25519 签名）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/opendkim-signing-setup.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
