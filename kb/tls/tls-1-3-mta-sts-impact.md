---
title: "TLS 1.3 对 MTA-STS 的影响"
source: "https://ztpop.net/kb/tls-1-3-mta-sts-impact.html"
license: CC-BY 4.0
---

# TLS 1.3 对 MTA-STS 的影响

## 一、引言

2018 年 8 月，IETF 先后发布了两个对邮件传输安全至关重要的标准：**RFC 8446（TLS 1.3）**和 **RFC 8461（MTA-STS）**。TLS 1.3 实现了握手延迟从两轮减到一轮的重大改进，并移除了大量不安全的密码套件和特性。MTA-STS 则为发件 MTA 提供了一种用于声明"我支持 TLS，而且你必须使用可信证书连接我"的机制。两个标准的叠加效应深刻改变了 SMTP 传输安全的面貌。

## 二、TLS 1.3 对 SMTP 传输的变革

### 2.1 握手延迟优化

TLS 1.3 使用 1-RTT（一次往返）握手替代了 TLS 1.2 的 2-RTT 握手，对于重连场景甚至支持 0-RTT（零往返）模式。在[SMTP](/kb/smtp-protocol-deep-dive.html) 的 STARTTLS 场景中，这意味着完成 EHLO → STARTTLS → TLS 握手的延迟大幅降低，特别有利于处理大量短期 SMTP 连接（如邮件列表投递、交易邮件）。

不过需要注意：0-RTT 由于存在重放攻击风险，IETF 在 TLS 1.3 规范中明确指出需要应用层自行处理重放保护。邮件传输场景中，对于已有消息去重机制的 MTA 来说风险可控，但敏感系统应禁用 0-RTT。

### 2.2 密码套件变更

TLS 1.3 移除了大量遗留密码套件，仅保留五个 AEAD 套件：

* TLS\_AES\_128\_GCM\_SHA256（强制实现）
* TLS\_AES\_256\_GCM\_SHA384
* TLS\_CHACHA20\_POLY1305\_SHA256
* TLS\_AES\_128\_CCM\_SHA256
* TLS\_AES\_128\_CCM\_8\_SHA256

所有套件都使用 AEAD（Authenticated Encryption with Associated Data），移除了 CBC 模式、RC4、3DES、静态 RSA 密钥交换、压缩等不安全特性。这对于 MTA-STS 的证书验证链来说是好事——避免了接收方因密码套件协商导致的连接降级。

### 2.3 证书验证的变化

TLS 1.3 删除了 renegotiation（重新协商）和客户端证书在服务器端的可选择性（在 SMTP 中已很少使用）。同时，TLS 1.3 要求服务器必须提供完整的证书链。对于 MTA-STS 策略而言，这意味着发送 MTA 必须能够验证接收 MTA 提供的 X.509 证书链至受信任的 CA 根。

## 三、MTA-STS 与 TLS 1.3 的互操作

### 3.1 模式兼容性

RFC 8461 定义的三种 MTA-STS 模式在 TLS 1.3 下均正常工作：

* **testing** — 发件 MTA 尝试建立 TLS 连接但允许降级；TLS 1.3 的握手加速在此模式下可更快发觉兼容性问题。
* **enforce** — 发件 MTA 强制要求 TLS 且证书必须通过验证；TLS 1.3 的 AEAD-only 密码套件使攻击者无法利用降级攻击。
* **none** — 策略已过期或域名退出 MTA-STS；TLS 1.3 的优越性在此模式下无法发挥。

### 3.2 与 DANE 的竞争与合作

[DANE TLSA](/kb/dane-smtp.html) 基于 DNSSEC，不依赖公共 CA。RFC 7672 定义的 DANE 在 TLS 1.3 下同样工作良好——DANE 更关注证书的公钥或主题匹配，而非 CA 信任链，因而对 TLS 1.3 的证书验证变化不敏感。在实践中，两者可以互补：MTA-STS 提供 .well-known 远端的策略获取（依赖 HTTPS），DANE 提供 DNS 原生策略获取（依赖 DNSSEC）。

Google 的 MTA-STS 部署指南明确建议同时配置 MTA-STS 和 DANE TLSA。在 TLS 1.3 环境下，发件 MTA 应优先尝试 DANE，若 DNSSEC 不可用则回退到 MTA-STS，最后回退到传统的 STARTTLS。

## 四、部署建议

### 4.1 证书管理

TLS 1.3 不再支持 RSA 密钥交换，但 RSA 签名证书仍可使用。推荐使用 ECDSA 证书以获得更佳性能。证书有效期应控制在 MTA-STS 策略的 max\_age（典型 86400 秒 = 1 天）以上。

### 4.2 服务端配置

以 Postfix 为例，启用 TLS 1.3 和 MTA-STS 的关键配置：

```
smtpd_tls_protocols = !SSLv2, !SSLv3, !TLSv1, !TLSv1.1, TLSv1.2, TLSv1.3
smtpd_tls_mandatory_protocols = !SSLv2, !SSLv3, !TLSv1, !TLSv1.1, TLSv1.2, TLSv1.3
smtp_tls_protocols = !SSLv2, !SSLv3, !TLSv1, !TLSv1.1, TLSv1.2, TLSv1.3
smtp_tls_mandatory_protocols = !SSLv2, !SSLv3, !TLSv1, !TLSv1.1, TLSv1.2, TLSv1.3
smtp_tls_mandatory_ciphers = high
```

## 五、总结

TLS 1.3 对 MTA-STS 的积极影响是全方位的：更低的握手延迟改善了大容量邮件投递的吞吐能力；移除不安全密码套件减少了攻击面；完整的证书链要求与 MTA-STS 的 enforce 策略天然契合。随着 2026 年 TLS 1.2 和 1.3 已成为邮件传输的事实标准，所有邮件系统运营者都应确保 SMTP 服务启用 TLS 1.3，并配置 [MTA-STS 策略](/kb/mta-sts-guide.html)和 [TLS-RPT 报告](/kb/tls-rpt-guide.html)。

### 相关文章

* [MTA-STS 配置指南](/kb/mta-sts-guide.html)
* [DANE SMTP 部署指南](/kb/dane-smtp.html)
* [TLS 邮件加密体系](/kb/tls-email-encryption.html)
* [邮件 TLS 策略强制](/kb/email-tls-policy-enforcement.html)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/tls-1-3-mta-sts-impact.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
