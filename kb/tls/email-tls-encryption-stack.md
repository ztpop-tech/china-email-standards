---
title: "邮件系统 TLS 加密技术栈深度解析：STARTTLS、MTA-STS、DANE 与 TLS-RPT 全体系"
source: "https://ztpop.net/kb/email-tls-encryption-stack.html"
license: CC-BY 4.0
---

# 邮件系统 TLS 加密技术栈深度解析：STARTTLS、MTA-STS、DANE 与 TLS-RPT 全体系

邮件系统TLS加密技术栈深度解析 — ztpop.net 知识库

  

## 1. 邮件传输 TLS 的核心问题

SMTP 设计于 1982 年（RFC 821），那个年代互联网上不存在窃听威胁。邮件在 MTA 之间以明文传输，任何中间节点都能读取或篡改内容。这个设计缺陷直到今天仍在制造安全事件——全球仍有约 10%~15% 的入站邮件在 SMTP 跳转中经历明文传输。

SMTP STARTTLS（RFC 3207，后由 RFC 7817 更新）试图在不改变协议端口的前提下引入加密：发件 MTA 连接收件 MTA 的 25 端口，发送
`EHLO`
，如果对方宣告
`250-STARTTLS`
，则双方协商升级到 TLS。连接在同一个 25 端口上完成从明文到加密的切换。

**降级攻击（downgrade attack）**
：STARTTLS 是
*机会性加密*
（opportunistic encryption）。中间人只需在 TCP 层面拦截并删除收件方的
`250-STARTTLS`
响应，发件方就会误认为对方不支持 TLS，回退到明文传输。整个过程对双方不可见，没有告警，没有日志差异。

这种攻击在现实中可操作且成本低廉。任何控制网络路径的 adversary（ISP、Wi-Fi 热点、BGP 劫持者）都能实施。STARTTLS 本身不提供任何身份验证——即使 TLS 握手成功，发件方也不会验证收件方证书的域名是否匹配，自签名证书同样被接受。

也就是说，
**STARTTLS 只防被动窃听，不防主动攻击**
。这个 gap 就是 MTA-STS 和 DANE TLSA 要填补的空间。

## 2. MTA-STS：基于 HTTPS 的策略强制执行

MTA-STS（SMTP MTA Strict Transport Security，RFC 8461）的思路与 Web 领域的 HSTS（RFC 6797）一脉相承：域名的所有者通过一个 HTTPS 端点发布 TLS 策略，发件方在发送前拉取策略，强制要求 TLS + 证书验证。策略缓存在发件方本地，天然抵抗降级攻击。

### 2.1 策略发现：两步查询

发件 MTA DNS 收件域 HTTPS
│ │ │
│ ① DNS TXT 查询 \_mta-sts.目标域 │ │
│ ──────────────────────────────> │ │
│ <────────────────────────────── │ │
│ v=STSv1; id=2026070401 │ │
│ │
│ ② GET /.well-known/mta-sts.txt ──────────────────────────────> │
│ <────────────────────────────────────────────────────────────── │
│ version: STSv1 │
│ mode: enforce │
│ mx: mx1.example.com │
│ mx: mx2.example.com │
│ max\_age: 86400 │

**第一步：DNS TXT 记录**

```
;; 查询 _mta-sts 子域
dig +short TXT _mta-sts.example.com
;; 返回：
"v=STSv1; id=2026070401"
```

TXT 记录存在的意义：告诉发件方"这个域发布了 MTA-STS 策略"。记录内容是
`v=STSv1`
和策略版本号
`id`
。发件方会比较本地缓存的 id，如果相同则跳过 HTTPS 拉取，大幅降低请求量。id 字段最大 32 字符，通常用时间戳或递增序号。

**第二步：HTTPS 拉取策略文件**

策略文件托管在
`https://mta-sts.example.com/.well-known/mta-sts.txt`
，注意子域名是
`mta-sts`
，不是主域本身。必须使用 HTTPS，证书必须由受信任 CA 签发。

```
version: STSv1
mode: enforce
mx: mx1.example.com
mx: mx2.example.com
max_age: 86400
```

2.1 策略发现：两步查询

| 字段 | 说明 |
| `version` | 固定为 `STSv1` |
| `mode` | `testing` （仅报告不阻断）或 `enforce` （阻断不合规连接）。生产部署必须从 testing 开始 |
| `mx` | 允许的收件 MX 主机名列表。只有列在这里的 MX 才被策略认可 |
| `max_age` | 策略有效期（秒）。发件方缓存在本地，到期后重新拉取。86400~31536000 |

**策略缓存语义**
：发件方成功拉取策略后，在
`max_age`
内即使收件域删除了 DNS TXT 记录或 HTTPS 端点不可达，已缓存的策略仍然生效。这保证了策略的"粘性"——攻击者无法通过临时性的 DNS/HTTPS 阻断绕过验证。这条规则与 HSTS
`max-age`
的设计一致。
**RFC 8689 补充**
：MTA-STS 策略在
`mode: testing`
下应配合 TLS-RPT 收集失败数据。生产切换前确保一周以上无异常报告。策略文件大小上限 64KB，但实际内容不超过几百字节。

### 2.2 发件方执行逻辑

发件 MTA 在投递邮件前的决策路径：

1. 检查本地是否有目标域的未过期 MTA-STS 策略缓存 → 有则直接应用，跳过联网查询
2. 无缓存 → 查询 DNS TXT
   `_mta-sts.目标域`
   → 无记录则回退到普通 STARTTLS
3. 有 TXT 记录 → 对比本地缓存的 id → 相同则沿用旧策略
4. id 不同 → 通过 HTTPS 拉取
   `/.well-known/mta-sts.txt`
5. 根据策略 mode 决定：enforce 模式下 TLS 协商失败或证书域名不匹配 → 拒绝投递并排入延迟队列；testing 模式下仅记录 TLS-RPT 报告

### 2.3 Nginx 部署 .well-known 端点

```
# /etc/nginx/sites-available/mta-sts.example.com
server {
    listen 443 ssl http2;
    server_name mta-sts.example.com;

    ssl_certificate     /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;

    root /var/www/mta-sts;

    location /.well-known/mta-sts.txt {
        default_type text/plain;
    }
}
```

策略文件内容放入
`/var/www/mta-sts/.well-known/mta-sts.txt`
：

```
version: STSv1
mode: testing
mx: mx1.example.com
mx: mx2.example.com
max_age: 86400
```

验证端点可访问性：

```
curl -sI https://mta-sts.example.com/.well-known/mta-sts.txt
# HTTP/2 200
# content-type: text/plain
```

## 3. DANE TLSA：基于 DNSSEC 的证书锁定

DANE（DNS-Based Authentication of Named Entities，RFC 6698）在 SMTP 场景下的应用由 RFC 7672 定义。核心思想：用 DNSSEC 签名的 TLSA 记录告诉发件方"连接我的 MX 服务器时，只能接受这个特定证书（或 CA）"。

MTA-STS 的信任锚是 CA 体系（HTTPS 的 PKI）；DANE 的信任锚是 DNSSEC 签名链（DNS 本身的信任根）。两者的信任模型完全不同。

### 3.1 TLSA 记录结构

```
_25._tcp.mx1.example.com.  IN  TLSA  3 1 1  (
      e3b0c44298fc1c149afbf4c8996fb924
      27ae41e4649b934ca495991b7852b855 )
```

3.1 TLSA 记录结构

| 字段 | 值 | 含义 |
| 端口 | `_25` | SMTP with STARTTLS 使用 25 端口 |
| 协议 | `_tcp` | TCP |
| Usage | `3` | DANE-EE：锁定具体证书（最严格） |
| Selector | `1` | SPKI：取 SubjectPublicKeyInfo 的 hash |
| Matching Type | `1` | SHA-256 |

3.1 TLSA 记录结构

| Usage | 名称 | 场景 | 信任锚 |
| `0` | PKIX-TA | CA 公钥锁定（不推荐 SMTP 用） | PKIX + DNSSEC |
| `1` | PKIX-EE | 服务证书锁定 + CA 验证 | PKIX + DNSSEC |
| `2` | DANE-TA | 私有 CA 公钥锁定，跳过公共 PKI | 仅 DNSSEC |
| **3** | **DANE-EE** | **服务证书直接锁定，完全跳过 CA** | **仅 DNSSEC** |

**Usage 2 vs Usage 3 的部署区别**
：Usage 3（DANE-EE）锁定的是服务器证书本身的 hash。证书轮换时必须同时更新 TLSA 记录，管理成本高，但安全性最强——即使 CA 被入侵签发伪造证书，攻击者也无法冒充你的 MX。Usage 2（DANE-TA）锁定的是签发 CA 的公钥，允许该 CA 签发的新证书自动生效，适合内部 PKI 场景。
**DNSSEC 是 DANE 的前提条件**
：如果收件域没有部署 DNSSEC，发件方无法验证 TLSA 记录的完整性。此时 DANE 退化为不安全状态（RFC 7672 第 5 节：发件方 MUST NOT 在未验证 DNSSEC 的情况下信任 TLSA）。部署 DANE 的第一步永远是 DNSSEC 签名。

### 3.2 生成 TLSA 记录

从现有证书生成 Usage 3 / Selector 1 / Matching 1 的 TLSA 记录：

```
# 获取 MX 服务器当前证书的 SPKI hash
openssl s_client -starttls smtp -connect mx1.example.com:25 \
    -servername mx1.example.com /dev/null \
  | openssl x509 -noout -pubkey \
  | openssl pkey -pubin -outform DER \
  | openssl sha256

# 输出：
# SHA256(stdin)= e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855

# 转为 TLSA 格式 (Usage=3, Selector=1, Matching=1)
# 记录: 3 1 1 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

在线验证工具（DNSViz 或 dane.sys4.de）可以确认 TLSA 记录是否与服务器证书匹配、DNSSEC 链是否完整。

### 3.3 Postfix DANE 配置

发件侧 Postfix 启用 DANE 验证（需要 Postfix ≥ 2.11 且编译时启用 DNSSEC）：

```
# /etc/postfix/main.cf

# 启用 DANE
smtp_tls_security_level = dane
smtp_dns_support_level = dnssec

# 仅对支持 DNSSEC 的域启用 DANE，其他回退到普通 STARTTLS
# (Postfix 3.0+)
smtp_tls_security_level = may
smtp_tls_policy_maps = hash:/etc/postfix/tls_policy

# 强制启用 DANE 的域列表 (可选，覆盖默认策略)
# /etc/postfix/tls_policy:
#   example.com  dane
#   example.org  dane

smtp_host_lookup = dns
# 确保可以解析 TLSA 记录

# TLS 日志
smtp_tls_loglevel = 1
```

收件侧（接受入站邮件的 MX 服务器），Postfix TLS 配置：

```
# /etc/postfix/main.cf

# 入站 STARTTLS
smtpd_tls_security_level = may
smtpd_tls_cert_file = /etc/letsencrypt/live/mx1.example.com/fullchain.pem
smtpd_tls_key_file  = /etc/letsencrypt/live/mx1.example.com/privkey.pem

# 密码套件：仅 TLS 1.2+
smtpd_tls_mandatory_protocols = !SSLv2, !SSLv3, !TLSv1, !TLSv1.1
smtpd_tls_protocols           = !SSLv2, !SSLv3, !TLSv1, !TLSv1.1

# 强密码套件（参考 NIST SP 800-52 Rev.2）
smtpd_tls_mandatory_ciphers = high
smtpd_tls_eecdh_grade = strong

# 日志
smtpd_tls_loglevel = 1
```

## 4. 三种机制的信任模型对比

4. 三种机制的信任模型对比

| 维度 | STARTTLS (RFC 3207/7817) | MTA-STS (RFC 8461) | DANE TLSA (RFC 7672) |
| 加密方式 | 机会性 TLS | 强制 TLS + 证书验证 | 强制 TLS + 证书/DNSSEC 锁定 |
| 信任锚 | 无（不验证证书） | CA 体系（HTTPS PKI） | DNSSEC 签名链 |
| 策略发布 | 无 | HTTPS (mta-sts.txt) | DNS (TLSA 记录) |
| 策略发现 | 无 | DNS TXT + HTTPS 拉取 | DNS 查询（TLSA RR） |
| 抗降级攻击 | ❌ 可被中间人剥离 STARTTLS 声明 | ✅ 策略缓存 + 强制验证 | ✅ DNSSEC 保证记录完整性 |
| 抗 DNS 欺骗 | ❌ | 部分（HTTPS 提供完整性） | ✅（DNSSEC 保证） |
| 抗 CA 劫持 | 不适用 | ❌（依赖 CA 体系） | ✅（Usage 3 完全跳过 CA） |
| 部署复杂度 | 零配置 | 中等（HTTPS + DNS TXT） | 较高（需要 DNSSEC + TLSA） |
| 运维成本 | 零 | 低（证书自动续期即可） | 中（证书轮换需同步 TLSA） |
| 覆盖范围 | 所有 TLS 支持的 SMTP | 主动发布策略的域 | 部署 DNSSEC 且发布 TLSA 的域 |

**三者不互斥，应叠加部署**
。DANE 提供最强的证书绑定（跳过 CA 信任链），MTA-STS 覆盖未部署 DNSSEC 但至少发布了 HTTPS 策略的域，STARTTLS 做 baseline。实际部署顺序：STARTTLS → MTA-STS testing → MTA-STS enforce → DNSSEC → DANE。每步观察 TLS-RPT 确认无误后再进入下一步。

## 5. TLS-RPT：加密部署的监控与反馈

TLS-RPT（SMTP TLS Reporting，RFC 8460）定义了一套 JSON 格式的聚合报告机制，功能定位类似于 DMARC 的聚合报告（
`rua`
）：收件域可以要求发件方把 TLS 连接的成功/失败统计通过邮件发回指定地址。

### 5.1 DNS 记录

```
_smtp._tls.example.com.  IN  TXT  "v=TLSRPTv1; rua=mailto:tls-reports@example.com"
```

5.1 DNS 记录

| 标签 | 含义 |
| `v=TLSRPTv1` | 协议版本 |
| `rua` | 聚合报告接收地址。多个地址逗号分隔，支持 `mailto:` 和 `https:` 两种 scheme（HTTPS 由 RFC 8460 第 3.2 节定义，但实际部署以 mailto 为主） |

### 5.2 报告格式

```
{
  "organization-name": "SenderOrg",
  "date-range": {
    "start-datetime": "2026-07-03T00:00:00Z",
    "end-datetime": "2026-07-04T00:00:00Z"
  },
  "contact-info": "postmaster@sender.example",
  "report-id": "2026-07-04T00:00:00Z_sender.example",
  "policies": [
    {
      "policy": {
        "policy-type": "sts",
        "policy-string": [
          "version: STSv1",
          "mode: enforce",
          "mx: mx1.example.com",
          "mx: mx2.example.com",
          "max_age: 86400"
        ],
        "policy-domain": "example.com"
      },
      "summary": {
        "total-successful-session-count": 1423,
        "total-failure-session-count": 7
      },
      "failure-details": [
        {
          "result-type": "certificate-expired",
          "sending-mta-ip": "203.0.113.45",
          "receiving-mx-hostname": "mx1.example.com",
          "receiving-mx-helo": "mx1.example.com",
          "failed-session-count": 3
        },
        {
          "result-type": "starttls-not-supported",
          "sending-mta-ip": "203.0.113.50",
          "receiving-mx-hostname": "mx2.example.com",
          "failed-session-count": 4
        }
      ]
    }
  ]
}
```

5.2 报告格式

| `result-type` | 含义 |
| `starttls-not-supported` | 收件方不支持 STARTTLS |
| `certificate-host-mismatch` | 证书 CN/SAN 不匹配 MX 主机名 |
| `certificate-expired` | 证书过期 |
| `certificate-not-trusted` | 证书链无法验证 |
| `validation-failure` | DANE 验证失败（TLSA 不匹配） |
| `sts-policy-invalid` | MTA-STS 策略格式错误 |
| `sts-policy-fetch-error` | 无法拉取 MTA-STS 策略 |

MTA-STS 的
`mode: testing`
必须配合 TLS-RPT 使用。testing 下连接失败只记报告不阻断投递，如果跳过这一阶段直接切 enforce，可能因为证书配置错误导致大量邮件被拒。建议 testing 观察至少 7 天，确认失败数趋近于零后再切换。

## 6. TLS 1.3 在 SMTP 中的部署考量

TLS 1.3（RFC 8446）相比 TLS 1.2 的核心变化：握手从 2-RTT 缩减到 1-RTT（ECDHE 密钥交换），废弃所有非 AEAD 密码套件和 RSA 密钥交换，0-RTT 模式下甚至可以零往返恢复会话。

### 6.1 0-RTT 与 SMTP 的重放风险

0-RTT（Early Data）在 HTTPS 场景下存在重放攻击面：攻击者捕获 0-RTT 包后重放到服务器，如果应用层不做幂等性保护，可能导致重复操作。在 SMTP 中这个风险更加棘手——
**重复投递一封邮件**
意味着收件人收到两份相同内容。

**Postfix 当前对 0-RTT 的处理**
：Postfix 3.7+ 在配置
`tls_ssl_options = NO_ANTI_REPLAY`
之前默认禁用 0-RTT。即使启用，SMTP 协议本身不具备内在的 0-RTT 重放保护。如果收件 MTA 接受 0-RTT 并在
`DATA`
阶段完成前断开，发件方会重试——此时同一封邮件可能被投递两次。在 SMTP 场景下
**建议始终禁用 0-RTT**
。

### 6.2 AEAD 密码套件

TLS 1.3 仅保留 5 个密码套件，全部基于 AEAD（Authenticated Encryption with Associated Data）：

6.2 AEAD 密码套件

| 密码套件 | 密钥交换 | 认证 | 加密 | Hash |
| TLS\_AES\_128\_GCM\_SHA256 | ECDHE | RSA/ECDSA | AES-128-GCM | SHA-256 |
| TLS\_AES\_256\_GCM\_SHA384 | ECDHE | RSA/ECDSA | AES-256-GCM | SHA-384 |
| TLS\_CHACHA20\_POLY1305\_SHA256 | ECDHE | RSA/ECDSA | ChaCha20-Poly1305 | SHA-256 |
| TLS\_AES\_128\_CCM\_SHA256 | ECDHE | RSA/ECDSA | AES-128-CCM | SHA-256 |
| TLS\_AES\_128\_CCM\_8\_SHA256 | ECDHE | RSA/ECDSA | AES-128-CCM-8 | SHA-256 |

Postfix 中的 TLS 1.3 密码套件配置：

```
# /etc/postfix/main.cf
# 限制 TLS 版本
smtpd_tls_mandatory_protocols = !SSLv2, !SSLv3, !TLSv1, !TLSv1.1
smtp_tls_mandatory_protocols  = !SSLv2, !SSLv3, !TLSv1, !TLSv1.1

# TLS 1.3 密码套件优先级（服务端）
# 参考 NIST SP 800-52 Rev.2 推荐
tls_preempt_cipherlist = yes
smtpd_tls_mandatory_ciphers = high
smtpd_tls_ciphers = high

# 显式 OpenSSL 密码字符串 (Postfix 3.6+)
smtp_tls_ciphers = high
smtpd_tls_ciphers = high

# 禁用 0-RTT
tls_ssl_options = NO_TICKET
```

**NIST SP 800-52 Rev.2**
将 TLS 1.2 标记为可接受但逐步淘汰（部分密码套件已不推荐），TLS 1.3 为当前推荐版本。对 SMTP 而言，最低安全基线应该是：禁止 TLS 1.0/1.1、禁止 SSLv2/v3、仅允许支持 PFS（Perfect Forward Secrecy）的密码套件。SMTP 场景不涉及浏览器兼容性负担，淘汰旧协议版本的速度可以比 HTTPS 更快。

## 7. 诊断与验证命令集

### 7.1 STARTTLS 握手诊断

```
# 基础 TLS 握手
openssl s_client -starttls smtp -connect mx1.example.com:25 \
    -servername mx1.example.com

# 显示证书详情
openssl s_client -starttls smtp -connect mx1.example.com:25 \
    -servername mx1.example.com /dev/null \
  | openssl x509 -noout -text

# 验证证书链
openssl s_client -starttls smtp -connect mx1.example.com:25 \
    -servername mx1.example.com -verify 9 -verify_return_error

# 指定 TLS 版本测试 (测试服务器是否支持低版本)
openssl s_client -starttls smtp -connect mx1.example.com:25 \
    -tls1_2 -servername mx1.example.com

# 检查是否支持旧版本 (预期应该失败)
openssl s_client -starttls smtp -connect mx1.example.com:25 \
    -tls1 -servername mx1.example.com
# 如果成功握手 → 说明服务器仍允许 TLS 1.0，需要加固
```

### 7.2 MTA-STS 验证

```
# 1. 检查 DNS TXT 记录
dig +short TXT _mta-sts.example.com
# 预期: "v=STSv1; id=2026070401"

# 2. 检查策略文件
curl -s https://mta-sts.example.com/.well-known/mta-sts.txt

# 3. 检查 HTTPS 证书
curl -sIv https://mta-sts.example.com/.well-known/mta-sts.txt 2>&1 \
  | grep -E "subject:|issuer:|expire date:|SSL certificate verify"

# 4. 验证证书链（模拟发件方）
openssl s_client -connect mta-sts.example.com:443 \
    -servername mta-sts.example.com -verify 9
```

### 7.3 DANE / DNSSEC 验证

```
# 检查域名的 DNSSEC 状态
dig +dnssec +short SOA example.com
# 有 RRSIG 记录表示已签名

# 查询 TLSA 记录
dig +short TLSA _25._tcp.mx1.example.com
# 预期: 3 1 1 e3b0c...

# 验证 DNSSEC 验证链
dig +dnssec +multi TLSA _25._tcp.mx1.example.com
# 检查 AD (Authenticated Data) 标志

# 使用 delv 验证（更严格）
delv TLSA _25._tcp.mx1.example.com
# fully validated 表示 DNSSEC 链完整
```

### 7.4 TLS-RPT 接收端部署

```
# 检查 TLS-RPT DNS 记录
dig +short TXT _smtp._tls.example.com
# 预期: "v=TLSRPTv1; rua=mailto:tls-reports@example.com"

# 检查接收地址可达性
swaks --to tls-reports@example.com --server localhost
```

## 8. 部署检查清单

8. 部署检查清单

| 阶段 | 操作 | 验证方式 |
| 0. 基线 | 确认 STARTTLS 可用，证书未过期 | `openssl s_client -starttls smtp -connect mx:25` |
| 1. TLS 加固 | 禁用 TLS 1.0/1.1，仅允许 TLS 1.2+ | `-tls1` 握手应失败 |
| 2. 证书 | 使用受信任 CA 签发的证书，SAN 包含 MX 主机名 | 浏览器访问 HTTPS 不报警 |
| 3. MTA-STS DNS | 添加 `_mta-sts` TXT 记录 | `dig TXT _mta-sts.域` |
| 4. MTA-STS HTTPS | 部署 `mta-sts.域/.well-known/mta-sts.txt` | `curl` 返回 200 |
| 5. MTA-STS policy | mode: testing, 配置正确的 mx 列表 | 内容检查 + 格式校验 |
| 6. TLS-RPT | 添加 `_smtp._tls` TXT 记录 | `dig TXT _smtp._tls.域` |
| 7. 观察期 | 至少 7 天 testing 期，检查 TLS-RPT 报告 | 0 异常后切换 enforce |
| 8. MTA-STS enforce | mode 改为 enforce，更新 id | 发件方日志确认 enforce 生效 |
| 9. DNSSEC | 在域名注册商/NS 启用 DNSSEC 签名 | `dig +dnssec SOA` 有 RRSIG |
| 10. DANE | 发布 TLSA 记录，发件侧启用 DANE | `dig TLSA _25._tcp.mx` |

## 9. 技术栈层次总览

Layer 4 — 监控与反馈
└── TLS-RPT (RFC 8460) ← JSON 聚合报告，类似 DMARC rua
Layer 3 — 策略强制执行
├── MTA-STS (RFC 8461) ← HTTPS 发布策略，CA 信任锚
└── DANE TLSA (RFC 7672) ← DNSSEC 发布证书锁定，DNS 信任锚
Layer 2 — 传输加密
└── STARTTLS (RFC 3207/7817) ← 机会性 TLS，不验证证书
Layer 1 — 协议安全基线
└── TLS 1.3 (RFC 8446) ← 强制 AEAD，禁止旧版本
参考标准:
NIST SP 800-52 Rev.2 ← TLS 部署指南
RFC 8689 ← MTA-STS 补充与最佳实践

邮件传输加密的实现路径明确：先让 TLS 本身安全（禁用旧协议、限制密码套件），再加策略层（MTA-STS 或 DANE），最后通过 TLS-RPT 建立监控闭环。单靠 STARTTLS 在今天的安全威胁模型下远远不够——如果 TLS 是在中间人注视下协商出来的，那就等于没加密。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-tls-encryption-stack.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
