---
title: "Postfix 3.10 新特性详解"
source: "https://ztpop.net/kb/postfix-3-10-new-features.html"
license: CC-BY 4.0
---

# Postfix 3.10 新特性详解

## 概述

Postfix 3.10 于 2026 年初正式发布，是继 3.9 之后的一个重要功能版本。本次更新在安全性、协议兼容性和运维便利性方面均有显著提升，尤其是对 TLS 报告（TLSRPT）的原生支持和 Post-Quantum 加密算法的引入，标志着 Postfix 在应对未来安全挑战方面迈出了关键一步。

## TLSRPT 原生支持

TLSRPT（TLS Reporting，RFC 8460）是一种让邮件服务器报告 TLS 连接问题的机制。此前需要借助外部工具（如 `tlsrpt-reporter`）或自行编写脚本才能生成和发送 TLS 报告。Postfix 3.10 在 `smtpd` 和 `smtp` 进程中内置了 TLS 报告生成能力。

### 配置方式

```
# master.cf
tlsrpt     unix  -       -       n       -       0       tlsrpt
```

启用后，Postfix 会自动解析本域 `_smtp._tls.domain` 的 TLSRPT DNS 记录，收集 TLS 连接统计，按指定周期（通常 24 小时）生成 JSON 格式报告并通过 SMTP 发送到报告地址。

### 数据来源

* `smtpd` 入站连接的 TLS 协商结果
* `smtp` 出站投递的 TLS 协商结果
* 证书链验证失败的具体原因
* 协议版本和密码套件使用统计

## Post-Quantum TLS 加密算法支持

随着量子计算的发展，传统公钥密码（RSA、ECDHE）面临被 Shor 算法破解的风险。Postfix 3.10 引入对混合式 Post-Quantum TLS 密码套件的支持，使用 **Kyber-768** 和 **Kyber-1024**（基于 CRYSTALS-Kyber，已被 NIST 选为标准）作为密钥封装机制（KEM）。

### 编译要求

Post-Quantum 支持需要 OpenSSL 3.5+（启用 `enable-kyber` 编译选项）。编译 Postfix 时需指定：

```
make makefiles CCARGS="-DUSE_TLS -I/usr/local/openssl35/include" \
    AUXLIBS="-L/usr/local/openssl35/lib -lssl -lcrypto"
```

### 配置示例

```
smtpd_tls_eecdh_grade = postquantum
# 或指定混合套件
smtpd_tls_eecdh_grade = hybrid
# 手工指定密码套件
tls_high_cipherlist = ECDHE-KYBER768-CHACHA20-POLY1305:ECDHE-ECDSA-AES256-GCM-SHA384
```

当启用 `postquantum` 模式时，Postfix 优先协商支持 PQ 密码套件的连接，回退到传统 ECDHE 套件以避免兼容性问题。

## SMTP UTF-8 (RFC 6531/6532) 改进

Postfix 3.8 开始实验性支持 SMTPUTF8（RFC 6531），3.10 版本在以下方面做了重要改进：

* **头尾转换修复**：正确实现了 `From` / `To` 头字段在 SMTPUTF8 与非 SMTPUTF8 MTA 之间转码
* **邮件头折叠处理**：UTF-8 邮件头中的长地址支持 RFC 5322 规定的折叠（folding）规则
* **DSN 本地化**：当 DSN 需要发送回支持 SMTPUTF8 的客户端时，诊断信息不再降级为 ASCII
* **`smtputf8_enable` 默认值**：3.10 中新安装实例默认启用 SMTPUTF8

## smtp\_tls\_policy\_maps 性能优化

`smtp_tls_policy_maps` 是 Postfix 出站 TLS 策略的核心配置。3.10 引入了以下优化：

* **缓存分层**：添加了进程级 LRU 缓存，减少对底层数据库（CDB/LMDB/MySQL）的重复查询
* **独立超时**：新增 `smtp_tls_policy_map_cache_size`（默认 32768 条）和 `smtp_tls_policy_map_cache_ttl`（默认 3600 秒）参数
* **延迟加载**：对于 `may` / `none` 策略的域不再加载证书链，直到实际需要时按需加载

## 弃用和废弃的功能

以下功能在 3.10 中标记为弃用，计划在 3.11 或后续版本中移除：

* **`lmtp_nullmx` 支持**：RFC 7505 定义的 Null MX 已被 TLSRPT 等新机制所覆盖
* **SSLv2 兼容代码路径**：Postfix 3.x 已不再允许 SSLv2，遗留的兼容性代码在 3.10 中完全移除
* **`smtpd_use_tls` / `smtp_use_tls` 简写形式**：建议迁移至 `smtpd_tls_security_level` / `smtp_tls_security_level`
* **Postfix-pcre 独立包**：PCRE 支持将合并到主包中

## 从 3.8/3.9 迁移注意事项

| 项目 | 变化 | 建议操作 |
| --- | --- | --- |
| SMTPUTF8 | 默认启用 | 若上游 MTA 不支持，显式设置 `smtputf8_enable = no` |
| 证书验证日志 | 细节更丰富 | 检查 `warning` 级别日志中新增的 TLS 事件，确认无异常 |
| Post-Quantum 支持 | 需 OpenSSL 3.5+ | 升级 libssl-dev 并重新编译 Postfix |
| milter 协议 | 内部状态机优化 | 确保 milter 实现兼容 v6 及以上协议 |
| `max_use` / `max_idle` | 新的默认值 | `max_use` 默认从 100 提升至 200，关注连接池行为 |

## 参考配置清单

以下是推荐的 3.10 最小安全配置，可直接用于生产环境：

```
# Postfix 3.10 安全基线配置
smtpd_tls_security_level = may
smtpd_tls_eecdh_grade = hybrid
smtpd_tls_protocols = TLSv1.2 TLSv1.3
smtpd_tls_mandatory_protocols = TLSv1.2 TLSv1.3
smtp_tls_security_level = dane
smtp_tls_eecdh_grade = hybrid
smtp_tls_protocols = TLSv1.2 TLSv1.3
smtp_tls_mandatory_protocols = TLSv1.2 TLSv1.3
smtputf8_enable = yes
tlsrpt_enable = yes
tlsrpt_reporter_address = tls-reports@example.com
```

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/postfix-3-10-new-features.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
