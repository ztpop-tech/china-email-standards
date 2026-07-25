---
title: "SMTP 吞吐压测：smtp-source 与 MTA 并发调优"
source: "https://ztpop.net/kb/smtp-benchmark-testing.html"
license: CC-BY 4.0
---

# SMTP 吞吐压测：smtp-source 与 MTA 并发调优

## 概述

SMTP 吞吐压测是邮件系统容量规划的核心环节。Postfix 内置的 smtp-source 工具可从单个节点发起数千封测试邮件的并发投递，模拟真实邮件流量场景。压测目标是通过调节并发连接数（-c）、并行会话数（-s）和投递总数（-m），找出 MTA 在当前硬件配置下的最大稳定投递速率。关键观测指标包括 smtpd 进程 CPU 占用率、队列放入速率、磁盘 I/O 等待时间和网络带宽利用率。

## smtp-source 压测方法

smtp-source 通过 SMTP 协议与目标 MTA 直接通信，不经过队列。每封邮件按参数配置源地址、目标地址、邮件大小和正文内容生成。测试前需准备真实域名以避免 DNS 查询成为瓶颈，同时在目标服务器上预先停止垃圾过滤以消除检查逻辑对测试结果的干扰。标准压测流程分三个阶段：单连接基准、并发爬坡和吞吐天花板探索。

```
# 基本吞吐测试（1000封 10KB 邮件 50并发）
smtp-source -s 50 -c 10 -m 1000 -l 10240 \
  -f sender@test.local -t rcpt@test.local localhost:25

# 高并发压力测试（10000封 1KB 邮件 100并发）
smtp-source -s 50 -c 100 -m 10000 -l 1024 \
  -d -M "stress-test" localhost:25

# 期间服务端监控
watch -n 1 'mailq | tail -1; ss -tn state established | grep :25 | wc -l'
sar -n DEV 1 30
iostat -x 1 30
```

## master.cf 并发调优

Postfix master.cf 中 smtpd 进程的 maxproc 参数决定了可同时处理的 SMTP 入站连接数上限。默认值通常为 100，在高并发压测场景下需要根据服务器 CPU 核心数和内存容量上调。同时需要增大内核参数 net.core.somaxconn 和 net.ipv4.tcp\_max\_syn\_backlog 以容纳更多待处理 TCP 连接。

```
# /etc/postfix/master.cf 中的 smtpd 行调整
# smtp      inet  n       -       n       -       300     smtpd

# 内核网络调优（临时）
sysctl -w net.core.somaxconn=4096
sysctl -w net.ipv4.tcp_max_syn_backlog=8192
sysctl -w net.ipv4.tcp_tw_reuse=1

# 监控 smtpd 活动进程数
top -bn1 | grep smtpd | wc -l
```

## 踩坑与排错

压测时邮件路由到真实域名会导致 DNS 查询成为瓶颈——应将测试收件域指向本地或使用 transport\_maps 硬编码投递路径。压测后需清理 deferred 队列中因测试域名无法投递而堆积的邮件，否则会影响后续正常邮件的投递。smtp-source 的 -d 参数启用详细输出后可实时显示吞吐速率，帮助确认性能在哪个并发台阶开始下降。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/smtp-benchmark-testing.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
