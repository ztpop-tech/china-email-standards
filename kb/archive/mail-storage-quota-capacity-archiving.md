---
title: "邮件系统的存储容量规划与配额、归档策略应如何落地？"
source: "https://ztpop.net/kb/mail-storage-quota-capacity-archiving.html"
license: CC-BY 4.0
---

# 邮件系统的存储容量规划与配额、归档策略应如何落地？

1
邮件系统的存储容量规划与配额、归档策略应如何落地？
▼

**容量规划的三块账，不能只算邮件正文**

邮件系统的磁盘占用由三部分构成，只算其中一部分是容量规划失准的常见原因：

* **邮件存储本身**：由邮箱格式与用户行为决定。
* **索引与缓存**：Dovecot 为每个邮箱维护 `dovecot.index`、`dovecot.index.log`（及轮转出的 `dovecot.index.log.2`）与 `dovecot.index.cache`。其中缓存文件的增长与客户端行为强相关——新的缓存字段会随客户端请求动态加入，因此换一批 IMAP 客户端就可能改变缓存体积。好在它有自净机制：长期未被访问的字段会被整体丢弃；临时字段对保存超过 7 天的邮件可被丢弃；并发写入产生的重复数据会在下次 purge（重建）时清理；已过期消息或缓存续行记录过多时，缓存文件会被重建。规划时应为索引与缓存单独留出余量，而不是把它们并入邮件存储估算。
* **队列**：Postfix 官方给出的经验值是，`deferred` 队列在约 10 万到 100 万封的规模上仍能保持良好性能；`active` 队列默认上限由 `qmgr_message_active_limit` 控制（默认 20000）。队列所在文件系统的容量与 I/O 能力，应按可能出现的最坏积压来预留。

**用 quota\_rule 系列表达分层配额**

Dovecot 的配额规则写在配额 root 之下，**第一条规则必须命名为 `quota_rule`，后续依次为 `quota_rule2`、`quota_rule3`**，数量不限。官方示例展示了三种典型写法：

```
quota_rule  = *:storage=1G
quota_rule2 = Trash:storage=+100M
quota_rule3 = SPAM:ignore
```

三行分别对应容量治理中最常用的三种策略：为全部邮箱设总额、为特定邮箱在总额之外追加额度（`+` 前缀）、把某个邮箱完全排除在配额统计之外（`ignore`）。多命名空间场景下可用 `quota2` 定义第二个配额 root（例如为 Public 命名空间单独计量）。

后端方面，官方文档中出现并给出配置示例的包括 Maildir++ 配额（`quota = maildir:User quota`）与 dict 配额（`quota = dict:...`）；使用 `count` 驱动时需要设置 `quota_vsizes = yes`（v2.2.19 起）。选型应结合存储格式与是否需要集中式配额库来定，本文不对未在官方文档中明确推荐的选项做倾向性断言。

**预警、宽限与超限行为**

**分级预警**：`quota_warning`、`quota_warning2`、`quota_warning3`…… 依次定义多档阈值，触发时执行指定命令（官方示例中通过 `service quota-warning` 定义一个执行脚本的服务，并在其中配置 `executable`、`user` 与 `unix_listener`）。分级的意义在于：单一「已满」告警对用户毫无缓冲，而 80%/95% 两档预警能把清理动作提前到不影响收信之前。

**宽限额度**：`quota_grace` 允许在硬限之上留一小段缓冲（可写成百分比或绝对值）。它解决的是一个真实的边界问题——正好卡在限额上的一封邮件被拒收，用户体验极差且难以自救。

**其他相关设置**：`quota_max_mail_size` 限制单封可保存邮件的大小（v2.2.29 起）；`quota_exceeded_message` 自定义超额提示；`quota_over_flag` 及配套的 `quota_over_flag_value`、`quota_over_flag_lazy_check`、`quota_over_script` 用于把「已超额」状态暴露给外部系统联动；`quota_set` 供管理命令写入配额。

**归档与回收：让存量真正降下来**

配额只能约束增量，存量下降依赖归档与回收：

* **邮箱格式层面的空间回收**：mdbox 依赖 `doveadm purge` 回收已删除邮件占用的空间。**需特别注意：在启用 dsync 复制的部署中，mdbox 的 `doveadm purge` 不会被复制到对端**，两端必须各自安排回收任务，否则副本容量会持续偏离。
* **缓存层面的自动老化**：如前所述，临时缓存字段对保存超过 7 天的邮件可被丢弃，长期不用的字段会被整体丢弃。这部分不需要人工干预，但在做容量趋势分析时应把它作为一个自然回落因素纳入模型，避免误判为异常。
* **迁移式归档**：把冷数据迁到独立存储时，应使用 dsync 迁移邮件而不是搬运索引文件——索引按 CPU 字节序存储，跨异构架构直接拷贝会出问题。
* **配额库的部署约束**：主主复制的两个副本**不能共用同一个配额数据库**，因为两边都会各自更新它。这条约束会直接影响集中式配额方案的可行性，应在架构阶段就确认，而不是等到上线后再改。

参考：Dovecot 官方文档 [Quota Configuration](https://doc.dovecot.org/2.3/configuration_manual/quota/)、[Mail Index File Format](https://doc.dovecot.org/2.4.4/developers/design/indexes/index_format.html)；队列容量参见 Postfix [QSHAPE\_README](https://www.postfix.org/QSHAPE_README.html)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/mail-storage-quota-capacity-archiving.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
