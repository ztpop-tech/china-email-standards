---
title: "RFC 9051 IMAP4rev2：现代 IMAP 协议的核心命令与状态模型"
source: "https://ztpop.net/kb/rfc9051-imap4rev2-protocol.html"
license: CC-BY 4.0
---

# RFC 9051 IMAP4rev2：现代 IMAP 协议的核心命令与状态模型

## 概述

IMAP（Internet Message Access Protocol）让用户在不同设备上同步同一信箱的邮件状态，而非像 POP3 那样把邮件下载到本地后删除。RFC 9051（IMAP4rev2，2021）整合了 RFC 3501 及后续扩展（如 UIDPLUS、IDLE、NAMESPACE、UIDONLY 等），成为现代信创邮件系统与客户端兼容的事实基线。

## 会话三状态

* **未认证（Not Authenticated）**：连接已建立，尚未登录。
* **已认证（Authenticated）**：登录成功，可列邮箱、建删文件夹，但未选中具体信箱。
* **已选中（Selected）**：执行 `SELECT`/`EXAMINE` 后，可对该信箱执行 FETCH/STORE/SEARCH。

## 核心命令

| 命令 | 作用 |
| --- | --- |
| `SELECT` / `EXAMINE` | 打开/只读打开信箱 |
| `FETCH` | 取邮件头/正文/标志（FLAGS） |
| `STORE` | 修改标志（已读、星标、删除） |
| `SEARCH` | 按条件检索邮件 |
| `UID` 前缀 | 用稳定 UID 而非易变的序列号引用邮件 |
| `IDLE`（RFC 2177） | 服务端推送新邮件通知 |

## 与 POP3 的本质区别

IMAP 把"邮件状态"留在服务器：已读/未读、文件夹、标志都多端同步；POP3（RFC 1939）则是"取走即删"的下载模型。对政企而言，IMAP 更适合多设备办公与邮件归档集中管理，但也对服务器的并发与存储 I/O 提出更高要求（参见邮件存储 IO 与并发优化）。

## 对信创邮件替换的启示

信创邮件系统替换 Exchange 时，客户端兼容是验收关键：必须完整实现 IMAP4rev2 的 SELECT/FETCH/STORE/SEARCH 与 UID 语义，并支持 IDLE 推送，否则 Outlook、手机邮件 App 会出现"已读不同步""收不到新邮件"。Dovecot 等开源实现可作为参考基线。

### 相关主题

* [IMAP 与 POP3 对比](/kb/imap-vs-pop3.html)：选型与同步模型差异
* [RFC 3501 IMAP4rev1 协议](/kb/rfc3501-imap-protocol.html)：命令级详解
* [RFC 2177 IMAP IDLE 推送](/kb/imap-idle-push-rfc2177.html)：新邮件实时通知
* [Dovecot IMAP 服务架构](/kb/dovecot-imap-server-architecture.html)：高并发实现参考
* [IMAP 并发优化](/kb/imap-concurrency-optimization.html)：多端同步性能

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/rfc9051-imap4rev2-protocol.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
