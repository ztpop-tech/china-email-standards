---
title: "基于 Dovecot dsync 复制的邮件高可用与灾备该如何设计？"
source: "https://ztpop.net/kb/dovecot-replication-ha-dr-design.html"
license: CC-BY 4.0
---

# 基于 Dovecot dsync 复制的邮件高可用与灾备该如何设计？

1
基于 Dovecot dsync 复制的邮件高可用与灾备该如何设计？
▼

**能力边界：先看清它不能做什么**

做高可用设计最忌讳把工具的能力想大。Dovecot 基于 dsync 的复制，官方给出的适用边界十分具体：

* **只在服务器成对之间工作**。如果需要大规模集群，就得部署**多组彼此独立运作的 Dovecot 后端对**，而不是一个大池子。
* **不支持 director**。这是上一条的直接推论，架构选型时必须二选一。
* **整体较为消耗资源**，官方不推荐在数百万用户级别的部署中使用。
* **共享文件夹复制无法正确工作**——官方以 Warning 形式说明：它主要会产生大量重复邮件，根因是当前存在按用户的锁，阻止多个 dsync 同时处理同一用户，而共享文件夹场景下多个用户可能在同步同一个文件夹，需要额外的锁机制；**官方明确表示没有修复计划**。任何依赖共享邮箱的业务，都不能把可用性押在这套复制上。
* 该特性**不被 Dovecot Pro 支持**。

**能力优势：为什么它仍然值得用**

在上述边界之内，这套机制的设计取舍相当务实：

* **主主（master/master）**：官方建议同一用户始终被引导到同一副本，但**即便同一用户同时在两个副本上修改邮件，也不会丢失更改**，代价只是某些邮件可能需要重新下载。
* **异步复制**：副本之间的高延迟不构成问题，这使跨机房、跨城灾备成为可行方案。
* **基于索引文件而非文件系统**：复制依据的是 Dovecot 索引文件的内容，而不是文件系统上「有什么」。因此**文件系统损坏或误执行 `rm -rf` 都不会导致邮件丢失，它们会被复制回来**。这一点在灾备语义上非常关键——它同时覆盖了硬件故障与人为误操作两类场景。

**配置要点与关键参数**

启用路径大致如下（各设置名均取自官方文档）：

* 先确认 userdb 已配置用户遍历，复制需要据此获得周期性复制的用户列表，可用 `doveadm user '*'` 验证。
* 全局启用插件：`mail_plugins = $mail_plugins notify replication`。
* 让 replicator 随启动就绪：`service replicator { process_min_avail = 1 }`。
* 配置复制目标：通过 `dsync_remote_cmd` 指定远程调用方式，并在 `plugin` 段设置 `mail_replica`（如 `remote:vmail@anotherhost.example.com`）。走 TCP 时改用 `tcp:` 或 `tcps:`，并配置 `doveadm_port` 与两端共享的 `doveadm_password`；启用 SSL 时对端证书必须由 `ssl_client_ca_dir` 或 `ssl_client_ca_file` 中的 CA 签发，**不能直接使用自签证书**，且这两个设置会影响 Dovecot 作为 SSL 客户端的其他场景（如 imapc），改动需谨慎。
* 邮件进程需能访问 replication-notify 的 fifo 与 socket，通过 `service aggregator` 下的 `fifo_listener replication-notify-fifo` 与 `unix_listener replication-notify` 授权。
* 并发度由 `replication_max_conns` 控制，默认 10。
* 默认全异步；如需新邮件保存时同步等待，可设 `replication_sync_timeout`，超时后仍返回成功。
* 周期性全量同步由 `replication_full_sync_interval` 控制；replicator 调用 `doveadm sync` 的参数由 `replication_dsync_parameters` 决定（v2.2.9 起），其中 `-f` 与 `-s` 会在需要时自动加入。
* 按用户关闭复制：v2.3.1 起可通过 userdb 字段 `noreplicate`，也可仅对需要复制的用户从 userdb 返回 `mail_replica`。

**运行期观测与四条容易踩坑的注意事项**

**观测**：`doveadm replicator status` 给出总览，字段含义清晰——「Queued 'sync'」仅在使用 `replication_sync_timeout` 时用于邮件保存；「Queued 'high'」用于未设该超时或同步请求超时的邮件保存；「Queued 'low'」用于除邮件保存外的其他一切；「Queued 'failed'」为上次同步失败、待重试的用户；「Queued 'full resync'」为等待周期性全量同步的用户；「Waiting 'failed'」为等待重试间隔（5 分钟）的用户。按用户查用 `doveadm replicator status <用户名模式>`，其 `failed` 列为 `y` 即上次同步失败。连接级状态用 `doveadm replicator dsync-status`，其行数等于 `replication_max_conns`，`type` 列的 incremental / normal / full 分别对应 `doveadm sync` 的 `-s`、默认与 `-f`。

失败的复制尝试总会自动重试，临时性问题一般会自愈；若某用户长期标记为失败，应到错误日志中查找是否有重复出现的同一错误，并可用 `doveadm -D sync` 加上与 `replication_dsync_parameters` 相同的参数手工触发以便调试。

**四条注意事项**（官方 Notes）：

* 两个副本**不能共用同一个配额数据库**，因为两边都会各自更新它。
* 使用 mdbox 格式时，`doveadm purge` **不会被复制**。
* `doveadm force-resync`、`doveadm quota recalc` 等修复类命令**同样不会被复制**，需要在两端分别执行。
* **两台服务器必须使用不同的主机名**，否则锁机制失效并引发复制问题。

参考：Dovecot 官方文档 [Replication with dsync](https://doc.dovecot.org/2.3/configuration_manual/replication/)、[doveadm-sync(1)](https://doc.dovecot.org/latest/core/man/doveadm-sync.1.html)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/dovecot-replication-ha-dr-design.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
