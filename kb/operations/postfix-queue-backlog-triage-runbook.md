---
title: "Postfix 邮件队列积压时，如何按官方方法逐级定位瓶颈？"
source: "https://ztpop.net/kb/postfix-queue-backlog-triage-runbook.html"
license: CC-BY 4.0
---

# Postfix 邮件队列积压时，如何按官方方法逐级定位瓶颈？

1
Postfix 邮件队列积压时，如何按官方方法逐级定位瓶颈？
▼

**先分清是哪一个队列在涨**

Postfix 的队列不是一个目录，而是五个语义完全不同的阶段：`maildrop` 存放经本地 `sendmail(1)` 提交、尚未被 `pickup(8)` 收入主队列的邮件；`incoming` 存放已由 `cleanup(8)` 写入主队列的新邮件；`active` 是队列管理器正在调度投递的邮件；`deferred` 存放遭遇暂时性失败、等待重试的邮件；`hold` 存放被访问策略或头/体检查扣下的邮件，不会周期性重试。

官方文档特别强调一个容易被误解的事实：**`active` 队列本质上是队列管理器进程内的内存数据结构**，而 `maildrop`、`hold`、`incoming`、`deferred` 不占用队列管理器内存。因此排障的第一步不是「清队列」，而是判断增长发生在哪一段——不同队列增长指向的根因完全不同，处置手段也不通用。

**五种积压各自对应的根因**

* **maildrop 涨**：本地提交速率过高，或 `cleanup(8)` CPU 开销过大（例如 `body_checks` 正则过重）。注意 `pickup(8)` 是单线程、一次处理一封。本地提交量异常升高，常见成因是转发环路或某个通知程序失控。
* **incoming 涨**：入站速率高于队列管理器的导入速率，主因通常是磁盘 I/O 或 `trivial-rewrite(8)` 查询变慢。Postfix 提供 `in_flow_delay` 用于在 `active` 队列吃紧时对新建队列文件做限流。
* **active 涨**：目标端「排空」速度低于输入速度。此时应检查 `smtp` / `relay` 传输通道的进程限制是否已被打满。
* **deferred 涨**：大量收件人遭遇暂时性失败。官方文档指出的一个高频成因是——未在 SMTP 阶段做收件人验证，字典攻击产生的退信把队列堵死；对应的防线是配置 `local_recipient_maps` 与 `relay_recipient_maps`。
* **hold 涨**：与性能关系不大，更多用于追踪垃圾邮件与恶意软件。

关于容量上限，官方给出的经验区间是：`deferred` 队列在约 10 万到 100 万封的规模上仍可保持良好性能；`active` 队列的消息数上限由 `qmgr_message_active_limit` 控制，默认 20000，达到上限后队列管理器会停止扫描 `incoming` 与 `deferred`；使用 `oqmgr(8)` 时还有 `qmgr_message_recipient_limit` 限制 `active` 队列中的收件人地址总数，默认同为 20000。

**用 qshape 做「域 × 年龄」二维定位**

`qshape(1)` 随 Postfix 源码的 auxiliary 目录分发，它把队列内容渲染成一张表：纵轴是目标域（加 `-s` 则改为发件域），横轴是邮件在队列中的停留年龄，新邮件粒度细、旧邮件按几何级数变粗（分钟桶依次为 5、10、20、40、80、160、320、640、1280 与 1280 以上）；`T` 列为该域总计，`TOTAL` 行为全部域合计。不带参数时默认统计 `incoming` 与 `active` 的并集，也可显式指定队列：

```
qshape
qshape deferred | head
qshape incoming active deferred
qshape -s active
```

判读要领：**问题域会浮到表格的左上角**。若某个目标域在各年龄桶中普遍堆积且旧桶持续增长，说明该目标已经 down 或严重变慢；若发件域侧（`-s`）出现异常集中，则更可能是本域内某账号被盗或某个应用在批量外发。官方还建议：向邮件列表求助时，附上 `qshape(1)` 输出的前 10 至 20 行。

**处置手段与三条纪律**

查看队列用 `mailq(1)` 或 `postqueue(1)`（非特权用户使用后者）；执行性操作用仅限超级用户的 `postsuper(1)`：`-d` 删除指定队列 ID 的邮件，`-h` 将邮件移入 `hold`，`-H` 把 `hold` 中的邮件释放到 `deferred`，`-r` 把邮件重新投入 `maildrop` 以重新排队（会重新经历地址重写与 `content_filter`，但不再经过 milter），`-s` 做结构检查与修复、`-p` 清理崩溃残留的临时文件（这两项先于其他选项执行）。批量操作时 `ALL` **必须大写**，这是官方设计的安全措施。

官方明确的三条纪律值得反复强调：

* **不要盲目提高重试频率或频繁 flush 队列**。文档直言这样做「反而更差」，因为它会使 `active` 队列饱和、把投递代理占满。相关参数为 `queue_run_delay`（默认 300 秒，2.4 之前为 1000 秒）、`minimal_backoff_time`（默认 300 秒）、`maximal_backoff_time`（默认 4000 秒）、`maximal_queue_lifetime` 与 `bounce_queue_lifetime`（默认均为 5 天）。
* **频繁 defer 时先修问题，而不是加大尝试力度**；若根因不可控，用 `fallback_relay` 把问题目标的邮件隔离到专用机器，避免其拖累正常投递，并可为该传输通道单独下调超时、调整并发。
* **使用 `-d` 与 `-r` 时注意队列 ID 复用风险**。Postfix 2.8 及更早总是复用队列 ID，2.9 及以后在 `enable_long_queue_ids=no` 时同样复用；在 Postfix 正在投递该邮件的瞬间执行命令，存在极小概率误删同 ID 的新邮件。

参考：Postfix 官方文档 [QSHAPE\_README（Postfix Bottleneck Analysis）](https://www.postfix.org/QSHAPE_README.html)、[TUNING\_README（Postfix Performance Tuning）](https://www.postfix.org/TUNING_README.html)、[postsuper(1)](https://www.postfix.org/postsuper.1.html)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/postfix-queue-backlog-triage-runbook.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
