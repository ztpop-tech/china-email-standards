---
title: "Dovecot 高级配置指南"
source: "https://ztpop.net/kb/dovecot-imap-advanced-config.html"
license: CC-BY 4.0
---

# Dovecot 高级配置指南

## 概述

Dovecot 是 Linux 平台上最流行的开源 IMAP/POP3 服务器之一。本文面向有 Dovecot 基础运维经验的工程师，深入讲解 dsync 高可用、FTS 全文搜索、Push 通知、压缩存储、配额管理和性能调优等高级话题。

## dsync 高可用同步配置

dsync 是 Dovecot 内置的邮箱同步工具，支持增量同步和多副本部署。

### 方案一：共享文件系统

两个 Dovecot 节点共享同一份存储（NFS/GlusterFS/DRBD），dsync 仅需同步元数据和锁状态：

```
# dovecot.conf — 双节点共享存储
mail_location = sdbox:/mnt/shared/mail/%u
dsync_alt_char = _
# 心跳和故障转移
service doveadm {
  inet_listener {
    port = 12345
    ssl = yes
  }
}
# 主节点上用 cron 定期同步
# */5 * * * * /usr/bin/doveadm sync -u remote:user@192.168.1.2
```

共享文件系统方案的优点是无数据冗余，瓶颈在于存储的 IOPS。建议使用 SSD 并启用 `mmap_disable = yes`。

### 方案二：主从复制

异地主从复制，每台机器持有完整副本：

```
# 主节点：推送模式
mail_location = sdbox:/var/vmail/%u
dsync_alt_char = _

# 从节点配置：接受同步
protocol doveadm {
  mail_plugins = notify replication
}
plugin {
  replication_dsync_parameters = -d -N 30 -l 30 -U -t 300
}
service replicator {
  process_min_avail = 1
  unix_listener replicator-doveadm {
    mode = 0600
    user = vmail
  }
}
```

主从复制适合双活或灾备场景，缺点是存储开销翻倍。

## Full Text Search (FTS) 引擎选择

Dovecot 的 FTS 插件允许客户端对邮件正文进行全文搜索。支持的引擎及其对比：

| 引擎 | 索引存储 | 性能 | 适用场景 |
| --- | --- | --- | --- |
| Solr | 外部 HTTP 服务 | 高（批量搜索） | 大规模部署（万级用户+） |
| Xapian | 本地文件 | 中高 | 中等规模（千级用户） |
| Flatcurve | 本地文件（LMDB 后端） | 高（写入/搜索均衡） | 中小规模（无需外部依赖） |

### Flatcurve 配置示例

```
# 推荐用于中小规模部署
mail_plugins = $mail_plugins fts fts_flatcurve

plugin {
  fts = flatcurve
  fts_flatcurve = max_term_size=30 max_doc_size=256k
  fts_autoindex = yes
  fts_autoindex_exclude = \Trash \Junk
  fts_autoindex_max_recent_msgs = 500
}
```

**迁移建议**：从 Solr 迁移到 Flatcurve 时，使用 `doveadm fts rescan -u user@domain` 重建索引。

## Push 通知机制

移动客户端要求邮件到达后即时推送，而非定期轮询。Dovecot 支持以下推送机制：

### IMAP IDLE

RFC 2177 定义的 IMAP IDLE 命令让客户端保持长连接，Dovecot 有新邮件时立即推送：

```
protocol imap {
  imap_idle_notify_interval = 29  # 29 秒心跳
  mail_max_userip_connections = 30
}
```

### Apple Push (APNs)

iOS 设备使用 Apple Push Notification service：

```
plugin {
  push_notification_driver = apns:cert=/etc/dovecot/push/apns-cert.pem
  push_notification_recipient_filter = %{if;%{userdb:apple-push-token};eq;;;true;false}
}
```

### Android / UnifiedPush

Android 和 Linux 桌面客户端可通过 UnifiedPush 协议接收通知。需安装 `dovecot-push-notification-plugin` 并配置推送网关地址。

## 压缩策略

邮件存储压缩可节省 60%-80% 的磁盘空间，代价是轻微的性能损耗。

### mail\_attachment\_dir 外置附件

将邮件附件单独存储，同一附件仅保留一份实体：

```
plugin {
  mail_attachment_dir = /var/vmail/attachments
  mail_attachment_hash = %{sha256}
  mail_attachment_min_size = 4096  # 大于 4KB 的附件离体存储
  mail_attachment_fs = sis posix
  mail_attachment_compress = gz
}
```

### zlib 插件

对整个邮件存储启用 gzip 压缩：

```
mail_plugins = $mail_plugins zlib
plugin {
  zlib_save = gz
  zlib_save_level = 6   # 1-9，默认 6
}
```

## 配额管理

### quota 插件

```
plugin {
  quota = dict:User quota::proxy::quotadict
  quota_rule = *:storage=5GB:messages=500000
  quota_rule2 = Trash:storage=500MB
  quota_rule3 = Junk:storage=250MB
  quota_warning = storage=95%% /usr/local/bin/quota-warning.sh 95 %u
  quota_warning2 = storage=100%% /usr/local/bin/quota-warning.sh 100 %u
}
```

### quota\_warning 脚本

示例告警脚本：

```
#!/bin/bash
# /usr/local/bin/quota-warning.sh
PERCENT=$1
USER=$2
SENDMAIL="/usr/sbin/sendmail"
cat << EOF | $SENDMAIL -t
From: postmaster@example.com
To: $USER
Subject: 邮箱使用量已达 ${PERCENT}%

您好，您的邮箱使用量已达 ${PERCENT}%。
请及时清理邮件，以免影响正常收信。
EOF
```

## 性能调优参数

### mail\_prefetch\_count

控制 Dovecot 从后端存储预读邮件数量的线程数。对于 SSD 存储，适当提高该值可提升 IMAP 客户端的列表和打开速度：

```
mail_prefetch_count = 20  # 默认 0（关闭预读），SSD 建议 10-20
```

### imap\_client\_workarounds

处理各类邮件客户端的兼容性问题：

```
imap_client_workarounds = outlook-idle delay-newmail tb-extra-mailbox-sep
```

* `outlook-idle` — 修复 Outlook 对 IDLE 命令的错误处理
* `delay-newmail` — 延迟发送新邮件通知直至客户端准备就绪
* `tb-extra-mailbox-sep` — 兼容 Thunderbird 的额外分隔符处理

### 进程和连接优化

| 参数 | 推荐值 | 说明 |
| --- | --- | --- |
| `service imap-login { process_limit }` | 256 | 同时运行的 IMAP 登录进程上限 |
| `service imap { service_count }` | 0 | 0=每个连接新建进程，避免单个进程处理过多连接 |
| `service imap { vsz_limit }` | 512M | IMAP 进程虚拟内存上限 |
| `mailbox_list_index` | yes | 使用邮箱列表索引加速 LIST 命令 |
| `pop3_uidl_format` | %08Xu%08Xv | POP3 UIDL 格式，确保跨重启唯一 |

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/dovecot-imap-advanced-config.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
