---
title: "怎么看懂 TLS-RPT（SMTP TLS 报告）回传的失败数据？"
source: "https://ztpop.net/kb/tls-rpt-report-interpretation.html"
license: CC-BY 4.0
---

# 怎么看懂 TLS-RPT（SMTP TLS 报告）回传的失败数据？

1
怎么看懂 TLS-RPT（SMTP TLS 报告）回传的失败数据？
▼

TLS-RPT（RFC 8460）是一种**聚合报告机制**，让发送方获知收件方 MX 在建立 TLS 连接时遇到的问题，弥补了 MTA-STS 仅「配置」不「反馈」的盲区。

#### 一、如何声明接收报告的地址

在域名下发布一条 TXT 记录：`_smtp._tls.example.com` 内容为 「v=TLSRPT1; rua=mailto:tls-reports@example.com」。其中 `rua` 即报告接收邮箱。

#### 二、报告长什么样

报告为 JSON 格式，核心字段包括 `organization-name`、`date-range`、以及 `failure-details` 数组。单条失败含 `result-type`（如 「starttls-not-supported」「certificate-host-mismatch」「tls-version」「certificate-expired」）、`sending-mta-ip`、`receiving-mx-hostname` 与 `failed-session-count`。

#### 三、怎么用

当 `result-type` 为证书不匹配或 TLS 版本被降维时，往往提示**中间人拦截或降级攻击**；成功会话则体现在 `summary` 的 `total-successful-session-count`。TLS-RPT 只报告、不阻断，是诊断而非过滤手段。

参考：https://www.rfc-editor.org/rfc/rfc8460

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/tls-rpt-report-interpretation.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
