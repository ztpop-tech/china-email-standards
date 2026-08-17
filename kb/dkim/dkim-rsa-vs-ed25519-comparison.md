---
title: "DKIM RSA 与 Ed25519 签名算法选型对比：密钥、性能与渐进式双签名过渡"
source: "https://ztpop.net/kb/dkim-rsa-vs-ed25519-comparison.html"
license: CC-BY 4.0
---

# DKIM RSA 与 Ed25519 签名算法选型对比：密钥、性能与渐进式双签名过渡

发布于 2026-08-17

## 1. 算法背景：从 RSA 独占到双算法时代

DKIM（DomainKeys Identified Mail，RFC 6376）自 2007 年发布以来，签名算法长期只有 RSA 一种。RFC 6376 第 3.3 节定义了 `rsa-sha256` 与 `rsa-sha1` 两种算法组合，其中 RSA 公钥存储在 DNS TXT 记录中供验证方取用。

密码学基线随算力提升而不断抬高：RFC 8301（2018-01）废弃 SHA-1、要求 RSA 密钥至少 1024 位并强烈推荐 2048 位；同年 9 月，RFC 8463 为 DKIM 增加了第二种签名算法——**Ed25519-SHA256**（基于 Curve25519 曲线的 Edwards 曲线数字签名算法 EdDSA）。RFC 8463 明确要求：签名方 SHOULD 实现、验证方 MUST 实现该算法。

由此，DKIM 进入 RSA 与 Ed25519 双算法时代。选型决策涉及密钥体积、签名性能、验证性能、DNS 记录大小与接收方兼容性五个维度，本文逐项对比并给出渐进式过渡建议。

## 2. 核心对比表

| 维度 | RSA-2048 | RSA-3072 | Ed25519 |
| --- | --- | --- | --- |
| 公钥长度（裸） | 256 字节 | 384 字节 | 32 字节 |
| 私钥长度 | 约 256 字节（含 CRT 参数更大） | 约 384 字节 | 32 字节 |
| 签名长度 | 256 字节 | 384 字节 | 64 字节 |
| 公钥 base64（DNS 记录负载） | 约 360 字符 | 约 512 字符 | **44 字符** |
| DNS TXT 单字符串容纳 | 需 2 段（255 字节上限） | 需 3 段 | **1 段即可** |
| 估算安全强度 | 约 112 位 | 约 128 位 | 约 128 位 |
| 签名性能 | 中等（私钥操作相对慢） | 较慢 | **快** |
| 验证性能 | 较快（公钥指数小） | 较慢 | **快** |
| 标准化状态 | RFC 6376 | RFC 6376（密钥长度自选） | RFC 8463 |
| 验证方支持现状 | 全部 | 绝大多数 | 主流逐步支持（Gmail/Outlook 已支持） |

说明：RSA 公钥的「裸长度」指模数（modulus）字节数；DNS 中实际发布的是 base64 编码的公钥，且 RFC 6376 要求 `p=` 值以 base64 表示。TXT 记录单字符串上限 255 字节（RFC 1035），超长需拆分为多段——并非所有 DNS 管理系统与解析器都能正确处理多段 TXT，这是 RSA 2048 以上密钥在部分环境中的部署痛点。

## 3. 逐维度分析

### 3.1 密钥长度与 DNS 记录大小

这是两种算法最直观的差异。Ed25519 公钥仅 32 字节，base64 编码后 44 字符，单条 TXT 字符串即可容纳；RSA-2048 公钥 base64 后约 360 字符，必须拆成两段 255 字节字符串，RSA-3072 则需三段。

RFC 8463 特别指出：Ed25519 公钥记录「generally fit in a single 255-byte TXT string and work even with DNS provisioning software that doesn't handle multistring TXT records」——即对不支持多段 TXT 的 DNS 管理软件也能正常工作。对于使用托管 DNS、配置界面简陋或存在历史兼容问题的环境，这是显著的运维优势。

多段 TXT 的解析依赖查询结果拼接顺序；实践中部分权威 DNS 会按段顺序返回，但缓存层与部分递归解析器对多段 TXT 的处理存在差异，偶发导致 DKIM 验证失败。单一字符串可彻底规避此类问题。

### 3.2 签名与验证性能

RSA 的验证性能依赖公钥指数（通常 65537），验证快于签名；而 Ed25519 在签名与验证两端都有出色表现，且验证不依赖任何特定指数。对大规模出站邮件系统（日发数百万封），签名侧 CPU 开销是实际成本；对接收方网关，验证性能决定吞吐上限。Ed25519 在两端的优势使其成为高吞吐场景的优选。

注意：实际性能差异与硬件（是否支持 AES-NI/AVX-512 等指令集）及实现（OpenSSL、libsodium、mbedTLS）密切相关，本文给出的是相对量级结论，具体项目应以基准测试为准。

### 3.3 安全强度

按 NIST SP 800-57 Part 1 的估算，RSA-2048 提供约 112 位安全强度，RSA-3072 提供约 128 位；Curve25519（Ed25519 所用曲线）提供约 128 位安全强度。若以 128 位为现代基线，RSA-2048 已处于边界，RSA-3072 与 Ed25519 均达标。

RFC 8301 当前要求 RSA 至少 1024 位、推荐 2048 位。若追求与 128 位基线对齐且避免 RSA 密钥体积问题，Ed25519 是更直接的选择；若必须保持 RSA，应选择 3072 位而非 2048 位。

### 3.4 兼容性现状

RSA 是所有验证方都支持的算法，兼容性无虞；Ed25519 自 2018 年标准化以来，主流邮箱服务商（Gmail、Outlook）与主流开源栈（OpenDKIM 2.11+、Rspamd、Mailcow 等）均已支持。但仍有少量历史验证器只认 RSA，单签 Ed25519 可能导致这些接收方验证失败——这正是「渐进式双签名」存在的理由。

## 4. 选择建议：渐进式双签名过渡

RFC 8463 第 6 节（Transition Considerations）给出了官方过渡路径：**同一封邮件同时附加 RSA 与 Ed25519 两段 DKIM-Signature**，由于每个选择器（selector）在 DNS 中只能有一条公钥记录，两段签名必须使用不同的选择器，但可使用相同的 `d=` 与 `i=` 标识。

推荐的四步过渡方案：

1. **发布**：为 Ed25519 新建选择器（如 `ed25519._domainkey`）并发布 `k=ed25519` 公钥记录；保留现有 RSA 选择器不动。
2. **双签观察**：出站邮件同时附 RSA 与 Ed25519 签名，通过 DMARC 聚合报告与退信监测观察验证通过率。此阶段任何接收方都可回退到 RSA 签名完成验证，风险可控。
3. **评估**：观察期建议不少于 2-4 周（覆盖完整业务周期），确认无因 Ed25519 引入的验证失败。
4. **收敛**：确认稳定后，可选择保留双签（推荐，成本低、冗余高），或在目标接收方全部支持后切换为仅 Ed25519 签名。

无论选择哪种算法，密钥轮换纪律不变：为每个算法维护独立选择器、定期滚动、旧密钥保留一个轮换周期（参见 DKIM 密钥轮换管理实践）。

## 5. 配置示例

### 5.1 OpenDKIM 双签名配置

```
# /etc/opendkim.conf 关键段（双签名：RSA + Ed25519）
# RSA 选择器与密钥
Selector          rsa2026
KeyFile           /etc/opendkim/keys/example.com/rsa2026.private
# Ed25519 选择器与密钥（OpenDKIM 2.11+ 支持）
Selector          ed2026
KeyFile           /etc/opendkim/keys/example.com/ed2026.private
# 对每封邮件同时附加两段签名
SigningTable      refile:/etc/opendkim/signing.table
```

生成 Ed25519 密钥对（OpenSSL 1.1.1+ 或 libsodium）：

```
# OpenSSL 生成 Ed25519 私钥
openssl genpkey -algorithm ED25519 -out ed2026.private
openssl pkey -in ed2026.private -pubout -out ed2026.public
# 将公钥的 base64 主体（去除 PEM 头尾）填入 DNS TXT 的 p= 字段
```

### 5.2 DNS 记录对比

```
; RSA-2048（多段 TXT，需拼接）
rsa2026._domainkey.example.com. IN TXT (
  "v=DKIM1; k=rsa; p=MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA..."
  "...AQAB" )

; Ed25519（单段 TXT，44 字符公钥）
ed2026._domainkey.example.com. IN TXT "v=DKIM1; k=ed25519; p=11qYAYKxCrfVS/7TyWQHOg7hcvPapiMlrwIaaPcHURo="
```

签名头示例（同一邮件的两段 DKIM-Signature，来自 RFC 8463 Appendix A 的格式约定）：

```
DKIM-Signature: v=1; a=rsa-sha256; d=example.com; s=rsa2026; ...
DKIM-Signature: v=1; a=ed25519-sha256; d=example.com; s=ed2026; ...
```

## 6. 兼容性观察与 DKIM 演进（2026）

截至 2026 年 8 月，DKIM 的算法格局保持稳定：RSA 仍为主流，Ed25519 支持度持续扩大。需要注意，社区讨论中的「DKIM2」目前处于 IETF 个人草案阶段（如 draft-robinson-dkim2-\* 系列），并非 IETF 工作组文档、也未进入标准化进程，写作与选型时不应将其视为既有标准；可关注的新进展包括 draft-latimer-dkim2-rcpt-nd-signing（2026-05-17，ESMTP 防重放相关）等个人草案。DKIM 密钥更新工作组（dcrup）已完成历史使命关闭，目前不存在推进 DKIM2 的工作组。

### 相关主题

* [RFC 8463 DKIM 的 ed25519 签名：更短密钥、更强抗量子前景](/kb/rfc8463-dkim-ed25519.html)
* [RFC 8301 DKIM 加密算法更新：密钥强度与哈希的现代基线](/kb/rfc8301-dkim-crypto-update.html)
* [DKIM 能用 Ed25519 密钥签名吗（RFC 8463）？](/kb/dkim-ed25519-signature.html)
* [DKIM 密钥轮换管理](/kb/dkim-key-rotation-management.html)
* [DKIM 记录检查器（在线工具）](/tools/dkim-checker.html)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/dkim-rsa-vs-ed25519-comparison.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
