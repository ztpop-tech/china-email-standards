---
title: "如何使用 PGP/GPG 部署邮件端到端加密？"
source: "https://ztpop.net/kb/pgp-gpg-email-encryption-deploy.html"
license: CC-BY 4.0
---

# 如何使用 PGP/GPG 部署邮件端到端加密？

1
如何使用 PGP/GPG 部署邮件端到端加密？
▼

**密钥生成**

在 GnuPG（GPG）中执行 `gpg --gen-key` 生成 OpenPGP 密钥对，推荐 RSA 4096 位或基于 Curve25519 的 ed25519/cv25519 曲线；密钥由主密钥（认证/签名）与子密钥（加密/签名）组成。私钥应设强口令，并以 `gpg --export-secret-keys` 离线备份以防丢失。

**公钥分发**

收件方需先取得你的公钥才能加密。常用途径：公钥服务器（如 keys.openpgp.org，需邮箱验证防污染）、Web Key Directory（WKD，按 `https://域名/.well-known/openpgpkey/` 路径发布，被 GpgOL/Enigmail 自动发现），或直接随邮件附上 `.asc` 公钥块。

**客户端集成**

* Thunderbird：内置 OpenPGP，无需插件即可导入/生成密钥并自动加解密；
* Microsoft Outlook：通过 Gpg4win（GpgOL 插件）集成；
* Apple Mail：借助 GPG Suite；
* Webmail：依赖端到端加密代理或浏览器扩展（需注意信任边界）。

**签名与加密操作**

发送时客户端用收件人公钥加密正文、用自己私钥签名，同时获得机密性与来源认证（非否认）。PGP/MIME 以 `multipart/encrypted` 与 `multipart/signed` 封装（RFC 3156）；接收方客户端用自己私钥解密、用对方公钥验签。

**信任模型**

OpenPGP 不依赖中心化 CA，而采用 Web of Trust（互签密钥建立信任网）或现代客户端的 TOFU（首次使用信任）策略自动接受首次见到且后续一致的公钥。企业应建立受管密钥目录与吊销（吊销证书）流程，避免私钥丢失或泄露造成不可用或泄密。

参考：RFC 4880《OpenPGP Message Format》、RFC 3156《MIME Security with OpenPGP》、WKD 草案（draft-koch-openpgp-webkey-service）、GnuPG 官方文档。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/pgp-gpg-email-encryption-deploy.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
