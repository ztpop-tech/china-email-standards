---
title: "SMTP DANE vs MTA-STS vs TLS-RPT 三选一对比决策"
source: "https://ztpop.net/kb/smtp-dane-mta-sts-tls-rpt-comparison.html"
license: CC-BY 4.0
---

# SMTP DANE vs MTA-STS vs TLS-RPT 三选一对比决策

DANE TLSA（RFC 7671）、MTA-STS（RFC 8461）和 TLS-RPT（RFC 8460）是 SMTP 传输加密策略的三大支柱。三者定位不同、依赖条件不同、安全强度不同。本文从七个维度进行横向对比，帮助运维团队做出合理的部署决策。

## 三者定位概述

DANE vs MTA-STS vs TLS-RPT 核心定位

| 协议 | 标准 | 核心定位 | 解决的核心问题 |
| --- | --- | --- | --- |
| DANE TLSA | RFC 7671（SMTP） RFC 6698（基础） | 基于 DNSSEC 的证书绑定 | 无需依赖 CA，自主验证 MTA 证书合法性 |
| MTA-STS | RFC 8461 | 基于 HTTPS 的策略分发 | 强制 TLS 加密，消除 STARTTLS 降级 |
| TLS-RPT | RFC 8460 | TLS 连接失败报告 | 运维可视性：发现 TLS 故障并修复 |

## 维度一：DNSSEC 依赖

这是三者在信任模型上的根本差异：

* **DANE**：强依赖 DNSSEC。TLSA 记录的验证链完全建立在 DNSSEC 之上。没有 DNSSEC 签名，TLSA 记录可被篡改，DANE 起不到任何绑定作用。RFC 7671 §4 明确要求发送方 MTA 必须验证 DNSSEC 签名。
* **MTA-STS**：不依赖 DNSSEC。策略通过 HTTPS 分发（从 `mta-sts.域名` 获取 JSON 文件），信任模型基于 Web PKI。
* **TLS-RPT**：不依赖 DNSSEC。报告通过 SMTP 邮件或 HTTPS POST 投递。

DNSSEC 部署率在中国大陆仍较低。如果域名未部署 DNSSEC，DANE 不可用，应转而部署 MTA-STS + TLS-RPT。

## 维度二：安全强度对比

安全强度评估

| 评估维度 | DANE TLSA | MTA-STS |
| --- | --- | --- |
| 防 STRIPTLS | ⭐⭐⭐ Enforce 模式强制 TLS | ⭐⭐⭐ Enforce 模式强制 TLS |
| 防中间人 | ⭐⭐⭐⭐ DNSSEC 签名验证，无 CA 信任链风险 | ⭐⭐⭐ 依赖 Web PKI，存在 CA 被攻破风险 |
| 防 CA 妥协 | ⭐⭐⭐⭐ 证书与 CA 解耦，TLSA 指纹直接绑定公钥 | ⭐⭐ 信任链断在 CA；妥协 CA 可签发假证书 |
| 策略新鲜度 | ⭐⭐⭐ 受 DNSSEC TTL 控制，刷新依赖签名 | ⭐⭐⭐⭐ 可通过 max\_age 控制，缓存刷新策略灵活 |
| 回退安全性 | ⭐⭐⭐⭐ 无 DNSSEC 签名时连接失败（DNSSEC 验证失败） | ⭐⭐ 策略获取失败可能回退到普通 STARTTLS（RFC 8461 §4.3） |

## 维度三：配置复杂度

**DANE 部署路径**：

```
# 前置条件
1. 域名注册 DNSSEC 签名（通过 DNS 托管商配置 DS 记录）
2. DNS 区域支持 TLSA 记录类型

# TLSA 记录生成
# 使用 postfix tls 工具
posttls-finger -l 25 mx.example.com

# 手动生成 TLSA 记录（RFC 6698 §2.1.3）
# Usage: 3 (DANE-EE: 终端实体证书关联)
# Selector: 1 (SPKI: 公钥) 
# Match: 1 (SHA-256)
openssl x509 -in /etc/ssl/certs/mx-cert.pem \
  -pubkey -noout | openssl pkey -pubin -outform DER | \
  openssl dgst -sha256

# DNS 记录示例：
_25._tcp.mx.example.com. IN TLSA 3 1 1 \
  abcd1234efab5678... (64 hex chars)
```

**MTA-STS 部署路径**：

```
# 前置条件
1. 有效的 TLS 证书（DV 即可）
2. HTTPS 可访问的 Web 服务器（或同一域名的静态托管）

# DNS TXT 记录
_mta-sts.example.com. IN TXT "v=STSv1; id=2026072401;"

# HTTPS 策略文件（部署在 https://mta-sts.example.com/.well-known/mta-sts.txt）
{
  "version": "STSv1",
  "mode": "testing",   # ← 先 testing，验证无误后改为 enforce
  "mx": ["mx.example.com.", "mx2.example.com."],
  "max_age": 86400
}

# Nginx 配置示例
location = /.well-known/mta-sts.txt {
    alias /var/www/mta-sts/policy.json;
    add_header Content-Type "text/plain; charset=utf-8";
    add_header Cache-Control "public, max-age=3600";
}
```

**TLS-RPT 部署路径**：

```
# DNS TXT 记录
_smtp._tls.example.com. IN TXT \
  "v=TLSRPTv1; rua=mailto:tls-reports@example.com;"

# 接收报告的邮件地址
# 建议设置专用邮箱 + 自动处理脚本
```

## 维度四：推荐部署组合

按场景推荐部署策略

| 场景 | 推荐组合 | 理由 |
| --- | --- | --- |
| 已部署 DNSSEC | **DANE Enforce + MTA-STS Testing → Enforce + TLS-RPT** | DANE 提供无 CA 认证，MTA-STS 兼容非 DNSSEC 接收方 |
| 未部署 DNSSEC | **MTA-STS Enforce + TLS-RPT** | DNSSEC 不是 MTA-STS 的前置条件 |
| 大型邮件服务商 | **DANE Enforce + MTA-STS Enforce + TLS-RPT + 证书透明度** | 双重保障，提升互操作性 |
| 中国大陆域名 | **MTA-STS Testing → Enforce + TLS-RPT** | DNSSEC 部署率低，优先 MTA-STS |

## 维度五：失败处理对比

失败场景对比

| 失败场景 | DANE | MTA-STS |
| --- | --- | --- |
| DNS 查询失败（DNSSEC 验证失败） | ❌ 连接失败（RFC 7671 §5） | 不适用（不依赖 DNSSEC） |
| TLSA 记录不存在 | 回退到普通 SMTP（无强制加密） | 不适用 |
| 证书不匹配 TLSA | ❌ 连接失败（安全终止） | 不适用 |
| 策略文件不可达 | 不适用 | max\_age 缓存期内使用缓存策略；期满后回退 |
| TLS 握手失败 | ❌ 连接失败 | Enforce: ❌; Testing: ⚠️ 记录后继续 |

## Postfix 配置参考

```
# DANE 配置
smtp_tls_security_level = dane
smtp_dns_support_level = dnssec
smtp_tls_CAfile = /etc/ssl/certs/ca-certificates.crt
smtp_tls_protocols = !SSLv2, !SSLv3, !TLSv1, !TLSv1.1
smtp_tls_mandatory_protocols = !SSLv2, !SSLv3, !TLSv1, !TLSv1.1
smtp_tls_mandatory_ciphers = medium
# DANE only 模式（严格）：仅对 DNSSEC 签名域使用 DANE
smtp_tls_security_level = dane
smtp_tls_dane_usage_requested = 3  # DANE-EE

# MTA-STS 需要通过 TLS 策略缓存实现
# Postfix 3.5+ 原生支持（via tls_policy 文件或 DANE fallback）
# 也可以使用外部工具：postfix-mta-sts-resolver

# TLS-RPT 不需要 Postfix 端配置
# 接收方配置 DNS 即可接收报告
```

### 核心要点

* DANE 安全强度最高，但强制依赖 DNSSEC — 没有 DNSSEC 就没有 DANE
* MTA-STS 是普适方案，兼容性最好，但安全上限低于 DANE（依赖 Web PKI）
* TLS-RPT 是运维必选项 — 没有报告就无法发现 TLS 失败
* 最安全组合 = DANE Enforce + MTA-STS Enforce + TLS-RPT
* 中国大陆场景推荐优先 MTA-STS + TLS-RPT，择机部署 DNSSEC 后再叠加 DANE

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/smtp-dane-mta-sts-tls-rpt-comparison.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
