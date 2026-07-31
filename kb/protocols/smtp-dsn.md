---
title: "投递状态通知（DSN，RFC 3461/3464）是什么？如何读懂失败/延迟/成功回执？"
source: "https://ztpop.net/kb/smtp-dsn.html"
license: CC-BY 4.0
---

# 投递状态通知（DSN，RFC 3461/3464）是什么？如何读懂失败/延迟/成功回执？

1
投递状态通知（DSN，RFC 3461/3464）是什么？如何读懂失败/延迟/成功回执？
▼

**定义**

DSN（Delivery Status Notifications，RFC 3461 命令扩展、RFC 3464 格式、RFC 6522 用 message/global-delivery-status）是邮件系统返回的“回执”：发送方在 MAIL FROM 加 NOTIFY/RET 参数请求，接收/中继方据此生成 multipart/report; report-type=delivery-status 报告。

**三类动作**

success（成功投递）、failure（永久失败）、delayed（暂态延迟，尚未放弃）。failure 对应 5.x 永久错误，delayed 对应 4.x 暂态，最终可能转 success 或 failure。

**如何读**

DSN 含原始信头、子系统诊断（如 smtp; 550 5.1.1 unknown user）与 per-recipient 动作/状态字段。看 Action 知结果、Status 知 RFC 3463 增强状态码、Diagnostic-Code 知对方具体拒绝原因，据此判断是地址错、域不可达还是被策略拒收。

**与退信关系**

DSN 是结构化回执，传统“退信正文”是服务商自由格式；现代 MTA 优先生成 DSN，便于自动解析。结合 VERP（每收件人唯一 Return-Path）可把 DSN 精确归因到具体订阅者，实现退信自动化。

参考：RFC 3461（DSN 命令扩展）；RFC 3464（DSN 格式）；RFC 6522（国际化 DSN）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/smtp-dsn.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
