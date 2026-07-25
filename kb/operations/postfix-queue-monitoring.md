---
title: "Postfix 队列监控与管理：qshape/mailq/postsuper 详解"
source: "https://ztpop.net/kb/postfix-queue-monitoring.html"
license: CC-BY 4.0
---

# Postfix 队列监控与管理：qshape/mailq/postsuper 详解

## 概述

Postfix 邮件队列是一个分层目录结构，位于 /var/spool/postfix/ 下。队列分为 active、incoming、deferred、hold、corrupt 等子目录。邮件的队列生命周期从 incoming 开始，经 cleanup 守护进程处理后被移入 active 等待立即投递；若投递失败则移入 deferred 排队重试。hold 队列存储管理员手动挂起的邮件，corrupt 队列存放解析异常的损坏邮件，每个队列目录下的文件以哈希散列分布避免单目录文件数过多。

## qshape 队列分布可视化

qshape 是 Postfix 内置的命令行队列分析工具，按邮件在队列中的停留时长将各队列邮件计数分桶统计。输出按活跃队列、延迟队列分列显示，每一行为一个发送域，按邮件数量降序排列。时间桶分为 5、10、20、40、80、160、320、640 分钟以上几档，运维人员可快速识别出哪些目标域导致了大量邮件积压。

```
# qshape 基本分析
qshape deferred | head -20
qshape -s hold
qshape active incoming

# 队列深度计数
find /var/spool/postfix/deferred -type f | wc -l
find /var/spool/postfix/active -type f | wc -l

# mailq 快速查看队列概要
mailq | tail -1
postqueue -p | grep -c "^[A-F0-9]"
```

## postsuper 队列维护操作

postsuper 是 Postfix 队列文件的维护工具，可在不停止 Postfix 的情况下对队列中的邮件执行删除、挂起、释放和重新排队操作。删除操作支持按队列 ID 或按发件人/收件人地址匹配批量清理。重新排队（requeue）可将 deferred 队列中的邮件移回 incoming 重新处理，适用于修复配置错误后恢复积压邮件的场景。

```
# 删除特定队列ID的邮件
postsuper -d 3fB8xZ6YKWz1JqD

# 批量删除发往特定域的所有邮件
mailq | tail +2 | grep -v "^ *(" | awk 'BEGIN { RS = "" } /@example\.com/ { print $1 }' | tr -d "*!" | postsuper -d -

# 删除所有 deferred 队列邮件
postsuper -d ALL deferred

# 挂起/释放邮件
postsuper -h 3fB8xZ6YKWz1JqD
postsuper -H 3fB8xZ6YKWz1JqD

# 强制重试所有排队的邮件
postqueue -f
postqueue -s example.com
```

## 踩坑与排错

高并发环境下 incoming 队列快速膨胀会导致磁盘 I/O 瓶颈，可在 master.cf 中增加 cleanup 进程数来提升邮件解析吞吐。deferred 队列中大量老旧邮件堆积时，qshape 命令本身可能因遍历大量文件而执行缓慢（超过 30 秒），可通过设置 maximal\_queue\_lifetime = 3d 限制退信前最长保留时间。切勿直接删除队列目录下的文件而不经 postsuper 操作，否则会破坏队列文件索引导致 Postfix 状态不一致。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/postfix-queue-monitoring.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
