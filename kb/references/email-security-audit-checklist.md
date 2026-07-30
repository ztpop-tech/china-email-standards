---
title: "邮件系统安全审计清单：认证层、传输层、反垃圾/反钓鱼、合规层 4 层级检查"
source: "https://ztpop.net/kb/email-security-audit-checklist.html"
license: CC-BY 4.0
---

# 邮件系统安全审计清单：认证层、传输层、反垃圾/反钓鱼、合规层 4 层级检查

参考 M3AAWG、NIST SP 800-177 及国内等保 2.0 标准

邮件系统安全审计是评估企业邮件基础设施安全状态的关键环节。基于 NIST SP 800-177（电子邮件安全指南）、M3AAWG 最佳实践和国内等保 2.0（GBT 22239-2019 三级指标），本章提供体系化的邮件安全审计清单。

## 认证层审计

| 检查项 | 审计标准 | 优先级 |
| --- | --- | --- |
| SPF 记录 | 所有发送域部署 SPF，包含所有发件 IP，-all 拒绝策略 | P0 |
| DKIM 签名 | 所有出站邮件使用 2048-bit RSA 签名，密钥轮转 ≤90 天 | P0 |
| DMARC 策略 | 至少 p=quarantine，推荐 p=reject，配置 rua/rf 报告 | P0 |
| BIMI 部署 | 品牌标识已配置，SVG 格式合规，VMC/CMC 证书有效 | P1 |
| ARC 链 | 邮件转发路径的认证结果保留 | P2 |

## 传输层审计

| 检查项 | 审计标准 | 优先级 |
| --- | --- | --- |
| MTA-STS | 已部署 MTA-STS 策略文件，模式为 enforce | P0 |
| DANE | 域已启用 DNSSEC 和 TLSA 记录 | P1 |
| TLS-RPT | 配置 rua 接收传输报告 | P0 |
| TLS 版本 | 禁用 TLS 1.0/1.1，强制 TLS 1.2/1.3 | P0 |
| 证书有效性 | 所有 MX 和提交 MTA 的 TLS 证书未过期、未被吊销、未使用自签名 | P0 |

## 反垃圾/反钓鱼审计

| 检查项 | 审计标准 | 优先级 |
| --- | --- | --- |
| RBL 监测 | 所有发件 IP 不在 Spamhaus/Barracuda/Microsoft 黑名单 | P0 |
| 投诉处理 | 有 FBL 注册，投诉率 <0.08% | P0 |
| 收件人清理 | 硬弹回用户 48h 内移除，不活跃用户季度清理 | P1 |
| MFA | 员工邮箱已启用 MFA，支持 FIDO2/Passkey | P0 |
| 邮件转发禁止 | 禁止邮件自动转发到外部域（防数据泄露） | P1 |

## 合规层审计

* 邮件数据留存策略是否符合《个人信息保护法》要求
* 跨境邮件数据传输的合规性（《数据安全法》跨境数据传输评估）
* 等保 2.0 三级指标的邮件安全控制措施（账号管理、日志审计、备份恢复）
* GDPR 合规（如涉及欧盟用户的邮件通信）
* 电子邮件归档要求（上市公司邮件保存 5-7 年）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-security-audit-checklist.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
