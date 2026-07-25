---
title: "IMAP 并发优化：Dovecot 连接池、索引缓存与 LMTP 批量投递"
source: "https://ztpop.net/kb/imap-concurrency-optimization.html"
license: CC-BY 4.0
---

# IMAP 并发优化：Dovecot 连接池、索引缓存与 LMTP 批量投递

## 概述

Dovecot 采用事件驱动的非阻塞 I/O 模型处理 IMAP/POP3 连接，单进程可管理数千个并发连接。imap-login 进程负责 TLS 握手与认证代理，认证通过后将连接移交给 imap 工作进程。在高并发场景下，连接管理策略、索引缓存命中率和 LMTP 投递效率决定了用户体验的响应速度。优化需从用户到存储的分层逐一审视：连接层减少不必要的进程 fork，缓存层最大化内存利用率，投递层降低邮件进入 Maildir 的写入延迟。

## Dovecot 连接管理调优

Dovecot 的连接模型分为 login 进程和 imap/pop3 进程两层。imap-login 的 process\_limit 控制同时处理登录握手的进程数，万级用户建议提升至 256。imap 的 process\_limit 控制实际处理邮件操作的进程数上限，每个进程内使用 I/O 多路复用管理数百个连接。service\_count 参数控制进程生命周期内可处理的连接数：设为 0 表示永不过期（连接池模式），设为 1 表示每个连接 fork 一个新进程（隔离模式，更安全但开销大）。

```
# Dovecot 10-master.conf 连接池配置
service imap-login {
  inet_listener imap { port = 143 }
  process_limit = 256
  process_min_avail = 4
  service_count = 0
}
service imap {
  process_limit = 2048
  vsz_limit = 512M
  service_count = 0
}

# 10-mail.conf: 限制单 IP 并发连接
mail_max_userip_connections = 20

# 监控活跃连接
doveadm who | head -30
doveadm process status
ss -tn state established | grep ':143\|:993' | wc -l
```

## 索引缓存优化

Dovecot 为每个 Maildir 文件夹维护索引文件（dovecot.index / dovecot.index.cache），缓存邮件头部、标记状态和正文关键字以提高列表和搜索性能。mail\_cache\_max\_size 控制每邮箱的缓存文件大小上限，大邮箱（>10 万封）应增大至 64MB 以上。FTS（全文搜索）插件的索引可大幅提升搜索速度，但需权衡索引文件存储开销。Postfix 的 LMTP 投递方式优于 pipe 方式的 dovecot-lda，批量投递时减少 fork 开销。

```
# Dovecot 索引缓存配置
mail_cache_max_size = 64M
mail_cache_min_mail_count = 30
mail_cache_record_max_size = 1M

# Postfix LMTP 投递配置
# master.cf: lmtp unix - - n - - lmtp
# main.cf: mailbox_transport = lmtp:unix:private/dovecot-lmtp

# Dovecot LMTP 配置
service lmtp {
  unix_listener /var/spool/postfix/private/dovecot-lmtp {
    mode = 0600
    user = postfix
    group = postfix
  }
  process_limit = 50
}
```

## 踩坑与排错

IMAP 客户端（尤其是移动端）频繁轮询会消耗大量 imap 进程——应在服务器端启用 IDLE 推送以减少轮询次数。索引文件损坏可能导致客户端列表操作变慢或报错，可通过 doveadm index -u user@domain INBOX 重建索引。LMTP 投递时若 Dovecot 的 lmtp 进程无法启动，需检查 Unix Socket 权限是否允许 Postfix 写入。service\_count=0 模式下进程内存泄漏会随时间累积并最终触发 vsz\_limit 被杀。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/imap-concurrency-optimization.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
