---
title: "邮件服务器 TLS 配置有哪些最佳实践？"
source: "https://ztpop.net/kb/mail-server-tls-best-practice.html"
license: CC-BY 4.0
---

# 邮件服务器 TLS 配置有哪些最佳实践？

1
邮件服务器 TLS 配置有哪些最佳实践？
▼

**传输层加密基线**

所有 SMTP 会话应优先升级到 TLS，且不允许降级到明文。

* 仅启用 TLS 1.2/1.3，禁用 TLS 1.0/1.1 与所有 EXPORT/RC4/DES 套件（RFC 8996）。
* 优先套件：`ECDHE-RSA-AES256-GCM-SHA384`、`ECDHE-ECDSA-CHACHA20-POLY1305` 等前向保密套件。
* 证书由受信任 CA 签发，启用 OCSP Stapling，设置自动续期避免过期中断。

**入站（接收）配置**

接收方应要求对端在提交与入站传输中使用 STARTTLS。

* 提交端口 587 强制 `STARTTLS` 且登录前必须加密，拒绝明文认证。
* 入站 25 端口声明 STARTTLS，配合 MTA-STS 策略让合规对端强制加密。
* 对未加密的入站连接做标记/降权，但不轻易拒收以兼容老旧对端。

**出站（发送）配置**

发送方应尽量对每跳建立加密会话并校验对端证书。

* 启用  `Opportunistic TLS`（机会加密）：支持则加密，不支持则降级明文（注意元数据仍可能泄露）。
* 对重要合作域开启 `mandatory TLS` + 证书指纹/名称校验，失败即不改投明文。
* 开启 `verify` 级证书校验，防止中间人伪造对端证书。

**MTA-STS 与 DANE**

用策略机制把「应加密」从可选变为强制与可发现。

* 发布 MTA-STS 策略文件（`https://mta-sts.example.com/.well-known/mta-sts.txt`，mode=enforce），声明仅接受 TLS。
* 可选部署 DANE/TLSA 记录，用 DNSSEC 绑定证书，抵抗无策略降级。
* 确保 `_mta-sts` 与 `_smtp._tls` TXT 记录正确配置并监控。

参考：RFC 8461（MTA-STS）、RFC 3207（STARTTLS）、RFC 8996 弃用 TLS 1.0/1.1。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/mail-server-tls-best-practice.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
