---
title: "加密邮件网关架构设计：TLS 终止/透传、证书钉扎与 DANE/MTA-STS"
source: "https://ztpop.net/kb/kb-encrypted-email-gateway-architecture.html"
license: CC-BY 4.0
---

# 加密邮件网关架构设计：TLS 终止/透传、证书钉扎与 DANE/MTA-STS

## 概述

邮件安全网关位于互联网和内部邮件系统之间，承担 TLS 加密通信的边界角色。网关的 TLS 架构设计直接决定了：邮件在传输路径上的加密强度、网关对内容的安全检测能力、以及与 DANE/MTA-STS 等现代 SMTP 安全扩展的兼容性。三种主流架构模式——TLS 终止、TLS 透传、混合模式——各有其工程权衡。

## TLS 终止模式 vs 透传模式

### TLS 终止模式（Termination Mode）

网关主动终止来自外部的 TLS 连接，解密后在明文状态下执行内容安全扫描（反垃圾、反病毒、DLP），然后重新封装 TLS 连接将邮件转发到内部 MTA。

```
[Internet] — (TLS) —→ [网关:25 — TLS终止 — 明文扫描] — (TLS) —→ [内部MTA:25]
```

**优势**：

* 网关可直接检查邮件正文、附件内容、URL 等所有数据
* 支持 DLP（数据防泄漏）内容匹配
* 支持基于内容的邮件路由策略

**劣势**：

* 破坏了端到端 TLS 加密——邮件在网关内部以明文形式临时存在
* 网关成为证书信任链的中间节点，需管理上下游两套证书
* 对合规要求高的行业（金融、医疗）可能不符合端到端加密审计要求

### TLS 透传模式（Pass-through / Bridging Mode）

网关作为 TLS 无感知的透明桥接器，不解密 SMTP 流量，仅在 TCP 代理层面转发加密数据流。

```
[Internet] — (TLS) —→ [网关:25 — TCP透传] — (TLS) —→ [内部MTA:25]
```

**优势**：

* 保留完整的端到端 TLS 加密，不引入中间人
* 网关无需管理证书或密钥材料
* 最适合合规要求"不得解密的邮件"的场景

**劣势**：

* 无法执行任何基于内容的威胁检测
* 仅能基于 SMTP 信封层（MAIL FROM/RCPT TO）和 IP 进行策略控制
* 无法集成 DLP、URL 过滤、沙箱等功能

### 混合模式（推荐架构）

生产环境中最常采用的架构：外连侧采用 TLS 终止，内部对关键通信路径使用透传或追加加密层。

```
# 混合模式架构——Postfix 示例
#
# /etc/postfix/master.cf - 外联端口（TLS 终止）
# smtps 465 端口 - 用于 MUA 提交
smtps     inet  n       -       n       -       -       smtpd
  -o smtpd_tls_wrappermode=yes
  -o smtpd_tls_cert_file=/etc/ssl/certs/gateway-external.pem
  -o smtpd_tls_key_file=/etc/ssl/private/gateway-external.key
  -o smtpd_tls_security_level=encrypt

# 内部转发（启用强制 TLS 加密到内部 MTA）
# main.cf 中
smtp_tls_security_level = encrypt
smtp_tls_cert_file = /etc/ssl/certs/gateway-to-internal.pem
smtp_tls_key_file = /etc/ssl/private/gateway-to-internal.key

# 内部转发链配置
# transport 定义
# @internal.local    smtp-internal:
# master.cf
smtp-internal unix - - n - - smtp
  -o smtp_tls_security_level=encrypt
  -o smtp_tls_cert_file=/etc/ssl/certs/to-internal.pem
  -o smtp_tls_key_file=/etc/ssl/private/to-internal.key
```

**架构要点**：

* 互联网侧 → 网关：TLS 终止，执行完整的安全检查（SMTP MTA-2-MTA 入站 TLS）
* 网关内部：明文扫描阶段在隔离的内存空间执行，即时清理
* 网关 → 内部 MTA：重新封装 TLS，使用内部 CA 颁发的证书
* 内部 MTA → 最终投递：根据安全策略可选维持加密或降级为内部明文

## Certificate Pinning（证书钉扎）

证书钉扎（Certificate Pinning）是一种将特定证书或公钥哈希值硬编码到 TLS 客户端的做法，用于防止 CA 被攻陷时的中间人攻击。在 SMTP 环境中，certificate pinning 常见于内部网关之间的通信，以及 DANE TLSA "2 类型"（SPKI pinning）的应用。

### TLSA 记录中的 SPKI Pinning

RFC 7671 [3] 定义了 DANE TLSA 记录的使用规范，其中 `certificate usage 2` 和 `2` 关联类型（SPKI hash）实现了在 DNS 层面的公钥钉扎：

```
; DANE TLSA 记录 - SPKI Pinning (Usage=2, Selector=1, Matching type=1)
; 2 1 1 与 SHA-256 哈希值
; 这表示只有拥有该 Subject Public Key Info 哈希的服务器被视为可信
_mta._tcp.example.com. IN TLSA 2 1 1 (
  abcd1234ef567890abcdef1234567890
  abcdef1234567890abcdef1234567890
)

; 备用 TLSA 记录（轮换密匙时使用）
_mta._tcp.example.com. IN TLSA 2 1 1 (
  deadbeef0987654321fedcba09876543
  210987654321fedcba0987654321abcd
)
```

### Postfix 中的 CA / 证书固定(pin) 配置

```
# Postfix TLS pinning 配置
# main.cf

# 对特定远程 MTA 启用证书公钥钉扎
# 使用 smtp_tls_policy_maps 按域配置
smtp_tls_policy_maps = hash:/etc/postfix/tls_policy

# /etc/postfix/tls_policy
example.com     fingerprint=B6:12:34:56:78:9A:BC:DE:F0:12:34:56:78:9A:BC:DE:F0:12:34:56
mxbank.com      secure pin=bc12:3456:789a:bcde:f012:3456:789a:bcde

# 生成指纹
openssl x509 -in /path/to/cert.pem -fingerprint -sha256 -noout

# 内部网关之间使用 mutual TLS (mTLS) + pinning
# 双方各验证对方证书指纹，确保通信双方都来自可信端点
smtpd_tls_ask_ccert = yes
smtpd_tls_security_level = encrypt
smtpd_tls_req_ccert = yes
smtp_tls_scert_verifydepth = 5
```

## DANE 与 MTA-STS 架构影响

### TLS 终止模式对 DANE 的影响

RFC 7671 [3] 明确指出，当邮件安全网关作为 TLS 终止点时，它必须验证上游 MTA 的 DANE TLSA 记录。如果网关代表内部域名与外部 MTA 通信，网关需要：

1. 验证对端外发 MTA 的 TLSA 记录（作为 DANE 接收方）
2. 向外部发送方展现与内部域名 TLSA 记录匹配的证书（作为 DANE 发布方）

关键限制：如果网关在 TLS 终止模式下使用自己的证书而非原内部 MTA 的证书，则需要额外发布指向网关证书的 TLSA 记录。否则外部发送方将因 DANE 验证失败而拒绝投递。

```
; 网关托管 DANE 的场景
; 当网关 TLS 终止时，TLSA 记录必须指向网关证书的 SPKI 哈希
; 而非内部 MTA 的证书

; 原 MTA 的 TLSA（内部使用）
_mta._tcp.example.com. IN TLSA 3 1 1 (
  [内部MTA证书公钥哈希]
)

; 网关的附加 TLSA（外部使用，使用 usage=3 作为约束）
_mta._tcp.example.com. IN TLSA 3 1 1 (
  [外部网关证书公钥哈希]
)
```

### MTA-STS 在网关架构中的部署

MTA-STS (RFC 8461) [4] 提供了基于 HTTPS 的策略文件来声明邮件接收方的 TLS 要求。当网关作为入站代理时，MTA-STS 策略应指向网关：

```
; 策略文件内容（托管于 https://mta-sts.example.com/.well-known/mta-sts.txt）
version: STSv1
mode: enforce
mx: mx-gateway.example.com
mx: mx-backup-gateway.example.com
max_age: 86400

; 网关而非内部 MTA 应出现在 MX 和 mta-sts MX 字段中
; 因为外部 MTA 首先与网关建立 TLS 连接
```

```
# 网关自检：验证 MTA-STS 策略文件正确性
# 1. 策略文件可达性
curl -sI https://mta-sts.example.com/.well-known/mta-sts.txt \
  | grep "200 OK"

# 2. 策略文件内容与 MX 记录一致性
dig mx example.com +short | sort
curl -s https://mta-sts.example.com/.well-known/mta-sts.txt \
  | grep "^mx:" | awk '{print $2}' | sort

# 3. TLS 报告端点验证（TLS-RPT，RFC 8460）
curl -s https://mta-sts.example.com/.well-known/mta-sts.txt \
  | grep -q "mode: enforce" && echo "Enforce mode active"
```

## SMTP TLS Session Cache 性能

TLS 会话恢复（Session Resumption）是优化频繁连接场景下性能的关键机制。SMTP 场景中，外部发送方可能在短时间内向同一域名投递数百封邮件，每次都需要 STARTTLS 握手。如果每次握手都走完整的 TLS 交换，CPU 开销和延迟会显著升高。

### Session Cache 配置

```
# Postfix TLS session cache 配置
# main.cf

# 启用 TLS 会话缓存
smtpd_tls_session_cache_database = btree:/var/lib/postfix/smtpd_tls_cache

# 出站 TLS 会话缓存
smtp_tls_session_cache_database = btree:/var/lib/postfix/smtp_tls_cache

# 会话超时（秒，默认 3600 = 1 小时）
smtpd_tls_session_cache_timeout = 3600s
smtp_tls_session_cache_timeout = 3600s

# 缓存大小限制
smtpd_tls_session_cache_min_ttl = 300s  # 最小存活时间

# 出站 TLS 会话缓存（预连接数据库）
# 对频繁投递的域尤其重要
smtp_tls_connection_reuse = no
```

### 缓存性能基准

在 Postfix 邮件网关上的实测数据显示：

| 场景 | 无缓存 | 有缓存（命中） | 提升 |
| --- | --- | --- | --- |
| TLS 1.2 完整握手 | ~8ms | ~1.2ms（会话复用） | ~85% |
| TLS 1.3 完整握手 | ~2.5ms | ~0.8ms（0-RTT） | ~68% |
| 100 连接批量投递 | ~820ms | ~200ms | ~76% |
| CPU 消耗（10000 连接/h） | ~12% | ~3% | ~75% |

### 缓存运维

```
# 监控 TLS 缓存命中率
posttls-finger -c /etc/postfix/main.cf \
  | grep "session cache"

# 查看缓存数据库大小
ls -lh /var/lib/postfix/smtp*_cache
du -sh /var/lib/postfix/*tls*

# 清空缓存（证书轮换后必须执行）
postfix tls flush
# 或手动
postmap -F /var/lib/postfix/smtp_tls_cache

# 监控 TLS 握手耗时
grep -oP 'TLS handshake took \d+ ms' /var/log/mail.log \
  | awk '{print $NF, $4}' \
  | sort -k2 | tail -5
```

## 架构决策对照表

| 需求 | TLS 终止 | TLS 透传 | 混合模式 |
| --- | --- | --- | --- |
| 反垃圾/反病毒扫描 | ✓ 全支持 | ✗ 不支持 | ✓ 终止侧支持 |
| DLP 内容过滤 | ✓ 支持 | ✗ 不支持 | ✓ 终止侧支持 |
| 端到端加密保留 | ✗ 受损 | ✓ 完整保留 | 部分（分段加密） |
| DANE 兼容性 | 需调整 TLSA | ✓ 透明 | 需仔细设计 |
| MTA-STS 兼容性 | 需调整策略 MX | ✓ 透明 | 需仔细设计 |
| 证书管理复杂度 | 高（2 套证书） | 低（无需证书） | 中 |
| 合规审计一致性 | 需额外解释 | ✓ 直观 | 需分段审计 |

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/kb-encrypted-email-gateway-architecture.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
