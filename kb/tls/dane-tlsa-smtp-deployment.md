---
title: "DANE TLSA for SMTP 完全部署指南：RFC 7671/7672、记录生成与Postfix集成"
source: "https://ztpop.net/kb/dane-tlsa-smtp-deployment.html"
mirror_date: 2026-07-25
license: CC-BY 4.0
---

# DANE TLSA for SMTP 完全部署指南：RFC 7671/7672、记录生成与Postfix集成

## 1. DANE for SMTP 协议栈

### 1.1 标准化路径

DANE for SMTP建立在两条核心RFC之上：RFC 6698（DANE TLSA基础规范）[1]定义了TLSA记录格式和验证规则；RFC 7672（SMTP Security via Opportunistic DANE TLS）[2]定义了SMTP特有约束——包括仅允许Usage 2和Usage 3、TLSA记录位置为\_25.\_tcp.MX-hostname.、出站MTA在启用了DANE安全级别时必须拒绝连接到不支持TLS的接收方。后续RFC 7218明确了DNSSEC对DANE验证的"all-or-nothing"原则——如果TLSA记录的DNSSEC验证失败，视为不安全，不能降级信任 [3]。

### 1.2 与MTA-STS的比较

| 维度 | DANE for SMTP | MTA-STS (RFC 8461) |
| --- | --- | --- |
| 信任根 | DNSSEC（根区签名） | Web PKI/CA体系 |
| 策略分发 | TLSA记录（DNS） | \_mta-sts.example.com TXT + HTTPS JSON |
| 证书验证 | 单次DNS查询即验证 | 解析JSON策略文件后验证 |
| DNSSEC依赖 | 强依赖（无DNSSEC即不可用） | 不依赖 |
| 自签名证书 | 支持（Usage 3） | 不支持（需CA签发） |

部署建议：DNSSEC就绪且域名ECS可用的场景优先使用DANE；否则使用MTA-STS。两者可共存，Postfix会自动择优——DANE级别高于MTA-STS [2] §4。

## 2. 前置条件：DNSSEC部署与验证

### 2.1 DNSSEC签名链

DANE的安全性完全依赖DNSSEC对TLSA记录的完整性保护。如果域名未部署DNSSEC，TLSA记录可以被中间人篡改，DANE验证形同虚设。完整的DNSSEC签名链需要：KKS（密钥签名密钥）和ZSK（区域签名密钥）生成 → DS记录上传至父域注册商 → 区域签名 → 验证DNSSEC链。

```
# 验证DNSSEC状态（支持DANE的解析器）
delv -t TLSA _25._tcp.mail.example.com +multi
# 应返回签名验证成功标志

# 使用DNSViz检查链完整性
# https://dnsviz.net 或本地
python3 -c "
import dns.resolver
res = dns.resolver.Resolver()
res.use_dnssec = True  # 仅适用于支持EDNS0 DNSSEC OK的解析器
try:
    answer = res.resolve('example.com', 'DNSKEY')
    print(f'DNSKEY记录数: {len(answer)}')
    print('DNSSEC已启用')
except Exception as e:
    print(f'DNSSEC错误: {e}')
"
```

## 3. TLSA记录生成

### 3.1 选择TLSA参数组合

RFC 7672 §3规定SMTP DANE仅允许两种证书使用模式：Usage 2（DANE-TA, Trust Anchor Assertion）和Usage 3（DANE-EE, Domain-Issued Certificate）[2]。推荐组合如下：

| 场景 | Usage | Selector | Matching | 说明 |
| --- | --- | --- | --- | --- |
| 自签名证书（推荐） | 3 | 1 (SPKI) | 1 (SHA-256) | 证书变更时仅需更新TLSA记录 |
| CA签发证书（兼容） | 2 | 0 (Cert) | 1 (SHA-256) | 信任CA而非具体证书 |
| 最严格固定 | 3 | 0 (Cert) | 1 (SHA-256) | 具体证书绑定，变更必须同时换证书和TLSA |

### 3.2 使用hash-slinger生成

```
# hash-slinger 是标准TLSA记录生成工具
# https://github.com/ietf-wg-dane/hash-slinger

# 安装
apt-get install hash-slinger  # Debian/Ubuntu
# 或 pip install hash-slinger

# 生成 Usage 3 + Selector 1 + Matching 1 (最常用)
tlsa --create --certificate /etc/ssl/certs/mail.example.com.pem \
     --usage 3 --selector 1 --matching-type 1 \
     _25._tcp.mail.example.com

# 输出示例:
# _25._tcp.mail.example.com. IN TLSA 3 1 1 (
#   AB12CD34EF567890AB12CD34EF567890
#   AB12CD34EF567890AB12CD34EF567890 )
#  (256 bits)
```

### 3.3 使用openssl手动计算

```
# 有时需要手动计算（如hash-slinger不可用）

# 1. 获取服务器证书
openssl s_client -starttls smtp -connect mail.example.com:25 \
    -servername mail.example.com < /dev/null 2>/dev/null \
    | openssl x509 -outform PEM > /tmp/mail_cert.pem

# 2. 提取主题公钥信息 (SPKI) — Selector 1
openssl x509 -in /tmp/mail_cert.pem -noout -pubkey > /tmp/spki.pem

# 3. 计算 SHA-256 哈希 — Matching Type 1
openssl dgst -sha256 /tmp/spki.pem \
    | awk '{print $2}' \
    | tr '[:upper:]' '[:lower:]'

# 4. 完整的TLSA记录
# _25._tcp.mail.example.com. IN TLSA 3 1 1 ab12cd34ef567890...
```

### 3.4 使用swaks验证

```
# swaks (Swiss Army Knife for SMTP) 支持DANE验证
# https://github.com/jetmore/swaks

swaks --server mail.recipient.com --tls \
  --tls-get-peer-cert --tls-cipher ECDHE-RSA-AES256-GCM-SHA384 \
  --tls-verify-dane \
  -f test@sender.com -t test@recipient.com

# 日志中应显示 DANE verification passed
```

## 4. Postfix DANE 端到端配置

### 4.1 出站（发送方）配置

```
# /etc/postfix/main.cf — DANE出站配置

# 安全级别：dane 要求 TLSA 记录存在且验证通过
# 如果接收域 DNSSEC 完整但有 TLSA 记录，Postfix 自动使用 DANE
# 如无 TLSA 记录，回退到 smtp_tls_security_level 指定的策略
smtp_tls_security_level = dane

# 强制 DNSSEC 解析
smtp_dns_support_level = dnssec

# 系统 CA 包（用于 Usage 2 回退验证）
smtp_tls_CAfile = /etc/ssl/certs/ca-certificates.crt

# 安全密码套件（前向安全优先）
smtp_tls_eecdh_grade = strong
smtp_tls_mandatory_ciphers = high
smtp_tls_protocols = !SSLv2, !SSLv3, !TLSv1, !TLSv1.1

# DANE 验证失败后的日志级别
smtp_tls_scert_verifydepth = 5

# 策略重试与缓存
smtp_tls_session_cache_database = btree:/var/lib/postfix/smtp_tls_session_cache
smtp_tls_note_starttls_offer = yes
```

### 4.2 入站（接收方）日志确认

接收方不需要特殊配置——只要启用TLS即可。但建议在main.cf中添加以下调试配置：

```
# /etc/postfix/main.cf — 接收方TLS（对DANE验证无影响但需配合）

smtpd_tls_cert_file = /etc/ssl/certs/mail.example.com.pem
smtpd_tls_key_file = /etc/ssl/private/mail.example.com.key
smtpd_tls_security_level = may
smtpd_tls_mandatory_protocols = !SSLv2, !SSLv3, !TLSv1, !TLSv1.1
smtpd_tls_mandatory_ciphers = high
smtpd_tls_eecdh_grade = strong

# 验证日志
smtpd_tls_received_header = yes
smtpd_tls_loglevel = 1  # 生产环境设为1，调试设为2
```

### 4.3 验证DANE生效（日志分析）

```
# 发送邮件后检查日志
grep "DANE" /var/log/mail.log
# 成功示例：
# postfix/smtp[12345]: Trusted TLS connection established to
#   mail.recipient.com[198.51.100.10]:25: TLSv1.3 with cipher
#   TLS_AES_256_GCM_SHA384 (256/256 bits)
#   (DANE: verified)

# 失败示例：
# warning: TLS library problem: 12345:error:1416F086:
#   SSL routines:tls_process_server_certificate:
#   certificate verify failed:
#   (DANE: certificate does not match TLSA record)

# 统计DANE连接比例
grep "DANE" /var/log/mail.log | wc -l
grep "smtp_tls_security_level = dane" /var/log/mail.log | wc -l
```

## 5. 证书轮换与TLSA同步策略

### 5.1 平滑轮换方案

证书轮换时必须同时更新TLSA记录，否则DANE验证失败。平滑策略：

1. **双TLSA记录法**：在新证书生效前，同时在DNS中保留旧TLSA记录和新TLSA记录。大多数MTA（包括Postfix）支持多条TLSA记录——匹配任何一条即通过
2. **Usage 3 + Selector 1 的优势**：如果使用Selector 1（SPKI），更换证书时如果公钥不变（例如在相同CSR下续期），TLSA记录不需要更新。
3. **TTL协调**：TLSA记录TTL设为5分钟（300s）以上，但证书轮换前至少提前1个TTL周期发布新TLSA

```
# 双TLSA记录示例：旧证书过期前两周同时保留两条记录
_25._tcp.mail.example.com. 300 IN TLSA 3 1 1 (
  ab12cd34ef567890... )  ;; 旧证书SPKI (将在14天后过期)
_25._tcp.mail.example.com. 300 IN TLSA 3 1 1 (
  ef567890ab12cd34... )  ;; 新证书SPKI (立即生效)
```

## 6. 七类常见故障排查

### 6.1 TLSA记录未签名（最常见的误配置）

症状：Postfix日志显示`DANE: TLSA lookup for _25._tcp.mail.example.com resulted in no DNSSEC signatures`。原因：TLSA记录存在于DNS但该区域未启用DNSSEC签名。DANE所有MTA拒绝使用未签名的TLSA记录。使用dig确认TLSA记录是否包含DNSSEC签名标记（RRSIG）：`dig +dnssec TLSA _25._tcp.mail.example.com`。输出中应包含RRSIG记录。

### 6.2 TLSA记录查询失败

症状：`warning: DANE TLSA lookup of _25._tcp.mail.example.com returned SERVFAIL`。原因：DNSSEC验证链断裂——从根区到目标域的任意环节DS记录缺失或签名过期。使用`delv +trace example.com`逐级排查验证链。

### 6.3 证书链不匹配

症状：`Certificate verify failed: (DANE: certificate does not match TLSA record)`。常见原因：TLSA记录生成时使用了错误证书（如使用了CA中间证书而非服务器证书）；或Selector选择错误（Usage 3 + Selector 0要求完整证书而非SPKI）。

### 6.4 MX主机名与TLSA名称不匹配

症状：DANE查询名称错误。RFC 7672要求TLSA记录位置为\_25.\_tcp.MX-TARGET.，即MX记录指向的主机名（而非域名）。如果MX记录指向`mx1.thirdparty.net`，TLSA记录必须位于`_25._tcp.mx1.thirdparty.net`。域所有者无法控制第三方MX的TLSA。

### 6.5 Postfix DNSSEC解析器未配置

症状：Postfix不使用DANE验证或降级为普通TLS。需确保`smtp_dns_support_level = dnssec`且系统resolv.conf指向支持DNSSEC的递归解析器（如8.8.8.8/8.8.4.4、1.1.1.1或自建Unbound）。Postfix的smtp\_tls\_security\_level=dane配置要求smtp\_dns\_support\_level至少为dnssec级别 [4]。

### 6.6 TLS版本不兼容

症状：DANE启用后连接失败但非证书原因。如果接收方MTA不支持TLS（25端口直接明文），启用了DANE的出站Postfix会拒绝发送（视为不安全）。这是RFC 7672的强制行为——DANE策略不允许回退到明文模式。

### 6.7 自签名证书测试环境失败

自签名证书在测试环境中常因系统CA包不包含自签名CA而失败。正确的DANE Usage 3模式不依赖CA链验证——TLSA记录直接约束服务器的证书/公钥，自签名证书只要符合TLSA记录即通过。如果仍失败，检查TLSA记录中的Matching Type是否正确匹配了SPKI或完整证书。

## 参考文献

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/dane-tlsa-smtp-deployment.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
