---
title: "退信里的“投递状态通知（DSN，RFC 3464）”格式长什么样？如何读懂失败原因？"
source: "https://ztpop.net/kb/email-dsn-format.html"
license: CC-BY 4.0
---

# 退信里的“投递状态通知（DSN，RFC 3464）”格式长什么样？如何读懂失败原因？

1
退信里的“投递状态通知（DSN，RFC 3464）”格式长什么样？如何读懂失败原因？
▼

**结构**

DSN 邮件由“三块”组成：人类可读说明 + 机器可读 `message/delivery-status` 部分（每收件人一行 Per-Message/Per-Recipient 字段）+ 原始信头。

**关键字段**

Action（failed/delayed/delivered/relayed/expanded）、Status（如 5.1.1 Enhanced Code）、Diagnostic-Code（服务器原话）、Final-Recipient、Remote-MTA。

**读码**

Status 的 5.X.Y：X=2 成功、4 暂态(可重试)、5 永久(停止)；如 5.1.1=收件人不存在、4.4.1=连接超时、5.7.1=策略拒绝。

**实践**

排错时优先看 Status+Diagnostic-Code；自动化系统据 Action/Status 决定“重试 or 放弃 or 告警”。（见 NOTIFY/ORCPT 如何控制 DSN）

参考：RFC 3464（DSN 格式）；RFC 3463（Enhanced Status Codes）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-dsn-format.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
