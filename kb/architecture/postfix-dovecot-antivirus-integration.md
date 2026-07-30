---
title: "Postfix + Dovecot 反病毒与反垃圾集成"
source: "https://ztpop.net/kb/postfix-dovecot-antivirus-integration.html"
license: CC-BY 4.0
---

# Postfix + Dovecot 反病毒与反垃圾集成

## 概述

邮件服务器的反垃圾和反病毒能力直接关系到用户安全和系统信誉。Postfix 提供了多种集成反垃圾引擎的方式：内容过滤器（content\_filter）、Milter（Sendmail 风格的邮件过滤协议）和代理服务。Dovecot 侧则可以通过 Sieve 脚本和服务端插件在投递阶段进行二次过滤。本文逐一分析各方案的部署方法与优劣。

## 集成架构总览

| 方案 | 调用位置 | 延迟影响 | 优点 | 缺点 |
| --- | --- | --- | --- | --- |
| content\_filter (amavisd-new) | Postfix cleanup 后 | 中 | 成熟、功能全、支持多后端 | 需重启一个额外的服务进程 |
| Milter (clamav-milter / rspamd-milter) | SMTP DATA 结束后 | 低 | 延迟低、协议标准、无需额外 MTA | 不支持对已入列邮件二次检查 |
| Proxy (rspamd-proxy) | SMTP 会话过程中 | 最低 | 可实时拒绝，数据流直通 | 实现复杂，调试困难 |
| Dovecot 侧 (Sieve + antispam 插件) | 投递后 | 无（不阻塞投递） | 不影响 SMTP 吞吐 | 只能隔离，无法拒绝入列 |

## ClamAV 集成

### 方案 A：content\_filter → amavisd-new → ClamAV

经典三件套架构，amavisd-new 作为内容过滤器后台，调用 ClamAV 进行病毒扫描和 SpamAssassin 进行垃圾评分。

```
# master.cf — 添加 amavisd-new filter 服务
smtp-amavis  unix  -       -       y       -       2       smtp
  -o smtp_data_done_timeout=1200
  -o smtp_send_xforward_command=yes
  -o disable_dns_lookups=yes
  -o max_use=20

127.0.0.1:10025 inet  n       -       y       -       -       smtpd
  -o content_filter=
  -o local_recipient_maps=
  -o relay_recipient_maps=
  -o smtpd_restriction_classes=
  -o smtpd_client_restrictions=
  -o smtpd_helo_restrictions=
  -o smtpd_sender_restrictions=
  -o smtpd_recipient_restrictions=permit_mynetworks,reject
  -o mynetworks=127.0.0.0/8
  -o strict_rfc821_envelopes=yes
  -o smtpd_authorized_xforward_hosts=127.0.0.0/8
```

然后在 `main.cf` 中启用内容过滤器：

```
content_filter = smtp-amavis:[127.0.0.1]:10024
```

### 方案 B：clamav-milter

配置较为简洁，适合仅需要反病毒的场景：

```
# main.cf
smtpd_milters = inet:127.0.0.1:7357
non_smtpd_milters = inet:127.0.0.1:7357
milter_protocol = 6
milter_default_action = tempfail

# clamav-milter 配置 (clamav-milter.conf)
MilterSocket inet:7357@127.0.0.1
ClamdSocket tcp:127.0.0.1:3310
OnInfected Reject
AddHeader Replace
```

## Rspamd 集成

Rspamd 是目前邮件社区最活跃的反垃圾引擎之一，使用自研的模糊哈希算法，资源占用低且规则更新快。

### rspamd-proxy 模式（推荐）

Rspamd 代理模式直接嵌入 SMTP 会话，可以在 DATA 阶段实时拒绝垃圾邮件而不先接收完整邮件：

```
# main.cf
smtpd_milters = inet:127.0.0.1:11332
non_smtpd_milters = inet:127.0.0.1:11332
milter_protocol = 6
milter_mail_macros = {auth_type} {auth_author} {auth_authen}

# 启用 rspamd 对出站邮件也进行扫描（可选）
# 出站 milter 配置点在 master.cf 对应 submission 端口中指定
```

### Rspamd Web UI

Rspamd 自带 `rspamd-controller`，提供 Web 管理界面（默认端口 11334）：

```
# rspamd.conf
worker "controller" {
  bind_socket = "127.0.0.1:11334";
  type = "controller";
  enable_password = "your-password";
}
```

通过 Web UI 可以查看实时扫描统计、符号命中率、学习训练效果以及调整评分阈值。

### Rspamd 学习（贝叶斯）

```
# rspamc 命令行学习
rspamc learn_spam /path/to/spam.mbox
rspamc learn_ham /path/to/ham.mbox

# 与 Dovecot 联动：用户从 Junk 文件夹移回 Inbox 则自动学习为 ham
# 需在 dovecot.conf 启用 antispam 插件
```

## SpamAssassin 集成

### spamass-milter

spamass-milter 是 SpamAssassin 的 Milter 封装，配置简洁：

```
# main.cf
smtpd_milters = inet:127.0.0.1:783
milter_protocol = 6

# 启动 spamass-milter
spamass-milter -p 127.0.0.1:783 -u sa-milt -- -x /etc/mail/spamassassin/local.cf
```

### dspam

DSPAM 是一个基于统计学习的反垃圾系统，特色为个体用户级别训练：

```
# main.cf — 通过 content_filter 集成
content_filter = dspam:[127.0.0.1]:6277
```

DSPAM 对每个收件人维护独立的语料库，准确率在高流量场景下表现优秀，但维护成本较高。

## 集成架构比较

### 内容过滤器

* **工作流**：Postfix 接收 → cleanup → content\_filter（amavisd-new → 扫描引擎）→ 重入 Postfix → 投递
* **优点**：最成熟，支持所有扫描引擎的组合，可对邮件进行隔离或修改
* **缺点**：多一次入队/出队开销，延迟增加约 200-500ms

### Milter

* **工作流**：SMTP DATA 结束时由 Postfix 通过 Milter 协议调用外部程序
* **优点**：延迟低，无需额外入队，支持实时拒绝
* **缺点**：协议版本兼容需注意（建议 milter\_protocol = 6）

### 代理模式

* **工作流**：Postfix 将入站 SMTP 连接转发给 rspamd-proxy，代理完成反垃圾检查后再返回 Postfix
* **优点**：可在 DATA 完成前拒绝垃圾邮件，节省带宽
* **缺点**：配置复杂度最高，升级时需协调 Postfix 和代理重启

## 性能优化

### 资源隔离

反垃圾引擎对 CPU 和内存的消耗不容忽视：

* 将 ClamAV / Rspamd / SpamAssassin 部署在独立的物理服务器或容器中
* 为 amavisd-new 设置 `max_servers` 限制（建议 ≤ CPU 核心数×2）
* Rspamd 的 `max_workers` 和 `max_processes` 根据内存配置调整

### 扫描超时设置

```
# postfix main.cf
content_filter = smtp-amavis:[127.0.0.1]:10024
smtp-amavis_destination_concurrency_limit = 4
smtp-amavis_connect_timeout = 30
smtp_data_done_timeout = 300

# amavisd-new — 设置各引擎超时
$child_timeout = 120;
$MAXLEVELS = 10;
$MAXFILES = 1500;
```

### 白名单/灰名单

减少对可信发件人的扫描，节省资源：

```
# Rspamd 白名单 /etc/rspamd/local.d/whitelist.inc
whitelist = {
  "sender" = "newsletter@trusted.com";
  "ip" = "198.51.100.0/24";
  "from" = "*.bank.com";
}

# Postfix 跳过内容过滤器
# 在 main.cf 的 smtpd_recipient_restrictions 前加上
check_client_access hash:/etc/postfix/whitelist_filter_skip
```

### 灰名单策略

Postfix 内置的灰名单（greylisting）机制配合 Rspamd 的灰名单模块，可以在响应阶段即过滤大量批量发送的垃圾邮件，有效减轻下游扫描引擎的负载。

## Dovecot 侧集成

Dovecot 可以通过 antispam 插件与后端反垃圾引擎联动：

```
plugin {
  antispam_backend = rspamc
  antispam_spam = Junk
  antispam_trash = Trash
  antispam_allow_append_to_spam = yes
}
```

用户将邮件移入/移出 Junk 文件夹时，Dovecot 自动触发 `rspamc learn_spam / learn_ham`，持续优化垃圾评分模型。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/postfix-dovecot-antivirus-integration.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
