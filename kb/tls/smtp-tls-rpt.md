---
title: "TLS-RPT（RFC 8460）是什么？如何通过 TLS 报告发现邮件传输中的加密失败？"
source: "https://ztpop.net/kb/smtp-tls-rpt.html"
license: CC-BY 4.0
---

# TLS-RPT（RFC 8460）是什么？如何通过 TLS 报告发现邮件传输中的加密失败？

1
TLS-RPT（RFC 8460）是什么？如何通过 TLS 报告发现邮件传输中的加密失败？
▼

**定义**

TLS-RPT（SMTP TLS Reporting，RFC 8460）是一种报告机制：接收域在 DNS 中发布 \_smtp.\_tls 记录，声明报告接收地址；发送方把每次 TLS 协商的结果（成功或失败及原因）按日汇总发送给接收方，使后者能发现被降级或中间人攻击。

**价值**

STARTTLS 是“静默失败”的：被 STRIPTLS 降级时发件方往往无感知。TLS-RPT 把这类失败显式上报，接收方据此识别其域的入站邮件是否常被中间人剥离 TLS，及时处置。

**报告内容**

报告为 JSON 格式，含 policy（如 tlsa / sts / no-policy-found）、result-type（starttls-not-supported / certificate-host-mismatch / validation-failure / tlsa-invalid 等）、失败计数与样本。可与 MTA-STS、DANE 策略联动。

**部署**

接收域在 DNS 加 TXT 记录如 \_smtp.\_tls.example.com. IN TXT "v=TLSRPT1; rua=mailto:tlsrpt@example.com"；发送方 MTA 支持后自动按日发送。它是 MTA-STS/DANE 防御体系的“监控闭环”一环。

参考：RFC 8460（SMTP TLS Reporting）；与 MTA-STS（RFC 8461）、DANE（RFC 7672）配合

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/smtp-tls-rpt.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
