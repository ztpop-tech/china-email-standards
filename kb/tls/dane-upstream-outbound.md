---
title: "DANE for Outbound 出站部署"
source: "https://ztpop.net/kb/dane-upstream-outbound.html"
license: CC-BY 4.0
---

# DANE for Outbound 出站部署

## DANE协议概述

DNS-Based Authentication of Named Entities（DANE）由RFC 6698定义，是一种通过DNSSEC验证TLS证书合法性的机制。DANE的核心价值在于打破传统PKI（公钥基础设施）的CA信任模型——通过TLSA（TLS Association）DNS记录，域名所有者可以指定哪些证书或CA被授权用于该域名的TLS服务，或直接指定证书的公钥哈希值。

在SMTP场景中，RFC 7672将DANE应用于SMTP STARTTLS的安全要求。不同于MTA-STS依赖于CA签发的HTTPS证书来分发策略，DANE通过DNSSEC实现了完全自控的证书绑定机制，消除了对第三方CA的信任依赖。

## TLSA记录结构与类型

### 记录格式

TLSA记录的查询域格式为：\_port.\_protocol.hostname。对于SMTP，典型查询域为\_25.\_tcp.mail.example.com。TLSA记录包含三个数字字段（Certificate Usage、Selector、Matching Type）和一个证书关联数据。

```
; TLSA记录格式
_25._tcp.mail.example.com IN TLSA (
  3 1 1  (
    AABBCCDDEEFF00112233445566778899AABBCCDDEEFF00112233445566778899
  )
)

; 参数说明：
; 字段1 - Certificate Usage (3 = DANE-EE: Domain Issued Certificate)
; 字段2 - Selector (1 = SPKI: Subject Public Key Info)
; 字段3 - Matching Type (1 = SHA-256)
; 关联数据 - 64字节公钥的SHA-256哈希（十六进制）
```

### 四种Certificate Usage类型

RFC 6698 §2.1.1定义了四种Usage类型，每种对应不同的信任锚定方式：

| Usage值 | 名称 | 信任锚 | SMTP推荐 |
| --- | --- | --- | --- |
| 0 | PKIX-TA | CA证书（信任锚） | 不推荐——仍依赖CA |
| 1 | PKIX-EE | 终端实体证书 | 可选——需CA+端点双重验证 |
| 2 | DANE-TA | 域名所有者指定的信任锚 | 推荐——自控CA |
| 3 | DANE-EE | 域名所有者指定的公钥 | 最推荐——完全自控 |

RFC 7672 §1建议SMTP出站场景优先使用Usage 3（DANE-EE）配合Selector 1（SPKI）和Matching Type 1（SHA-256）。这种组合最安全——即使CA被攻破签发虚假证书，攻击者也无法伪造匹配的公钥哈希。

## 部署前提：DNSSEC

DANE的前提条件是域名必须部署DNSSEC（RFC 4033-4035）。TLSA记录作为DNSSEC签名区域的一部分，其完整性由DNSSEC链式信任保证。部署DNSSEC的关键步骤：

1. DNSSEC Key Generation：生成ZSK（Zone Signing Key）和KSK（Key Signing Key）
2. DS Record：将KSK的DS记录提交到父域注册商
3. Zone Signing：使用ZSK对区域中的TLSA等记录进行签名
4. 验证：通过dnssec-verify工具验证签名链完整性

```
# 检查域名DNSSEC状态
$ dig example.com DNSKEY +short
# 若返回DNSKEY记录则表明域已配置DNSSEC

$ delv -t TLSA _25._tcp.mail.example.com
# 使用delv执行DNSSEC验证查询
# 成功输出应显示 fully validated

# 手动验证签名链
$ dig _25._tcp.mail.example.com TLSA +dnssec +multiline
```

## DANE TLSA记录生成实战

以邮件服务器mail.example.com使用Let's Encrypt证书为例，生成TLSA记录的完整流程：

```
# 1. 获取证书公钥
$ openssl x509 -in /etc/ssl/certs/mail.example.com.pem -pubkey -noout > pubkey.pem

# 2. 提取SPKI（Subject Public Key Info）的SHA-256哈希
$ openssl pkey -in pubkey.pem -pubin -outform DER | \
    openssl dgst -sha256 -c | sed 's/.*= //; s/://g'

# 输出：aabbccddeeff001122334455667788990011223344556677889900aabbccdd

# 3. 生成的TLSA记录（Usage 3, Selector 1, Matching Type 1）
_25._tcp.mail.example.com IN TLSA 3 1 1 (
  AABBCCDDEEFF00112233445566778899
  AABBCCDDEEFF00112233445566778899
)
```

证书更新时必须同步更新TLSA记录（因为公钥哈希变了）。建议设置TLSA记录的TTL不超过证书剩余有效期的一半，且不超过3600秒。TLSA记录的更新应在证书轮转前完成，给予DNS传播时间。

## 出站DANE验证工作原理

当邮件发送方MTA向example.com的MX主机投递邮件时，DANE验证流程如下：

1. 发送方查询example.com的MX记录获取mail.example.com
2. 发送方查询\_25.\_tcp.mail.example.com的TLSA记录（通过DNSSEC验证）
3. 若TLSA记录存在且验证有效：连接必须使用TLS，且证书必须符合TLSA关联要求
4. 若TLSA记录不存在：回退到STARTTLS机会主义加密或无加密
5. 若TLSA记录存在但DNSSEC验证失败：根据RFC 7672 §3.3，发送方必须中止连接或回退（但安全上不应信任未签名的TLSA记录）

```
# 在Postfix中启用出站DANE验证
# /etc/postfix/main.cf

# 启用DANE出站验证
smtp_tls_security_level = dane
smtp_tls_CAfile = /etc/ssl/certs/ca-certificates.crt
smtp_dns_support_level = dnssec

# DANE仅支持DNSSEC验证的DNS
smtp_host_lookup = dns

# 验证日志级别
smtp_tls_loglevel = 1

# 在master.cf中启用DANE的传递服务
# 需要在系统DNS解析器中启用DNSSEC（使用unbound或knot-resolver）
```

Postfix的smtp\_tls\_security\_level = dane为每个目标域自动执行DANE验证。当TLSA记录不存在时降级为may（机会主义TLS）；当TLSA记录存在但验证失败时，拒绝投递。

## DANE与MTA-STS的对比与协同

DANE（RFC 7672）和MTA-STS（RFC 8461）是邮件传输层安全的两大支柱。两者的核心区别对比：

| 维度 | DANE | MTA-STS |
| --- | --- | --- |
| 信任根 | DNS根（通过DNSSEC） | CA证书（通过HTTPS） |
| DNSSEC依赖 | 必需 | 不需要 |
| 策略分发 | DNS TLSA记录 | HTTPS / .well-known/mta-sts.txt |
| 报告机制 | 无原生报告 | TLS-RPT（RFC 8460） |
| 优先顺序 | DANE优先（RFC 7672 §2.2） | DANE不存在时应用 |
| 证书锚定 | 域名所有者自控 | 依赖第三方CA |

RFC 7672 §2.2明确指出：当同时部署DANE和MTA-STS且两者一致时，优先使用DANE的证书要求。因为DANE的TLSA记录通过DNSSEC提供了更强的安全保证。实际部署中，DANE更适合有DNSSEC能力的组织，MTA-STS则适合所有域名。对于大型邮件运营商，同时部署两者是最佳实践——DANE提供最高安全性，MTA-STS提供TLS-RPT报告和更细粒度的策略控制。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/dane-upstream-outbound.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
