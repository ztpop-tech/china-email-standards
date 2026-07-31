---
title: "RFC 3501 IMAP4rev1：邮件访问协议的命令级详解"
source: "https://ztpop.net/kb/rfc3501-imap-protocol.html"
license: CC-BY 4.0
---

# RFC 3501 IMAP4rev1：邮件访问协议的命令级详解

## 概述

RFC 3501（IMAP4rev1）是迄今部署最广的 IMAP 版本，定义了邮件访问的完整协议细节。尽管 RFC 9051（IMAP4rev2）已发布，绝大多数现役邮件系统仍以 IMAP4rev1 为兼容基线。理解其标志、UID 与搜索机制，是排查"邮件状态不同步""搜索慢"等问题的前提。

## 信箱与命名空间

IMAP 用层级化信箱名（如 `INBOX、INBOX/Sent`），分隔符由服务器声明。NAMESPACE 扩展让客户端发现个人/共享/公共三套命名空间——这对信创邮件系统的"公共文件夹""共享邮箱"实现至关重要。

## FLAGS 与状态

每封邮件有一组标志：系统标志 `\Seen`（已读）、`\Answered`、`\Flagged`、`\Deleted`、`\Draft`，以及用户自定义关键字。通过 `STORE` 修改，状态留在服务器，实现多端同步。`\Deleted` 配合 `EXPUNGE` 才真正删除（IMAP 默认"标记删除"而非立即清除）。

## 序列号 vs UID

序列号是信箱内按到达顺序的临时编号，删信后会重排；`UID` 是每封邮件在信箱内的稳定唯一号（单调递增）。客户端应始终用 `UID` 引用邮件，否则在"收件方删除导致序列号偏移"时会操作错邮件。`UIDVALIDITY` 标识信箱是否重置，避免 UID 复用造成错乱。

## FETCH 与 SEARCH

```
C: A1 FETCH 1:5 (FLAGS INTERNALDATE RFC822.SIZE BODY.PEEK[HEADER])
C: A2 UID SEARCH UNSEEN SINCE 01-JUL-2026
```

`BODY.PEEK[]` 取正文但不置 `\Seen`；`SEARCH` 支持按标志、日期、大小等条件检索。服务端应索引常用搜索字段以保证性能。

## 对信创邮件实现的启示

信创邮件系统实现 IMAP 时，务必正确处理 UIDVALIDITY 的一致性、`\Deleted`+`EXPUNGE` 语义、NAMESPACE 三层结构，否则会踩中 Outlook/手机客户端的兼容性雷区。可参考 Dovecot 的索引与缓存设计。

### 相关主题

* [RFC 9051 IMAP4rev2](/kb/rfc9051-imap4rev2-protocol.html)：现代 IMAP 状态与命令
* [IMAP 与 POP3 对比](/kb/imap-vs-pop3.html)：同步模型选型
* [Dovecot IMAP 服务架构](/kb/dovecot-imap-server-architecture.html)：索引与缓存实现
* [IMAP 并发优化](/kb/imap-concurrency-optimization.html)：多端同步性能

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/rfc3501-imap-protocol.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
