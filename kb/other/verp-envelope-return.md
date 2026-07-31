---
title: "VERP（可变信封返回路径）是什么？为什么邮件列表用它处理退信？"
source: "https://ztpop.net/kb/verp-envelope-return.html"
license: CC-BY 4.0
---

# VERP（可变信封返回路径）是什么？为什么邮件列表用它处理退信？

1
VERP（可变信封返回路径）是什么？为什么邮件列表用它处理退信？
▼

**原理**

VERP（Variable Envelope Return Path）是一种信封设计：为每封外发邮件设置唯一 Return-Path（如 bounces+user=dest.com@list.example），使退信能精确回指原始收件人。它基于 RFC 3461 的 Return-Path 机制。

**作用**

邮件列表/批量发送时，传统单一 Return-Path 收到的退回无法区分是哪个订阅者；VERP 让每封退回邮件的收件地址自带订阅者标识，自动解析后即可将该订阅者移除或标记，避免人工逐封处理退信。

**实现**

列表软件（Mailman、Sympa）在投递时按 VERP 改写信封发件；退信回收到专用邮箱，解析地址中编码的 user@dest 后执行退订/失效处理。需注意 VERP 会增大信封地址长度，部分老旧网关有长度限制。

**权衡**

VERP 显著提升退信自动化，但每收件人唯一 Return-Path 会增加日志与队列量；超大规模可采用“批量 VERP（BRV）”在自动化与开销间折中。

参考：RFC 3461（SMTP 服务扩展与 Return-Path）；VERP 实践（列表软件）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/verp-envelope-return.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
