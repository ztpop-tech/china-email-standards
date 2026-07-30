---
title: "MTA-STS、DANE 与 TLS-RPT 部署：邮件传输安全三层实践"
source: "https://ztpop.net/kb/dane-mta-sts-tls-rpt-deployment.html"
license: CC-BY 4.0
---

# MTA-STS、DANE 与 TLS-RPT 部署：邮件传输安全三层实践

参考 RFC 7672、RFC 8461、RFC 8460 及部署实践

MTA-STS（RFC 8461）、DANE（RFC 7672）和 TLS-RPT（RFC 8460）共同构成了现代邮件传输安全的三大支柱。本文提供三者的实际部署指南，以及通过 TLS-RPT 报告监控传输问题的方法。

## MTA-STS 部署

### MTA-STS 的工作原理

MTA-STS 允许域管理员通过 DNS 和 HTTPS 发布一个策略文件，要求接收方 MTA 在连接到指定 MX 时使用 TLS 加密，并验证服务器证书。如果接收方 MTA 无法通过 TLS 连接到发件方指定的 MX，邮件不得发送（"strict"模式下）。

### 部署步骤

1. **DNS 记录**：在 \_mta-sts 子域添加 TXT 记录：`_mta-sts.example.com TXT "v=STSv1; id=20260730;"`
2. **策略文件**：在 https://mta-sts.example.com/.well-known/mta-sts.txt 部署 JSON 策略文件
3. **MX 配置**：确保所有 MX 主机名与策略文件中列出的 mx 字段一致，且配置了有效的 TLS 证书
4. **监控**：配置 TLS-RPT 接收 MTA-STS 报告

## DANE (DNSSEC-based) 部署

### DANE 对比 MTA-STS 的优势

DANE 通过 DNSSEC 签名将 TLSA 记录直接发布在 DNS 中，不依赖 PKI/CA 体系。这意味着 DANE 不受 CA 被入侵或 TLS 证书被撤销的问题影响。DANE 是 MTA-STS 的安全增强，部署了 DANE 的域可以获得传输安全保证等级最高的连接。

### 部署步骤

1. **DNSSEC 签域**：域必须启用 DNSSEC 签名
2. **TLSA 记录**：为每个 MX 添加 TLSA 记录，格式：`_25._tcp.mx.example.com IN TLSA 3 1 1 [证书哈希]`
3. **证书匹配**：TLSA 记录的哈希值必须与 MX 服务器当前使用的 TLS 证书的 SPKI 哈希匹配
4. **备份方案**：为每个 MX 至少配置两条 TLSA 记录（当前证书 + 备用证书），用于证书轮转

## TLS-RPT 报告配置

TLS-RPT（TLS Reporting, RFC 8460）定义了 MTA-STS 和 DANE 连接失败的报告格式。部署 TLS-RPT 后：

* 接收方 MTA 在尝试连接发送方 MX 失败时生成结构化报告
* 报告使用 JSON 格式，包含失败的时间、MX 主机名、TLS 错误类型
* 报告通过 SMTP 发送到管理员指定的邮箱地址

TLS-RPT DNS 记录配置示例：

```
_smtp._tls.example.com IN TXT "v=TLSRPTv1; rua=mailto:tls-reports@example.com"
```

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/dane-mta-sts-tls-rpt-deployment.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
