---
title: "IMAP 的 IDLE（RFC 2177）如何实现“新邮件实时推送”而不必轮询？"
source: "https://ztpop.net/kb/imap-idle-push.html"
license: CC-BY 4.0
---

# IMAP 的 IDLE（RFC 2177）如何实现“新邮件实时推送”而不必轮询？

1
IMAP 的 IDLE（RFC 2177）如何实现“新邮件实时推送”而不必轮询？
▼

**问题**

早期客户端只能定时轮询（NOOP/POLL）查新信，既耗电又延迟高；RFC 2177 的 IDLE 让服务器在“有事件时主动通知”客户端。

**机制**

客户端发 IDLE 进入阻塞等待，服务器在邮箱有变化（新信到达、标记变更）时发无编号响应（EXISTS 等）通知；客户端处理完发 DONE 退出 IDLE 再重新进入，形成长连接推送。

**价值**

近实时收信、省电省流量；是 Push 邮件的基础（移动端“新邮件提醒”多基于此）。

**实践**

邮件系统须支持 IDLE（与 keepalive 配合防断连）；移动客户端优先走 IDLE/推送而非短轮询以提升体验。

参考：RFC 2177（IMAP4 IDLE 非阻塞通知）；RFC 3501（IMAP 基础）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/imap-idle-push.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
