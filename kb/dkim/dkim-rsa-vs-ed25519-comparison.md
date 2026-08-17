---
title: "DKIM RSA 与 Ed25519 签名算法选型对比：密钥、性能与渐进式双签名过渡"
source: "https://ztpop.net/kb/dkim-rsa-vs-ed25519-comparison.html"
license: CC-BY 4.0
---

# DKIM RSA 与 Ed25519 签名算法选型对比：密钥、性能与渐进式双签名过渡

DKIM（RFC 6376）长期只有 RSA 一种签名算法。RFC 8301 收紧密钥强度基线后，RFC 8463（2018-09）为 DKIM 增加第二种签名算法 Ed25519-SHA256（基于 Curve25519 的 EdDSA），要求签名方 SHOULD 实现、验证方 MUST 实现。由此进入双算法时代，选型决策涉及密钥体积、签名性能、验证性能、DNS 记录大小与兼容性五个维度。

## 核心对比表

| 维度 | RSA-2048 | RSA-3072 | Ed25519 |
| --- | --- | --- | --- |
| 公钥长度（裸） | 256 字节 | 384 字节 | 32 字节 |
| 签名长度 | 256 字节 | 384 字节 | 64 字节 |
| 公钥 base64（DNS 负载） | 约 360 字符 | 约 512 字符 | **44 字符** |
| DNS TXT 单字符串容纳 | 需 2 段（255 字节上限） | 需 3 段 | **1 段即可** |
| 估算安全强度 | 约 112 位 | 约 128 位 | 约 128 位 |
| 签名性能 | 中等 | 较慢 | **快** |
| 验证性能 | 较快 | 较慢 | **快** |
| 验证方支持现状 | 全部 | 绝大多数 | 主流逐步支持 |

## 逐维度分析

### 密钥长度与 DNS 记录大小

Ed25519 公钥仅 32 字节，base64 后 44 字符，单条 TXT 字符串即可容纳；RSA-2048 公钥 base64 后约 360 字符，必须拆成两段 255 字节字符串（RFC 1035 单字符串上限），RSA-3072 需三段。RFC 8463 明确指出 Ed25519 记录「generally fit in a single 255-byte TXT string and work even with DNS provisioning software that doesn't handle multistring TXT records」——对不支持多段 TXT 的 DNS 管理软件也能正常工作。多段 TXT 依赖拼接顺序，部分缓存层与递归解析器处理存在差异，偶发导致验证失败，单段可彻底规避。

### 签名与验证性能

RSA 验证依赖公钥指数（通常 65537），验证快于签名；Ed25519 在签名与验证两端都有出色表现。对大规模出站系统，签名侧 CPU 开销是实际成本；对接收方网关，验证性能决定吞吐上限。具体差异与硬件指令集及实现（OpenSSL/libsodium/mbedTLS）相关，应以基准测试为准。

### 安全强度

按 NIST SP 800-57 Part 1，RSA-2048 约 112 位、RSA-3072 约 128 位、Curve25519 约 128 位安全强度。以 128 位为现代基线，RSA-2048 处于边界，RSA-3072 与 Ed25519 达标。若追求与基线对齐且避免 RSA 体积问题，Ed25519 更直接；若必须 RSA，应选 3072 位。

### 兼容性现状

RSA 全部验证方支持；Ed25519 自 2018 标准化以来，Gmail/Outlook 与主流开源栈（OpenDKIM 2.11+、Rspamd 等）均已支持，但仍有少量历史验证器只认 RSA——这正是渐进式双签名存在的理由。

## 选择建议：渐进式双签名过渡

RFC 8463 第 6 节给出官方路径：同一邮件同时附加 RSA 与 Ed25519 两段 DKIM-Signature；由于每个选择器在 DNS 中只能有一条公钥记录，两段签名必须使用不同选择器，但可使用相同 d= 与 i= 标识。

四步过渡方案：

1. **发布**：为 Ed25519 新建选择器（如 ed25519._domainkey）并发布 k=ed25519 公钥；保留现有 RSA 选择器不动。
2. **双签观察**：出站同时附两段签名，通过 DMARC 聚合报告与退信监测观察验证通过率，任何接收方都可回退到 RSA 完成验证。
3. **评估**：观察期建议不少于 2-4 周，确认无因 Ed25519 引入的验证失败。
4. **收敛**：确认稳定后保留双签（推荐，成本低、冗余高），或切换为仅 Ed25519。

密钥轮换纪律不变：每算法独立选择器、定期滚动、旧密钥保留一个轮换周期。

## 配置示例

### OpenDKIM 双签名

```
# /etc/opendkim.conf 关键段
Selector          rsa2026
KeyFile           /etc/opendkim/keys/example.com/rsa2026.private
Selector          ed2026
KeyFile           /etc/opendkim/keys/example.com/ed2026.private
SigningTable      refile:/etc/opendkim/signing.table
```

生成 Ed25519 密钥对：

```
openssl genpkey -algorithm ED25519 -out ed2026.private
openssl pkey -in ed2026.private -pubout -out ed2026.public
```

### DNS 记录对比

```
; RSA-2048（多段 TXT，需拼接）
rsa2026._domainkey.example.com. IN TXT (
  "v=DKIM1; k=rsa; p=MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA..."
  "...AQAB" )

; Ed25519（单段 TXT，44 字符公钥）
ed2026._domainkey.example.com. IN TXT "v=DKIM1; k=ed25519; p=11qYAYKxCrfVS/7TyWQHOg7hcvPapiMlrwIaaPcHURo="
```

同一邮件的两段签名头：

```
DKIM-Signature: v=1; a=rsa-sha256; d=example.com; s=rsa2026; ...
DKIM-Signature: v=1; a=ed25519-sha256; d=example.com; s=ed2026; ...
```

## 兼容性观察与 DKIM 演进（2026）

截至 2026 年 8 月，RSA 仍为主流，Ed25519 支持度持续扩大。「DKIM2」目前处于 IETF 个人草案阶段（如 draft-robinson-dkim2-* 系列），非 IETF 工作组文档、未进入标准化进程，选型时不应视为既有标准；可关注 draft-latimer-dkim2-rcpt-nd-signing（2026-05-17，ESMTP 防重放相关）。DKIM 密钥更新工作组（dcrup）已关闭，目前不存在推进 DKIM2 的工作组。

## 权威参考来源

- RFC 8463：A New Cryptographic Signature Method for DKIM（IETF Standards Track）
- RFC 6376：DomainKeys Identified Mail (DKIM) Signatures
- RFC 8301：Cryptographic Algorithm and Key Usage Update to DKIM
- RFC 8032：Edwards-Curve Digital Signature Algorithm (EdDSA)
- RFC 1035：Domain Names - Implementation and Specification（TXT 记录格式）
- NIST SP 800-57 Part 1 Rev.5：Recommendation for Key Management
- OpenDKIM 官方文档（Ed25519 支持自 2.11 起）
