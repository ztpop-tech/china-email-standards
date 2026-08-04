---
title: "邮件系统日志应按什么顺序分析才能快速定位故障？"
source: "https://ztpop.net/kb/postfix-dovecot-log-fault-localization.html"
license: CC-BY 4.0
---

# 邮件系统日志应按什么顺序分析才能快速定位故障？

1
邮件系统日志应按什么顺序分析才能快速定位故障？
▼

**第一步：确定日志在哪里**

Postfix 把所有成功与失败的投递都记入日志。使用 syslog 时（传统默认），文件通常名为 `/var/log/maillog`、`/var/log/mail` 或类似名称，具体路径由 `/etc/syslog.conf`、`/etc/rsyslog.conf` 等决定；若使用 Postfix 自带的日志机制，则由参数 `maillog_file` 指定位置。排障脚本不应硬编码路径，而应先从这两处确认。

**第二步：按严重级别先捞出「拦路的错误」**

官方给出的第一条命令就是按级别过滤，并且强调**最重要的信息通常出现在输出的开头，后续错误信息价值递减**：

```
grep -E '(warning|error|fatal|panic):' /some/log/file | more
```

四个级别在 Postfix 中有严格语义，读懂它们能直接决定下一步该找谁：

* **panic**：软件自身的问题，只有程序员能修，Postfix 无法继续。
* **fatal**：文件缺失、权限错误或配置错误，需要管理员修复，Postfix 无法继续。
* **error**：错误条件；同一进程内发生超过 13 次会导致该进程终止。
* **warning**：非致命错误，可能是外部 DNS 问题，也可能是本地隐患。

换言之，看到 fatal 应立刻去查配置与权限，看到 panic 则应准备版本信息与复现步骤上报，而不是继续在配置里试错。

**第三步：按队列 ID 与地址串联单封邮件的全链路**

邮件在 Postfix 内的生命周期由队列 ID 串起，官方在队列分析文档中给出的检索方式是直接以队列 ID 为锚点抓取该邮件的全部日志行：

```
tail -10000 /var/log/maillog | grep -E ': 2B2173FF68: '
```

按收件人或发件人域回溯，则用：

```
tail -10000 /var/log/maillog | grep -E -i ': to=<.*@example\.com>,' | less
tail -10000 /var/log/maillog | grep -E -i ': from=<.*@example\.com>,' | less
```

怀疑是队列管理器层面的问题时，单独看它的告警：

```
grep -E 'qmgr.*(panic|fatal|error|warning):' /var/log/maillog
```

这一步的价值在于：它能把「投递失败」这一现象拆解为具体发生在 `cleanup`、`qmgr` 还是 `smtp` 阶段，从而避免在错误的组件上浪费时间。

**第四步：按最小侵入原则逐级升级排查手段**

官方把排查手段按侵入性从低到高排列，明确要求逐级升级，而不是一上来就全局提高日志级别：

* **为特定守护进程加 `-v`**：在 `/etc/postfix/master.cf` 中对选定守护进程追加一个或多个 `-v`，再执行 `postfix reload`。选谁加 `-v` 有讲究——地址重写问题查 `cleanup(8)` 与 `trivial-rewrite(8)`；投递问题查 `qmgr(8)`/`oqmgr(8)` 以及 `lmtp(8)`、`local(8)`、`pipe(8)`、`smtp(8)`、`virtual(8)`。
* **只对特定对端开详细日志**：在 `main.cf` 中设置 `debug_peer_list`，列出远程站点名、域、地址或 net/mask，Postfix 便只对来自/发往这些对端的连接记录大量信息，`postfix reload` 后立即生效。这是在生产环境定位单一对端互通问题的首选手段，日志量可控。
* **更进一步**：临时关闭 `master.cf` 中的 chroot、用 `tcpdump` 录制 SMTP 会话、乃至进程跟踪与调试器。这些手段侵入性显著更高，应在前述步骤全部无果后才考虑。

Dovecot 侧对应的做法是给 `doveadm` 加全局 `-D`（开启详细与调试消息）或 `-v`（详细输出并显示进度计数）；向官方报告问题时需附 `doveconf -n` 输出。Rspamd 侧则在 `local.d/logging.inc` 中用 `debug_modules = ["module_name"];` 精确打开某个模块的调试日志，而非整体调高日志级别。向 Postfix 邮件列表提交问题时，官方要求附上 `postconf -n` 与 `postconf -Mf` 的输出——这两条命令同样是本地自查配置漂移的利器。

参考：Postfix 官方文档 [DEBUG\_README（Postfix Debugging Howto）](https://www.postfix.org/DEBUG_README.html)、[QSHAPE\_README](https://www.postfix.org/QSHAPE_README.html)；Dovecot [doveadm(1) 全局选项](https://doc.dovecot.org/latest/core/man/doveadm-force-resync.1.html)；Rspamd [官方 FAQ](https://rspamd.com/doc/faq.html)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/postfix-dovecot-log-fault-localization.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
