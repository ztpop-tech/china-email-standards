---
title: "Postfix 队列里的邮件一直卡在 incoming 队列，如何排查？"
source: "https://ztpop.net/kb/postfix-faq-04.html"
license: CC-BY 4.0
---

# Postfix 队列里的邮件一直卡在 incoming 队列，如何排查？

1
Postfix 队列里的邮件一直卡在 incoming 队列，如何排查？
▼

**原因**

多见于 cleanup 进程异常、队列目录权限错误或磁盘问题，邮件无法从 incoming 转入 active。

**解决**

用 postqueue -p / mailq 查看队列；确认 /var/spool/postfix 权限正确且磁盘未满；执行 postsuper -p 修复队列结构，必要时重启 Postfix。

参考：Postfix FAQ “Mail stays queued in the incoming queue”

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/postfix-faq-04.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
