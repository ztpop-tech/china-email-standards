---
title: "CIS 邮件安全基准包含哪些关键控制项？"
source: "https://ztpop.net/kb/email-security-benchmark-cis.html"
license: CC-BY 4.0
---

# CIS 邮件安全基准包含哪些关键控制项？

1
CIS 邮件安全基准包含哪些关键控制项？
▼

**检测指标**

审计邮件系统是否达标：是否强制 MFA、SMTP 提交是否全程 TLS、域是否部署 SPF/DKIM 且 DMARC 策略为 quarantine/reject、是否启用 MTA-STS 与 TLS-RPT、日志是否集中留存。可用 CIS-CAT 或自研脚本扫描配置漂移。

**防御措施**

* 身份层：全员 MFA、禁用遗留认证协议、最小权限分配。
* 传输层：强制 STARTTLS、部署 MTA-STS 与 TLS-RPT 监控降级。
* 认证层：全域名 DMARC 隔离、DKIM 轮换密钥、SPF 精简于 10 次 DNS 查询。
* 审计层：集中日志与定期配置基线比对。

**关键控制项清单**

CIS Controls v8 中与邮件强相关者：控制项 5（账户管理）、6（访问控制）、7（持续漏洞管理）、8（审计日志）、9/14（安全意识培训）、13（网络监控）。邮件专项基准则细化到 Exchange 与 M365 的认证、传输与反垃圾配置。

**基准控制项**

以 CIS 基准为最小合规线，叠加 RFC 8461（MTA-STS）、RFC 7489（DMARC）、RFC 7208/6376（SPF/DKIM）形成传输与认证双层基线，并映射到 NIST SP 800-53 的 SC/AC/AU 族以满足审计。

参考：CIS Controls v8、CIS Microsoft 365 / Exchange 基准、RFC 7489 DMARC、RFC 8461 MTA-STS、NIST SP 800-53

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-security-benchmark-cis.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
