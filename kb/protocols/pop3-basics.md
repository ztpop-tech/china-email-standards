---
title: "POP3 协议（RFC 1939）是什么？它如何把邮件下载到本地客户端？"
source: "https://ztpop.net/kb/pop3-basics.html"
license: CC-BY 4.0
---

# POP3 协议（RFC 1939）是什么？它如何把邮件下载到本地客户端？

1
POP3 协议（RFC 1939）是什么？它如何把邮件下载到本地客户端？
▼

**定义**

POP3（Post Office Protocol v3，RFC 1939）是邮件客户端从服务器“取信”的协议：客户端连上 110 端口（POP3S 为 995 加密），用 USER/PASS 登录，LIST 看邮件清单，RETR 取某封，DELE 标记删除。

**下载模型**

经典 POP3 是“拉取后默认删除服务器副本”（或保留 N 天），适合单设备、省服务器空间；现代客户端常勾选“在服务器保留副本”以支持多端。

**局限**

POP3 对“多设备同步”支持弱——一台下载并删除后，其他设备看不到；文件夹/已读状态也不跨设备同步。

**与 IMAP 对比**

IMAP 把邮件留在服务器、同步文件夹与状态，多端一致；POP3 简单轻量、适合单端归档。二者解决“客户端如何访问邮箱”，但模型截然不同。

参考：RFC 1939（Post Office Protocol - Version 3）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/pop3-basics.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
