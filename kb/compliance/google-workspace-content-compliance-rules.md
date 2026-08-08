---
title: "Google Workspace 内容合规（Content compliance）规则怎么设，能做什么动作？"
source: "https://ztpop.net/kb/google-workspace-content-compliance-rules.html"
license: CC-BY 4.0
---

# Google Workspace 内容合规（Content compliance）规则怎么设，能做什么动作？

1
Google Workspace 内容合规（Content compliance）规则怎么设，能做什么动作？
▼

**是什么**

内容合规是 Gmail Compliance 中的高级内容过滤。管理员可针对含特定字词/模式/元数据的邮件设规则，例如拒绝可能含敏感信息的出站邮件、对特定 IP 范围邮件隔离、把匹配文本串的邮件路由到法务部门。

**适用范围与表达式**

规则里勾选 Inbound / Outbound / Internal-receiving / Internal-sending 决定对哪类邮件生效；可加最多 10 条表达式，支持 Simple match、Advanced content match、Metadata match、Predefined content match（如信用卡号、SSN 等 DLP 检测器）。Advanced content match 可指定 Location（Headers+Body / Full headers / Body / Subject / Sender / Recipients / Envelope sender / Any envelope recipient / Raw message）与 Match type（Contains / Matches regex / Equals / Is empty 等）。Metadata match 支持来源 IP 范围、TLS、邮件大小、认证状态（符合 DMARC：通过 SPF 或 DKIM 即视为已认证）。

**可执行的动作**

命中后可 Reject（拒绝，自动加 550 5.7.1 等 SMTP 码，可自定义退信语）、Quarantine（送管理员隔离区）、Deliver with modifications（加头/删附件/改 envelope 收件人/加收件人/改路由）。

**多规则冲突**

若多条设置都想"改主路由"，Gmail 只取其一；更具体的单位设置优先于继承设置，针对性相同时先创建者优先。

参考：Google Workspace Help · 1346934 / 7676854 / 2683865

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/google-workspace-content-compliance-rules.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
