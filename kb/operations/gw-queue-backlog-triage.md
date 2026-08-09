---
title: "邮件队列突然堆积怎么排查？该按什么顺序定位？"
source: "https://ztpop.net/kb/gw-queue-backlog-triage.html"
license: CC-BY 4.0
---

# 邮件队列突然堆积怎么排查？该按什么顺序定位？

**先看堆在哪个队列，含义完全不同**

Postfix 分了几个队列，堆积位置直接指向不同的故障域：`incoming` 堆积说明接收速度超过了 qmgr 的处理能力；`active` 堆积说明正在投递但投递慢；`deferred` 堆积说明投递失败正在等重试；`hold` 是人为挂起；`maildrop` 堆积通常是本地 sendmail 命令提交异常。

多数「队列告警」实际是 deferred 增长，属于投递侧问题；而 incoming 与 active 同时增长才是系统容量问题。两者的处置方向相反，先分清能省掉大量无效排查。

**用 qshape 按域和按年龄切一刀**

QSHAPE\_README 描述的 `qshape deferred` 输出是一张二维表：行是收件域，列是消息在队列中的停留时间分桶。这张表几乎能一眼定性。

判定逻辑：若堆积集中在单个收件域，是对端问题（限流、拒收、不可达）；若分散在大量域上且年龄分桶集中在最近，是本机出口问题（DNS、网络、出口 IP 被封）；若某域的老年龄桶持续增大而新桶正常，说明少量消息卡死，清理这批比调整全局参数更有效。

同样对 `qshape active` 执行一次，可以看出是否有单一域占满了投递槽位，把其他域的邮件挤在后面。

**按发件人切第二刀，识别自循环**

`qshape -s deferred` 按发件人聚合。若某个发件地址贡献了绝大部分堆积，通常是内部系统故障：定时任务重复触发、告警风暴、应用把同一封信反复重投，或是转发环路。

这类问题在网关侧调参数无解，必须在源头停任务。临时止血可用 `postsuper -h` 把该发件人的消息挂起到 hold 队列（保留可恢复性），确认后再 `postsuper -d` 删除或 `-H` 释放。直接删除前务必先 hold，避免误删业务邮件。

**对端限流与 DNS 的区分**

看具体消息的延迟原因：`postqueue -p` 输出中每条消息带有最近一次失败的原因文本，`postcat -q <queueid>` 可查看完整内容与头部。

对端限流的特征是 4xx 应答且文字中含速率或连接数相关描述，此时应降低对该域的并发（Postfix 用 transport 配合 `*_destination_concurrency_limit` 与 `*_destination_rate_delay` 单独限速），而不是提高并发——提高并发只会加剧被限。

DNS 故障的特征是「Host or domain name not found」或「Name service error」，且跨多个域同时出现。先在网关上直接解析验证，再查解析器可用性，不要动队列参数。

**容量型堆积的处置**

若 incoming 与 active 同时增长且投递本身正常，是处理能力不足。可调的方向按优先级：先确认磁盘 I/O 与队列文件系统是否成为瓶颈（队列目录建议独立且使用支持大量小文件的文件系统），再看 `default_process_limit` 与 smtp 客户端进程数是否受限，最后才考虑水平扩容。

Exchange 环境下对应的观测入口是队列查看器与传输服务的队列数据库，判定思路一致：先分队列类型，再按目标域聚合，最后区分是投递侧受阻还是本机资源受限。

**恢复后的收尾**

堆积消除后有两件事必须做：其一，用 `postqueue -f` 主动 flush 前先确认根因已解决，否则会立刻再次堆积并放大对端的限流；其二，检查是否有消息已超过 `maximal_queue_lifetime` 被退信，这批需要单独统计并通知业务方，不能默认「队列清了就没事了」。

参考：[Postfix QSHAPE\_README](https://www.postfix.org/QSHAPE_README.html) ｜ [Postfix postqueue(1) 手册页](https://www.postfix.org/postqueue.1.html) ｜ [Microsoft Learn：Exchange Server 队列](https://learn.microsoft.com/en-us/exchange/mail-flow/queues/queues)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/gw-queue-backlog-triage.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
