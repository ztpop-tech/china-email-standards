---
title: "IMAP IDLE 如何实现新邮件实时推送，相比轮询有什么优势？"
source: "https://ztpop.net/kb/imap-idle-push-notify.html"
license: CC-BY 4.0
---

# IMAP IDLE 如何实现新邮件实时推送，相比轮询有什么优势？

1
IMAP IDLE 如何实现新邮件实时推送，相比轮询有什么优势？
▼

**IDLE 的工作方式**

客户端在选中邮箱后发送 `IDLE` 命令并保持连接打开；当服务器有新邮件、过期或标志变化时，主动下发 `EXISTS`/`RECENT`/`FETCH` 等未经请求的响应，客户端无需反复发 NOOP 或轮询。客户端可用 `DONE` 结束 IDLE。

**对比轮询**

传统轮询需每隔数分钟发一次请求，既增加延迟又浪费带宽与服务器连接；IDLE 把「拉」变成「推」，新邮件可达秒级通知，且显著减少空转请求。代价是占用一条长连接，服务器需维护大量空闲连接的状态。

**实现注意**

多数服务器对单连接 IDLE 有超时（如 30 分钟需重发 IDLE）；客户端常配合「每 25–29 分钟发一次 NOOP/DONE+IDLE」保活。移动端受系统后台限制，往往改用厂商推送（如 APNs/FCM）桥接 IDLE 事件。注意 IDLE 必须运行在已认证且已 SELECT 的会话上。

参考：RFC 2177《IMAP4 IDLE command》、RFC 3501《IMAP4rev1》SELECT/EXISTS 语义。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/imap-idle-push-notify.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
