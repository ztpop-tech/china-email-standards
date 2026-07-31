---
title: "RFC 8301 DKIM 加密算法更新：密钥强度与哈希的现代基线"
source: "https://ztpop.net/kb/rfc8301-dkim-crypto-update.html"
license: CC-BY 4.0
---

# RFC 8301 DKIM 加密算法更新：密钥强度与哈希的现代基线

## 概述

DKIM（RFC 6376）用非对称签名保证邮件完整性与信头 From 可信。但随着算力提升，早期允许的短密钥与 SHA-1 哈希已不再安全。RFC 8301 作为对 RFC 6376 的更新，明确**废弃 SHA-1、要求 RSA 密钥至少 1024 位（强烈推荐 2048 位），并引入 Ed25519（RFC 8463）作为更轻量的曲线**，把 DKIM 的密码学基线拉到现代水平。

## 关键更新

| 项 | RFC 6376 旧基线 | RFC 8301 新要求 |
| --- | --- | --- |
| 哈希算法 | SHA-1 允许 | 禁止 SHA-1，必须 SHA-256 |
| RSA 密钥长度 | 512/1024 可接受 | ≥1024 位，推荐 2048 位 |
| 新算法 | — | 支持 Ed25519 (RFC 8463) |

## 为什么 SHA-1 必须退役

SHA-1 已被实际攻破（碰撞攻击），攻击者理论上可构造不同内容但同哈希的邮件，削弱 DKIM 的完整性保证。RFC 8301 要求签名与密钥都用 SHA-256，接收方对仍用 SHA-1 的签名应按失败处理。实际上主流接收方（Gmail、Microsoft 365）早已拒绝 SHA-1 签名的 DKIM。

## 密钥轮换与强度权衡

2048 位 RSA 更安全但 DNS 中存 TXT 记录更长（需分段）；Ed25519 密钥短、验签快，适合高吞吐邮件系统。无论哪种，都应按 RFC 6376 + M3AAWG 建议定期轮换（多选择器平滑切换），私钥安全存储。信创邮件系统对外发信默认 2048 位 RSA + SHA-256 是最稳妥的起点。

## 对信创邮件与网关的启示

邮件安全网关签发 DKIM 时，应：禁用 SHA-1、RSA 默认 2048、启用选择器轮换；入站验证拒绝 SHA-1 与弱密钥签名。这直接对齐 NIST SP 800-177r1 对 DKIM ≥2048 位的建议，是 DMARC 对齐成功的前提。

### 相关主题

* [DKIM 完全指南](/kb/dkim-guide.html)：签名与验证原理
* [DKIM 密钥轮换管理](/kb/dkim-key-rotation-management.html)：多选择器平滑切换
* [NIST SP 800-177r1 可信电子邮件](/kb/nist-sp800-177r1-trustworthy-email.html)：DKIM ≥2048 位建议
* [DMARC 完全指南](/kb/dmarc-guide.html)：对齐依赖 DKIM 结论
* [M3AAWG DKIM 密钥轮换 BCP](/kb/m3aawg-dkim-key-rotation-bcp.html)：轮换最佳实践

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/rfc8301-dkim-crypto-update.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
