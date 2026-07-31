---
title: "RFC 7672 DANE for SMTP：用 DNS 公钥钉住杜绝 STARTTLS 降级攻击"
source: "https://ztpop.net/kb/rfc7672-dane-for-smtp.html"
license: CC-BY 4.0
---

# RFC 7672 DANE for SMTP：用 DNS 公钥钉住杜绝 STARTTLS 降级攻击

## 概述

RFC 7672 把 DANE（基于 DNS 的命名实体认证）应用到 SMTP 传输。它借助 DNSSEC 保护的 `TLSA` 记录，向发送方"钉住"（pin）接收方 MX 服务器预期使用的证书或受信任 CA。这样即便攻击者能篡改网络流量，也无法用自签/伪造证书冒充对端——因为发送方会拿 DNS 里的预期值核对。

## 为什么需要 DANE：STARTTLS 的软肋

原生 SMTP 的 `STARTTLS` 是"机会性加密"：服务器先告知支持加密，客户端再升级。主动攻击者可在中间剥离 `STARTTLS` 声明（STRIPTLS），让双方以为"对方不支持加密"而退回明文。由于传统 PKI 不要求 SMTP 证书与域名强绑定，攻击者还能出示任意有效 CA 签发的证书做中间人。DANE 正是为堵这两个洞而生。

## TLSA 记录与匹配模式

TLSA 记录由四个字段组成：证书用法（Certificate Usage）、选择符（Selector）、匹配类型（Matching Type）与证书关联数据。常见用法：

* **PKIX-TA (0)**：信任锚为该 CA，证书须由其签发；
* **PKIX-EE (1)**：信任锚为终端实体证书本身；
* **DANE-TA (2)**：用自有（非公开 CA）信任锚；
* **DANE-EE (3)**：直接钉住终端实体证书/公钥，最严格，无需公开 CA。

## 与 DNSSEC 强绑定

DANE 的安全完全依赖 DNSSEC：若 DNS 响应可被伪造，攻击者改 TLSA 记录就能攻破钉住。因此**没有 DNSSEC 就没有可信 DANE**。部署 DANE 前必须先为邮件域启用并正确签名 DNSSEC。

## 与 MTA-STS 的关系

两者目标一致（防 SMTP 降级/明文），但机制互补：

| 维度 | DANE (RFC 7672) | MTA-STS (RFC 8461) |
| --- | --- | --- |
| 前提 | 需 DNSSEC | 无需 DNSSEC |
| 信任源 | DNS TLSA 记录 | HTTPS 发布的策略文件 |
| 证书钉住 | 强（可钉公钥） | 弱（仅要求有效证书） |
| 部署复杂度 | 较高 | 较低 |

最佳实践：两者同时启用——DANE 提供最强保证，MTA-STS 为尚未部署 DNSSEC 的对端提供兜底。

## 部署现状

受限于 DNSSEC 普及率，DANE for SMTP 在欧美政府邮件中采用较多，商业领域仍在爬坡。对高安全等级的信创邮件（金融、军工、政务），DANE + DNSSEC 是值得投入的"传输层零信任"能力。

### 相关主题

* [DANE for SMTP 概览](/kb/dane-smtp.html)：用 DNS 钉住证书
* [DANE/TLSA 部署实战](/kb/dane-tlsa-smtp-deployment.html)：记录生成与排错
* [DANE vs MTA-STS vs TLS-RPT](/kb/smtp-dane-mta-sts-tls-rpt-comparison.html)：三者如何互补
* [RFC 8461 MTA-STS](/kb/rfc8461-mta-sts.html)：强制加密传输策略
* [RFC 8460 TLS-RPT](/kb/rfc8460-tls-rpt.html)：加密失败的可视化报告

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/rfc7672-dane-for-smtp.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
