---
title: "TLS 1.3 STARTTLS 协议流程详细分析 — RFC 8446 与 RFC 3207 握手序列及部署实践"
source: "https://ztpop.net/kb/tls13-starttls-protocol.html"
license: CC-BY 4.0
---

# TLS 1.3 STARTTLS 协议流程详细分析 — RFC 8446 与 RFC 3207 握手序列及部署实践

## 1. STARTTLS 协议基础：RFC 3207 的行为模型

RFC 3207（2015 年由 RFC 7817 更新）定义了一种在 SMTP 会话内部升级至 TLS 加密通道的机制，称为 STARTTLS [1]。它的核心设计约束是：不改变端口号，通过在明文会话中发送一条命令触发加密升级。

协议序列的上半段始终是明文的：

```
C: EHLO example.com
S: 250-mx.example.com Hello
S: 250-STARTTLS
S: 250-SIZE 52428800
S: 250-PIPELINING
S: 250-CHUNKING
S: 250 8BITMIME
C: STARTTLS
S: 220 Ready to start TLS
C: [TLS 握手开始]
```

收到 220 回复后，两端立即丢弃明文解析，直接开始在现有 TCP 连接上执行 TLS 握手。TLS 1.2 使用的标准握手分为两步：ClientHello → ServerHello + Certificate + ServerHelloDone → ClientKeyExchange + ChangeCipherSpec + Finished → ServerCCS + Finished。这个过程需要两次网络往返（2-RTT）。

RFC 7817 对 RFC 3207 的主要更新是要求客户端在 EHLO 回复中收到 STARTTLS 关键字后才能发出 STARTTLS 命令，并澄清了 TLS 协商失败时的回退要求：必须发送 454 4.7.0 错误码并关闭连接，不得降级到明文传输同一封邮件 [1]。

## 2. TLS 1.3 握手架构：RFC 8446 的核心变更

### 2.1 1-RTT 全握手

TLS 1.3 设计上最大的结构性变化是移除了 TLS 1.2 的对称协商模式，采用基于 (EC)DHE 的一次性握手 [2]。ClientHello 中直接携带客户端支持的 key\_share（DH 公钥），ServerHello 回复中即携带服务器选择的 key\_share 和证书链。握手的完整序列如下：

```
C: ClientHello
   (supported_versions=1.3, key_share=client_kex, signature_algorithms=ed25519|rsa_pss_rsae)
S: ServerHello
   (supported_versions=1.3, key_share=server_kex, cipher_suite=TLS_AES_256_GCM_SHA384)
S: EncryptedExtensions
S: Certificate
S: CertificateVerify
S: Finished
C: Finished
[加密数据传输开始]
```

与 TLS 1.2 的 2-RTT 相比，TLS 1.3 将 ServerHello、Certificate、CertificateVerify 和 Finished 全部压缩在服务器单次响应中发送，客户端只需一个回复（Finished）即可开始加密传输。这种 1-RTT 结构在 SMTP 场景中尤其受益——一个典型的 MX 到 MX 投递流程通常只有一条邮件需要传输，减少一次往返意味着每封邮件的投递延迟降低了大约 50-100ms（取决于 RTT）。

### 2.2 Cipher Suite 精简与降级防护

TLS 1.3 仅保留五个 AEAD 套件，移除了 TLS 1.2 中的 CBC 模式、RC4、3DES 和静态 RSA 密钥交换 [2]：

表1：TLS 1.3 强制/推荐密码套件

| 套件 | 认证/KEM | AEAD | 要求 |
| TLS\_AES\_128\_GCM\_SHA256 | ECDHE/RSA | AES-128-GCM | MUST |
| TLS\_AES\_256\_GCM\_SHA384 | ECDHE/RSA | AES-256-GCM | SHOULD |
| TLS\_CHACHA20\_POLY1305\_SHA256 | ECDHE/RSA | ChaCha20-Poly1305 | SHOULD |
| TLS\_AES\_128\_CCM\_SHA256 | ECDHE/RSA | AES-128-CCM | SHOULD |
| TLS\_AES\_128\_CCM\_8\_SHA256 | ECDHE/RSA | AES-128-CCM-8 | OPTIONAL |

TLS 1.3 的降级防护机制是协议层面的：服务器在 ServerHello 的 Random 字段中嵌入了一个降级魔法字节（downgrade sentinel）。如果客户端发送的 supported\_versions 包含 1.3，但服务器回复了一个 TLS ≤1.2 的 ServerHello 且该字段包含降级标识，客户端必须终止连接 [2, §4.1.3]。这从协议层面杜绝了攻击者通过修改 ClientHello 迫使服务器使用低版本 TLS 的可能性——在 STARTTLS 的 STRIPTLS 攻击场景中，这是关键防御。

## 3. STARTTLS 内的 TLS 1.3 握手序列

### 3.1 完整交互字节流

以下是一段真实的 SMTP STARTTLS + TLS 1.3 完整握手的 wireshark 级分步解析。假定发送方 MTA（192.0.2.1:34567）连接接收方 MX（192.0.2.2:25）：

```
Step 1: TCP 三次握手
Step 2: SMTP 明文协商
  C -> S: EHLO sending.example.com
  S -> C: 250-mx.example.com Hello
           250-STARTTLS
           250-PIPELINING
           250-SIZE 52428800
           250 8BITMIME
  C -> S: STARTTLS
  S -> C: 220 Ready to start TLS

Step 3: TLS 1.3 单次握手（1-RTT）
  C -> S: ClientHello
           Protocol: TLS 1.3 (supported_versions extension)
           Key Share: secp256r1 (x25519) 客户端临时公钥
           Signature Algorithms: rsa_pss_rsae_sha256, ed25519
           cipher_suites: TLS_AES_256_GCM_SHA384, TLS_AES_128_GCM_SHA256,
                          TLS_CHACHA20_POLY1305_SHA256
  S -> C: ServerHello
           Protocol: TLS 1.3 (从 supported_versions 选中)
           Key Share: 服务器临时公钥
           cipher_suite: TLS_AES_256_GCM_SHA384
           Random: [含 TLS 1.3 降级标识指示]
  S -> C: {EncryptedExtensions}
  S -> C: {Certificate}
           - 服务器证书（CN=mx.example.com）
           - 中间 CA 证书链
  S -> C: {CertificateVerify}
           - 签名算法: rsa_pss_rsae_sha256
  S -> C: {Finished}
  C -> S: {Finished}

Step 4: 加密 SMTP 会话
  C -> S: EHLO sending.example.com [TLS 保护]
  S -> C: 250-mx.example.com Hello [TLS 保护]
  MAIL FROM:
  ...
```

其中 `{}` 表示 EncryptedExtensions 之后的所有消息都由握手密钥加密保护，但对端尚未完成身份验证。

### 3.2 与 TLS 1.2 的差异对比

表2：STARTTLS 下 TLS 1.2 vs TLS 1.3 握手差异

| 维度 | TLS 1.2 (RFC 5246) | TLS 1.3 (RFC 8446) |
| RTT | 2-RTT（ClientHello→ServerHello→CCS→Finished 两个完整往返） | 1-RTT（所有服务器消息一次发送） |
| ChangeCipherSpec | 显式发送，每条消息后切换加密 | 隐式，由握手状态机自动管理 |
| 密码套件数量 | 官方定义 30+，实际实现支持数百种 | 严格限制 5 种，仅 AEAD |
| 密钥交换 | 可选静态 RSA 或 DHE/ECDHE（由密码套件决定） | 强制 (EC)DHE，每次握手独立 |
| 证书请求时机 | ServerHello 后服务器主动发送 | CertificateRequest 为独立消息，可在 EncryptedExtensions 之后分批发 |
| 降级检测 | 无协议级机制，依赖客户端逻辑 | ServerHello.Random 内嵌降级标识 |

## 4. 0-RTT 与 SMTP 互操作的合规风险

TLS 1.3 引入了 0-RTT 模式（RFC 8446 §2.3），允许在之前建立过会话的客户端直接发送加密数据——用户数据和 Finished 在同一个 TCP 段中发出 [2]。这在 SMTP 场景中理论上极具吸引力：如果 MTA 维护了到目标 MX 的会话缓存，可以在 0-RTT 下直接把 EHLO + MAIL FROM + RCPT TO + DATA 全部发出，零额外往返。

但是，0-RTT 存在不可忽视的重放攻击风险 [2, §8]。攻击者截获 0-RTT 数据段后，可以在不了解会话密钥的情况下将其重放到服务器的另一个实例。在 SMTP 场景中，这意味着攻击者可以复制一条邮件投递请求，导致收件箱出现重复邮件。RFC 8446 明确要求应用层提供重放防护——在 SMTP 协议中，邮件去重通常由 Message-ID 和接收 MTA 的去重逻辑负责，但这并非所有实现都可靠。

生产邮件服务器的建议是：**在 STARTTLS 场景中默认禁用 0-RTT**，或仅在出站队列中启用到高度可信目标 MTA（且该 MTA 本身有去重机制的）缓存会话。Postfix 中可通过 `tls_ssl_options = NO_0RTT` 强制禁用。

## 5. Postfix 部署配置

### 5.1 SMTP 服务端（入站 STARTTLS）

```
# /etc/postfix/main.cf
smtpd_tls_security_level = may                  # 机会加密
smtpd_tls_protocols = !SSLv2, !SSLv3, !TLSv1, !TLSv1.1, TLSv1.2, TLSv1.3
smtpd_tls_mandatory_protocols = !SSLv2, !SSLv3, !TLSv1, !TLSv1.1, TLSv1.2, TLSv1.3
smtpd_tls_ciphers = medium
smtpd_tls_mandatory_ciphers = medium
tls_preempt_cipherlist = yes
smtpd_tls_eecdh_grade = auto

# 显式禁用 0-RTT
tls_ssl_options = NO_0RTT

# 禁用不安全的 TLS 1.2 密码套件
smtpd_tls_mandatory_exclude_ciphers = aNULL, eNULL, EXPORT, DES, RC4, MD5, PSK, DHE-DSS
smtpd_tls_exclude_ciphers = aNULL, eNULL, EXPORT, DES, RC4, MD5, PSK, DHE-DSS
```

### 5.2 SMTP 客户端（出站 STARTTLS）

```
# /etc/postfix/main.cf
smtp_tls_security_level = may
smtp_tls_protocols = !SSLv2, !SSLv3, !TLSv1, !TLSv1.1, TLSv1.2, TLSv1.3
smtp_tls_mandatory_protocols = !SSLv2, !SSLv3, !TLSv1, !TLSv1.1, TLSv1.2, TLSv1.3
smtp_tls_ciphers = medium
smtp_tls_mandatory_ciphers = medium
smtp_tls_eecdh_grade = auto
tls_ssl_options = NO_0RTT

# DANE TLSA 要求至少 TLS 1.2
smtp_tls_security_level = dane
smtp_tls_mandatory_protocols = !SSLv2, !SSLv3, !TLSv1, !TLSv1.1, TLSv1.2, TLSv1.3

# 当 MTA-STS enforce 时
smtp_tls_security_level = verify
smtp_tls_CAfile = /etc/ssl/certs/ca-certificates.crt
```

### 5.3 验证 TLS 1.3 已启用

使用 openssl s\_client 手动测试：

```
$ openssl s_client -starttls smtp -connect mx.example.com:25 \
    -tls1_3 -servername mx.example.com 2>&1 | grep -E "TLS|Cipher|Protocol"
New, TLSv1.3, Cipher is TLS_AES_256_GCM_SHA384
Server public key is 256 bit
```

使用 qshape 观察延迟队列趋势，排除 TLS 1.3 兼容性问题导致的 defer：

```
$ qshape deferred | head -20
```

如果发现特定域出现大量延迟，检查 TLS 版本协商：

```
$ postconf | grep tls_protocols
smtp_tls_protocols = !SSLv2, !SSLv3, !TLSv1, !TLSv1.1, TLSv1.2, TLSv1.3
```

## 6. 部署注意事项

### 6.1 老旧 MTA 兼容性

截至 2026 年，仍有大量中小型邮件系统运行在 TLS ≤1.2 只读模式上。如果出站队列中大量邮件延迟，可考虑暂时在出站端允许 TLS 1.2 作为备选——TLS 1.3 本身就是向下兼容的（通过 supported\_versions 扩展），现代 MTA 会回退到 TLS 1.2。Postfix 的配置支持按域覆盖：

```
# 针对已知兼容性问题的域降级
/etc/postfix/transport:
example.org    smtp:[mx.example.org]:25:protocol=TLSv1.2
```

### 6.2 SNI 支持

TLS 1.3 的 ClientHello 中包含 SNI（Server Name Indication）扩展，支持在同一 IP 上托管多个证书的 MX。SMTP 场景中，某些老旧的 MTA 在 TLS 1.2 下可能不发送 SNI，但 TLS 1.3 的几乎所有主流实现（OpenSSL 1.1.1+、BoringSSL、LibreSSL 3.0+）都默认携带 SNI。接收端如果有大量虚拟主机，务必确保 SNI 证书匹配逻辑正确处理 SMTP 的 hostname（MX 记录的 A/AAAA 名称）。

### 6.3 证书链长度与握手延迟

TLS 1.3 虽然将握手压缩到 1-RTT，但 Certificate 消息的传输时间并未压缩——如果证书链过长（常见问题：服务器证书 + 4〜5 级中间 CA），Certificate 消息本身可能超过 10KB，在低带宽链路上反而导致比 TLS 1.2 更长的实际延迟。建议定期检查证书链长度：

```
$ openssl s_client -starttls smtp -connect mx.example.com:25 -tls1_3 \
    /dev/null | openssl x509 -text | grep "CA Issuers" | wc -l
```

理想的链长不应超过 3（服务器证书 + 2 级中间 CA）。

## 7. 安全降级路径

对于一个完整的邮件传输安全栈，建议按以下优先级顺序尝试：

1. **DANE TLSA** (DNSSEC 证书绑定) — 启用后跳过 1-2，直接要求 TLS 1.3 且证书通过 TLSA 验证
2. **MTA-STS enforce** — 要求 TLS 1.3 且证书经 CA 链验证
3. **MTA-STS testing** — 优先 TLS 1.3，允许降级到 TLS 1.2
4. **机会加密 STARTTLS** — 尝试 TLS 1.3，不成功则 TLS 1.2
5. **明文（已废弃）** — 仅限邮件列表和测试环境

如果 DANE 或 MTA-STS 策略不可用，TLS 1.3 的下一个合理降级目标是 TLS 1.2，而非更低版本。TLS 1.0/1.1 已由 RFC 8996 正式标记为禁止使用 [3]。

## 参考文献

1. IETF RFC 3207 (2002) / RFC 7817 (2016) — SMTP Service Extension for Secure SMTP over Transport Layer Security (STARTTLS)
2. IETF RFC 8446 (2018) — The Transport Layer Security (TLS) Protocol Version 1.3
3. IETF RFC 8996 (2021) — Deprecating TLS 1.0 and TLS 1.1
4. IETF RFC 5246 (2008) — The Transport Layer Security (TLS) Protocol Version 1.2
5. IETF RFC 8314 (2018) — Cleartext Considered Obsolete: Use of TLS for Email Submission and Access
6. Postfix Documentation — TLS\_README, <https://www.postfix.org/TLS_README.html>

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/tls13-starttls-protocol.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
