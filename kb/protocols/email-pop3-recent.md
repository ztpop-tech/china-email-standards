---
title: "POP3 的“会话与状态”行为有哪些容易忽略的细节（RETR/DELE/STAT/UIDL）？"
source: "https://ztpop.net/kb/email-pop3-recent.html"
license: CC-BY 4.0
---

# POP3 的“会话与状态”行为有哪些容易忽略的细节（RETR/DELE/STAT/UIDL）？

1
POP3 的“会话与状态”行为有哪些容易忽略的细节（RETR/DELE/STAT/UIDL）？
▼

**会话态**

POP3 是“单连接单邮箱”模型：登录后服务器给邮件打“待删标记”，QUIT 才真正执行删除；中途断线则删除不生效（邮件恢复）。

**命令**

STAT 看数量/大小；LIST 列每封大小；UIDL 给每信稳定唯一 ID（重下不乱，见 UIDL 篇）；RETR 取信；DELE 标删；RSET 撤销本会话所有删除。

**无状态差异**

不同于 IMAP，POP3 不保留“已读/文件夹”等跨会话状态，多设备同步差；常见“收完即删留本地”或“保留服务器副本”两种模式。

**实践**

客户端要正确处理“DELE 仅标记、QUIT 才落定”；多设备用户常选“保留副本”避免一台收走全删，但需防服务器配额爆。

参考：RFC 1939（POP3 命令与状态）；RFC 2384/2449（扩展）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-pop3-recent.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
