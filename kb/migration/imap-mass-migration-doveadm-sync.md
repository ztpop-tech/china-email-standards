---
title: "用 doveadm sync/backup 做大规模邮箱迁移的正确姿势是什么？"
source: "https://ztpop.net/kb/imap-mass-migration-doveadm-sync.html"
license: CC-BY 4.0
---

# 用 doveadm sync/backup 做大规模邮箱迁移的正确姿势是什么？

1
用 doveadm sync/backup 做大规模邮箱迁移的正确姿势是什么？
▼

**三种模式的语义差别决定迁移方案**

dsync（即 `doveadm sync` / `doveadm backup`）可用于双向同步邮箱、创建备份、转换邮箱格式（例如 Maildir 转 mdbox），并支持同机或跨机（ssh、tcp 或 IMAP 协议）操作。三种模式的语义必须分清：

* **`doveadm backup`**：单向同步，**目标端的任何更改都会被回滚**，结束后目标与源完全一致。
* **`doveadm sync`**：双向同步，合并双方所有更改，**不丢失任何改动**，结束后两端相同。
* **`doveadm sync -1`**：单向同步，保留目标端已有更改，把源端的新更改合并到目标上。

关键在于官方对 `sync -1` 的限定：这种单向合并「目前并不完美」，**应限制使用**。一旦两端都有更改，邮箱会迅速发散。

**官方给出的迁移流程**

文档直接给出了 `sync -1` 的既定用途——迁移场景：**先多次运行 `backup`，在切换投递之后再跑一次 `sync -1` 传输最后的邮件**。因算法限制，仅建议在 `backup` 或 `sync` 之后的短时间内使用。

把这一句话展开为可执行的迁移节奏，就是：

* **预同步阶段**：在业务不中断的前提下反复执行 `doveadm backup`，每一轮都以源为准、把目标刷成源的镜像。由于 backup 会回滚目标端改动，这个阶段绝不能让用户在目标端产生任何操作。
* **切换阶段**：把新邮件投递指向新系统。这是唯一的时间敏感点，其前后的窗口应尽可能短。
* **收尾阶段**：切换完成后执行**一次** `doveadm sync -1`，把源端在切换窗口内残留的最后变更合并过来，同时保留用户已经在新系统上产生的操作。

需要强调「一次」：把 `sync -1` 当作常态化同步手段循环执行，恰恰是官方警告要避免的用法。

**必须理解的选项与目标语法**

**同步深度**：默认是「快速同步」，只查看元数据；`-f` 执行**全量同步**，扫描所有邮件，慢但最可靠；`-s` 为状态同步。官方指出快速同步存在一个真实局限——若两端恰好修改了相同数量的邮件，NEXTUID/HIGHESTMODSEQ 可能相同但改动内容不同，从而漏同步；此时需改用 `-f` 或 `-s`。**迁移的最后一轮校验建议用 `-f`。**

**范围控制**：`-n` *namespace* 只同步指定命名空间（可多次给出），`-N` 同步所有命名空间，`-m` *mailbox* 只同步指定邮箱，`-x` 排除；`-u` *user/mask* 支持 `*` 与 `?` 通配（如 `-u *@example.org`），`-A` 对所有用户执行——与 `userdb { driver = passwd }` 组合时不推荐，会包含 UID 低于 `first_valid_uid` 的系统用户。`-R` 反向同步：默认是从本地推到远程，加 `-R` 改为从远程拉到本地。

**目标（destination）语法**：`mail_driver:mail_path` 指本地存储（如 `maildir:~/Maildir`）；`remote:login@host` 通过 `dsync_remote_cmd`（通常是 ssh）连远程；`remoteprefix:login@host` 同上但会先发送 `user@domain\n` 供包装脚本读取；`tcp:host[:port]` 连远程 doveadm 服务（默认端口由 `doveadm_port` 决定）；`tcps:host[:port]` 为其 SSL 版本；也可直接给出本地命令，其 stdin/stdout 接到 dsync 服务。

```
doveadm sync -u username@example.com remote:server-replica.example.com
```

**安全红线与结果判读**

**安全警告（官方 SECURITY 节）**：该命令**不能安全地交给不可信用户使用**，除非输入被严格过滤。原因有三：destination 参数允许运行任意命令；使用 `dsync_remote_cmd` 时，用户名或主机名中含空格、或以 `-` 开头，可注入 ssh 参数；由于 ssh 经过 shell，含 `;` 或 `&&` 的内容可造成多命令执行。在迁移自动化脚本中把用户名直接拼进命令行，是最容易踩的坑——必须对用户名做白名单校验。

**退出状态 2**：表示同步过程无报错，但部分更改未被应用（例如新邮箱的修改序列、同步过程中邮箱又发生变动）。官方说明再跑一次通常即可修复。迁移脚本应把退出码 2 当作「需重试」而非「失败」，并把重试次数与最终状态纳入迁移报表。

**跨架构迁移**：索引文件按 CPU 字节序存储，官方明确指出——如果确实需要在小端与大端 CPU 之间迁移，应当**用 dsync 迁移邮件**，而不是搬运索引文件。这也是大规模迁移中优先选择 dsync 而非文件系统层面拷贝的重要理由之一。

参考：Dovecot 官方文档 [doveadm-sync(1)](https://doc.dovecot.org/latest/core/man/doveadm-sync.1.html)；索引跨架构迁移参见 [Mail Index File Format](https://doc.dovecot.org/2.4.4/developers/design/indexes/index_format.html)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/imap-mass-migration-doveadm-sync.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
