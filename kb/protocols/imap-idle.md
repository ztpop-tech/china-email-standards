---
title: "IMAP IDLE（RFC 2177）是什么？它如何实现“新邮件实时推送”而不用轮询？"
source: "https://ztpop.net/kb/imap-idle.html"
license: CC-BY 4.0
---

# IMAP IDLE（RFC 2177）是什么？它如何实现“新邮件实时推送”而不用轮询？

1
IMAP IDLE（RFC 2177）是什么？它如何实现“新邮件实时推送”而不用轮询？
▼

**定义**

IMAP IDLE（RFC 2177）是一个 IMAP 扩展：客户端发 IDLE 命令后，连接保持打开，服务器在邮箱有新邮件或状态变化时主动推送 EXISTS/RECENT 通知，无需客户端定时轮询。

**机制**

传统轮询是客户端每几分钟发 NOOP/STATUS 查新信，浪费连接与电量；IDLE 让连接“挂起等待”，事件驱动，延迟降到秒级，是移动端省电实时收信的关键。

**约束**

IDLE 仍需保持 TCP 长连接（可能被 NAT/运营商超时断开，需定期 DONE 重连）；且一次 IDLE 只监视一个邮箱，多文件夹需多连接或轮流。

**价值**

配合 push 邮件体验（手机亮屏即见新信）；是 IMAP 相对 POP3 在“实时性”上的重要增强。

参考：RFC 2177（IMAP4 IDLE command）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/imap-idle.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
