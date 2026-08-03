---
title: "如何分析与利用 TLS-RPT 报告？"
source: "https://ztpop.net/kb/email-authentication-tlsrpt-analysis.html"
license: CC-BY 4.0
---

# 如何分析与利用 TLS-RPT 报告？

1
如何分析与利用 TLS-RPT 报告？
▼

**策略发布**

在域的 DNS 中发布 `_smtp._tls.<domain>` 的 TXT 记录，例如 `v=TLSRPTv1; rua=mailto:tlsrpt@<domain>`，声明接收报告的邮箱。此后对端（接收方 MTA）会定期把本域外发邮件的 TLS 协商结果汇总发回。

**报告结构**

报告为 JSON（通过 SMTP 发送），关键字段含 `policy-domain`、`summary`（total-successful/total-failure 计数）、以及 `failure-details` 数组。每项错误含 `result-type`（如 `starttls-not-supported`、`certificate-host-mismatch`、`certificate-expired`、`validation-time-out`、`tlsa-invalid`）、`sending-mta-ip`、`receiving-mx-hostname` 与 `failed-session-count`。

**分析与处置**

按 `result-type` 聚合失败次数：若大量出现 `starttls-not-supported` 或 `certificate-host-mismatch`，提示对端可能被中间人降级或证书配置错误，应联系对方修复；`certificate-expired` 说明对方证书过期。将报告接入看板与告警，可把原本不可见的明文降级风险转化为可度量指标，与 MTA-STS/DANE 配合形成「强制 TLS + 可观测」闭环。

参考：RFC 8460《SMTP TLS Reporting》、RFC 8461《MTA-STS》、RFC 7672《DANE for SMTP》。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-authentication-tlsrpt-analysis.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
