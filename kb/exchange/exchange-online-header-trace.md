---
title: "Exchange Online 的邮件信头里哪些字段最能帮助追溯来源与防钓鱼？"
source: "https://ztpop.net/kb/exchange-online-header-trace.html"
license: CC-BY 4.0
---

# Exchange Online 的邮件信头里哪些字段最能帮助追溯来源与防钓鱼？

1
Exchange Online 的邮件信头里哪些字段最能帮助追溯来源与防钓鱼？
▼

**认证判定字段**

Authentication-Results 由 Exchange 写入，列出 SPF/DKIM/DMARC 的 pass/fail 与对齐结果；compauth 与 reason 进一步标注复合认证结论。钓鱼邮件常在此呈现 dmarc=fail 或 spf=softfail，是优先排查信号。

**路由溯源字段**

自上而下阅读的 Received 链还原了邮件每一跳；X-MS-Exchange-IncomingMessageId / X-MS-Exchange-Organization-\*-SenderId 等记录内部探针与网络信头。Forwarding 场景可借助 ARC-Seal / ARC-Authentication-Results 保留原始认证结论，避免转发后 DMARC 误判。

**反滥用与威胁字段**

X-MS-Exchange-Organization-Antispam-Report、X-Forefront-Antispam-Report 给出反垃圾/反钓鱼引擎评分与命中规则；X-MS-Exchange-Organization-Network-Message-Id 用于跨日志关联。分析钓鱼时应把这些字段与 Received 链交叉比对，确认伪造跳点。

参考：Microsoft Learn《Anti-spam message headers in Microsoft 365》、RFC 8601《Authentication-Results Header Field》、RFC 8617《ARC》。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/exchange-online-header-trace.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
