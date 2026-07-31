---
title: "IMAP 协议（RFC 3501）是什么？它如何实现多设备邮件同步？"
source: "https://ztpop.net/kb/imap-basics.html"
license: CC-BY 4.0
---

# IMAP 协议（RFC 3501）是什么？它如何实现多设备邮件同步？

1
IMAP 协议（RFC 3501）是什么？它如何实现多设备邮件同步？
▼

**定义**

IMAP（Internet Message Access Protocol v4rev1，RFC 3501）是“邮件访问”协议：客户端连 143 端口（IMAPS 993 加密），邮件始终留在服务器，客户端操作的是服务器上的“邮箱/文件夹”视图。

**同步模型**

收件箱、已发送、自定义文件夹都存在于服务器；已读/未读、旗标（flag）状态也在服务器同步，手机、网页、桌面客户端看到的是一致的视图。

**能力**

IMAP 支持选择性下载（只取信头先看摘要，再取正文/附件）、服务器端检索与搜索、多文件夹层级，远比 POP3 丰富。

**价值**

现代多端（手机+电脑+网页）场景的事实标准；但服务器存储与带宽开销更高，需要配套配额与清理策略。

参考：RFC 3501（IMAP4rev1）；与 RFC 1939（POP3）对比

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/imap-basics.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
