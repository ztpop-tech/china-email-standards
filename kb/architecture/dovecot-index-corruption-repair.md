---
title: "Dovecot 索引文件损坏时应如何诊断与修复？"
source: "https://ztpop.net/kb/dovecot-index-corruption-repair.html"
license: CC-BY 4.0
---

# Dovecot 索引文件损坏时应如何诊断与修复？

1
Dovecot 索引文件损坏时应如何诊断与修复？
▼

**先认清四类索引文件的角色**

Dovecot 的索引文件在三个场景中被使用：邮箱索引（`dovecot.index*`）、邮箱列表索引（`dovecot.list.index*`）以及 mdbox 的 map 索引（`dovecot.map.index*`）。邮箱索引对 maildir、mbox 这类格式是可选的，但对 sdbox、mdbox 这些高性能格式是**必需**的——这一区别直接决定了故障的严重程度。

* **`dovecot.index`（主索引）**：定长记录，至少包含 IMAP UID 与消息标志；可选扩展会增大记录尺寸，包括关键字（自定义标志）、指向 cache 文件的偏移、排序优化记录以及邮箱格式专有扩展。文件头还存有汇总信息（消息总数、未读数、带 \Deleted 标志数），使 IMAP STATUS 命令可被高效应答。**已存在的 `dovecot.index` 永远不会被原地写入**，它只是隔一段时间被惰性重建。
* **`dovecot.index.log`（事务日志）**：承载所有对主索引的变更（不含 cache 内容），是**一个文件夹唯一始终必须存在的文件**。新事务通常追加写入；日志足够大时轮转为 `dovecot.index.log.2` 并新建空日志，`.log.2` 在下次轮转或足够老时被删除。它提供事务原子性，并让其他进程能快速获知邮箱变更——这对 IMAP 在每条命令后向客户端推送变更、以及把索引放在 NFS 或集群文件系统上的部署尤为关键，同时也是 QRESYNC 扩展与 `doveadm sync` 快速取增量的基础。
* **`dovecot.index.cache`（缓存文件）**：缓存邮件头等数据，**缓存内容不可更改**；过大的缓存记录不会被写入以防滥用；每个邮箱可有各自不同的缓存决策，新字段随使用动态加入，长期不访问的字段会被整体丢弃。字段分永久缓存与临时缓存两类，临时字段对保存超过 7 天的邮件可被丢弃。
* **`dovecot.list.index*`**：邮箱列表索引。

**为什么索引会「坏」：字节序与对齐**

索引文件常被 `mmap()` 映射进内存并通过结构体直接访问，这意味着**数据按 CPU 字节序存储**，且所有落盘结构体都必须谨慎处理数据对齐，否则在要求严格对齐的 CPU 上会崩溃。官方对此的说明是：曾考虑过让索引处理不再关心字节序与对齐，但那是一次巨大改动且几乎肯定带来更差的性能；实践中索引文件在小端与大端 CPU 之间迁移的情形极为罕见。

这条设计约束给运维的直接结论是：**跨异构架构迁移邮件时，绝不能直接拷贝索引文件**；官方给出的正确做法是用 dsync 迁移邮件本身。同理，在共享存储上让不同架构的节点访问同一份索引，也属于自找麻烦。

**自愈机制：什么情况下不需要人工介入**

Dovecot 对索引缺失有内建的容错：**索引文件缺失时，邮箱被打开时会自动创建**。此外，若在创建文件或增长文件的任何环节遇到「磁盘空间不足」错误，索引会在本次会话的剩余时间内被透明地转入内存——但**依赖索引文件的邮箱格式（如 dbox）不适用此机制**。

cache 文件也有自净能力：由于并发写入时没有机制阻止两个进程把相同的缓存数据重复写入，同一份数据可能在文件中存在多份，这只浪费磁盘空间而不构成正确性问题，重复项会在下次 purge（重建）时被丢掉。当已过期消息或缓存续行记录过多时，cache 文件会被重建。

因此，遇到「索引报错」先不要急着动手：确认磁盘空间、inode、目录权限是否正常，很多症状在空间恢复后即自行消失。真正需要人工修复的，是 Dovecot 自身无法自动解决的邮箱问题。

**修复动作：doveadm force-resync**

官方对 `doveadm force-resync` 的定位很明确——在某些情况下 `dovecot(1)` 无法自动解决邮箱问题，此时该命令会尝试修复所有问题；**对 sdbox 与 mdbox 邮箱，还会一并检查存储文件**。参数 `mailbox` 指定要修复的邮箱名；使用 mdbox 时所有邮箱都会被修复，因此传 `INBOX` 即可。

```
doveadm force-resync -u bob INBOX
```

常用选项：`-u` 指定用户，支持 `*` 与 `?` 通配（如 `-u *@example.org`）；`-A` 对所有用户执行——官方提醒，与 `userdb { driver = passwd }` 组合使用**不推荐**，因为它会包含 UID 低于 `first_valid_uid` 的系统用户；`-F` *file* 从文件按行读取用户名批量执行；`-S` 指定本地 UNIX socket 绝对路径或 *hostname*:*port*，用于通过 socket 执行；`--no-userdb-lookup` 跳过 userdb 查询、改用 `USER` 环境变量。全局选项中 `-D` 开启调试日志、`-v` 开启含进度计数的详细输出，排障时应优先带上。

批量修复前的两点提醒：使用 `-A` 时若用 SQL userdb，需确保 `userdb_sql_iterate_query` 与库表结构匹配；用 LDAP userdb 则需确保 `userdb_fields` 与 `userdb_ldap_iterate_fields` 匹配 schema，否则 `doveadm(1)` 无法遍历全部用户。另需注意，在启用了 dsync 复制的部署中，`doveadm force-resync` 一类修复命令**不会被复制到对端**，两端都需要各自执行。

参考：Dovecot 官方文档 [Mail Index File Format](https://doc.dovecot.org/2.4.4/developers/design/indexes/index_format.html)、[doveadm-force-resync(1)](https://doc.dovecot.org/latest/core/man/doveadm-force-resync.1.html)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/dovecot-index-corruption-repair.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
