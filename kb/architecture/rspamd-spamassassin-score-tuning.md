---
title: "Rspamd 与 SpamAssassin 的评分机制有何不同，规则调优应如何进行？"
source: "https://ztpop.net/kb/rspamd-spamassassin-score-tuning.html"
license: CC-BY 4.0
---

# Rspamd 与 SpamAssassin 的评分机制有何不同，规则调优应如何进行？

1
Rspamd 与 SpamAssassin 的评分机制有何不同，规则调优应如何进行？
▼

**Rspamd：动态评分与「按动作决策」原则**

Rspamd 支持**动态评分**——部分符号的分数会乘以一个 0 到 1 的置信因子。官方给出的例子是：Bayes 概率 50% 时约为 0 分，90% 时约 0.95，100% 时为 1.0；Fuzzy 按匹配权重缩放；Phishing 随置信度变化。这解释了一个常被误读的现象：同一条规则命中，不同邮件得分并不相同。

更重要的是官方反复强调的一条原则：**始终用 action（动作）而不是 score（分数）来决定邮件如何处理**。原因是存在「直通动作（passthrough actions）」——某些模块会直接设置动作而绕过评分累加，例如 greylist、ratelimit、antivirus、multimap、force\_actions。这会导致「分数为零却被拒绝」的情形，日志中会以 `forced:` 条目体现。任何按分数阈值做二次判定的下游集成（网关联动、报表、隔离系统），都应改为读取 action。

另有两个影响判读的机制：**提前拒绝**——邮件一旦达到 reject 阈值，部分检查会停止以节省资源，因此复盘时看到的符号集可能不完整；**超时**——异步规则可能在任务超时前未完成。要强制执行全部检查，可使用 `Pass: all` 头，或用 `rspamc -p` 扫描。

**Rspamd：改阈值与改权重的正确位置**

**动作阈值**写在 `local.d/actions.conf`，官方示例形如：

```
reject = 15;
add_header = 6;
greylist = 4;
```

Rspamd 支持的动作包括：`no action`（放行）、`add header`（加垃圾邮件标头）、`rewrite subject`（改写主题）、`soft reject`（临时拒绝，用于 greylisting 与 ratelimit）、`reject`（永久拒绝）、`quarantine`（转入隔离，需 MTA 配合）、`discard`（静默丢弃）。

**符号权重**写在 `local.d/groups.conf`，或对应分组的专用文件（例如 `local.d/rbl_group.conf`）：

```
symbols {
  "SOME_SYMBOL" {
    weight = 1.0;
  }
}
```

这里有一个极易踩的坑：**WebUI 修改的分数存放在 `$DBDIR/rspamd_dynamic`，其优先级高于配置文件**。如果改了配置却不生效，应先检查该文件——需要编辑或删除它，才能让配置文件中的分数重新生效。

调完之后必须验证：`rspamadm configtest` 校验配置（嵌套错误会在日志与该命令中报告），`rspamadm configdump -g` 查看生效的分组与分数（加 `-j` 输出 JSON 便于程序化比对）。贝叶斯训练用 `rspamc learn_spam` 与 `rspamc learn_ham`。

**SpamAssassin：required\_score 与 score 的四分数形式**

**`required_score n.nn`** 设定判定为垃圾邮件所需的分数，**默认为 5**。官方对这个默认值有一句相当重要的评价：5.0 「相当激进」，适合单用户环境；如果是 ISP 部署，默认值应设得更保守一些，例如 8.0 或 10.0。这是一条常被忽略却直接决定误杀率的建议。

**`score SYMBOLIC_TEST_NAME n.nn [ n.nn n.nn n.nn ]`** 为规则赋分，分值可正可负、可为整数或实数。其精髓在于**四分数形式**——当列出四个分数时，实际使用哪一个取决于 SpamAssassin 的运行方式：

* 第一个：贝叶斯与网络测试**都禁用**（score set 0）。
* 第二个：贝叶斯禁用、网络测试**启用**（score set 1）。
* 第三个：贝叶斯**启用**、网络测试禁用（score set 2）。
* 第四个：贝叶斯与网络测试**都启用**（score set 3）。

这意味着：在一台启用了贝叶斯和 RBL 查询的服务器上调优，只改第一个分数是完全无效的。另有两条必须记住的规则：**把某条规则的分数设为 0 即可禁用该规则**；若配置结束时某测试仍未被赋分，则套用默认值——一般规则为 1.0，而名称以 `T_` 开头的规则（表示处于测试中）为 0.01。

**SpamAssassin：放行名单、自动学习与标头改写**

**放行与阻断名单**：4.x 起采用 `welcomelist_from`、`welcomelist_from_rcvd`、`welcomelist_auth`、`welcomelist_to`、`unwelcomelist_from`、`blocklist_from` 等命名，旧的 `whitelist_*` / `blacklist_*` 可互换使用至 4.1。三者的强度差异是选型关键：`welcomelist_from` 仅匹配发件人地址；`welcomelist_from_rcvd` 在匹配发件人地址之外，**还要求某个中继的 rDNS 名称或 IP 地址也匹配**；`welcomelist_auth` 则会**先验证邮件确由该地址的授权发送者发出**再放行。仅凭 `welcomelist_from` 放行是可被伪造发件人绕过的，涉及重要往来方时应使用后两者。

**贝叶斯自动学习**：`bayes_auto_learn` 默认为 1，即自动把高分邮件（以及低分的非垃圾邮件）喂给学习系统。其阈值的默认实现位于 `Mail::SpamAssassin::Plugin::AutoLearnThreshold` 插件模块。规则级别可用 `tflags autolearn_force` 放宽约束——正常情况下自动学习为垃圾邮件需要**邮件头贡献 3 分且正文贡献 3 分**，该选项把门槛保持在总计 6 分但不再区分分数来源。

**标头改写**：`rewrite_header { subject | from | to } STRING`。默认情况下疑似垃圾邮件的 Subject、From、To 不会被打标；启用后，From/To 会以 RFC 2822 注释形式追加在地址之后（**STRING 中不允许出现圆括号，会被转成方括号**），Subject 则是前置。官方提醒：**只有在 `report_safe` 为 0 时，才应在改写 Subject 时使用 `_REQD_` 与 `_SCORE_` 标签**，否则可能无法通过常规方法移除 SpamAssassin 的标记。若消息原本没有 Subject 头，使用 `rewrite_header subject` 会创建一个；把 STRING 置空则移除已有改写。此外 `subjprefix` 需要先启用 `rewrite_header Subject` 才能工作。

参考：[Rspamd 官方 FAQ](https://rspamd.com/doc/faq.html)；Apache SpamAssassin [Mail::SpamAssassin::Conf 配置文档](https://spamassassin.apache.org/full/4.0.x/doc/Mail_SpamAssassin_Conf.html)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/rspamd-spamassassin-score-tuning.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
