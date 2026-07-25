---
title: "邮件递送速度控制 — Outbound Queue 管理与 Backoff 算法深度实践"
source: "https://ztpop.net/kb/email-delivery-rate-control.html"
license: CC-BY 4.0
---

# 邮件递送速度控制 — Outbound Queue 管理与 Backoff 算法深度实践

## 1. 递送速度的定义与度量

邮件递送速度可以从三个维度度量：

* **交付吞吐量（Delivery Throughput）** — 单位时间内成功送达的邮件数，通常以 封/秒（mps）或 封/小时（mph）计
* **并发连接数（Concurrent Connections）** — 到同一目标域的活跃 SMTP 连接数；Postfix 通过 `default_destination_concurrency_limit` 和每个目标域的传输映射来控制
* **重试速率（Retry Rate）** — deferred 队列中邮件的回访频率，由 `queue_run_delay` 和 backoff 参数决定

大部分大型邮箱提供商（Google、Microsoft 365）会对每个发送源 IP 施加隐性速率上限。Google 的指南建议每 IP 的并发连接不超过 10〜20、每连接不超过 100 封/10 分钟 [2]。超出此阈值的邮件将被延迟（451 4.7.650）或直接拒绝。

## 2. Postfix 出站队列节流参数体系

### 2.1 核心出站参数

```
# /etc/postfix/main.cf — 出站队列管理核心参数

# 默认目标域并发连接上限（默认 20）
default_destination_concurrency_limit = 20

# 单次连接的最大收件人数（按收件人分批投递）
default_destination_recipient_limit = 50

# 到同一域的最大递送尝试速率（Postfix 3.7+）
default_destination_rate_delay = 0s

# 队列扫描间隔（默认 1000s，约 16 分钟）
queue_run_delay = 1000s

# 最小回退间隔（默认 300s）
minimal_backoff_time = 300s

# 最大回退间隔（默认 4000s）
maximal_backoff_time = 4000s

# 出站连接缓存时长（复用 TCP/SSL，默认 2s）
smtp_connection_cache_time_limit = 2s

# 单次 SMTP 会话超时
smtp_connection_reuse_time_limit = 300s
```

### 2.2 基于目标域的差异化节流

不同的目标域对递送速率有完全不同的容忍度。Google 的 MX 可容忍较高的并发，但 Microsoft 365 的大多数 IP 有隐性速率门槛。

```
# /etc/postfix/transport — 按目标域的差异化速率控制
# 格式：domain transport:nexthop:concurrency_limit:recipient_limit:rate_delay

# Google Workspace/Google Mail — 较高并发
gmail.com                   smtp:[gmail-smtp-in.l.google.com]:25:10:100
google.com                  smtp:[gmail-smtp-in.l.google.com]:25:10:100

# Microsoft 365/Exchange Online — 降低并发，防止 451 4.7.650
outlook.com                 smtp:[mx1.hotmail.com]:25:5:25:rate_delay=2s
hotmail.com                 smtp:[mx1.hotmail.com]:25:5:25:rate_delay=2s
office365.com               smtp:[mx*.mail.protection.outlook.com]:25:5:25:rate_delay=2s

# QQ 邮箱 — 中等
qq.com                      smtp:[mx1.qq.com]:25:8:30
foxmail.com                 smtp:[mx1.qq.com]:25:8:30

# 163/126 邮箱
163.com                     smtp:[163mx01.mxmail.netease.com]:25:6:20
126.com                     smtp:[126mx02.mxmail.netease.com]:25:6:20

# 内部系统域 — 高并发
myinternal-corp.com         smtp:[10.0.0.5]:25:50:200:rate_delay=0s

# 低优先级域（邮件列表、非关键服务使用较低并发）
bulk-newsletter-domain.com  smtp:[mx.example.com]:25:3:10:rate_delay=5s
```

上述配置生效需要启用：

```
transport_maps = hash:/etc/postfix/transport
```

## 3. Retry Backoff 算法

### 3.1 RFC 5321 §4.5.4 的 retry 规范

RFC 5321 §4.5.4 对重试行为给出了明确的工程约束 [1]：

* MUST 在首次失败后保留邮件至少 30 分钟
* SHOULD 在 4-6 小时内至少进行一次重试
* MUST 在 4-5 天后仍无法投递时生成退信（DSN 5.x.x）
* MUST 使用指数退避（exponential backoff）而非固定间隔

RFC 5321 同时指出，重试间隔应包含随机抖动（jitter），以避免多个队列在整点时间同步重试导致的"雷鸣群"（thundering herd）效应 [1, §4.5.4.1]。

### 3.2 指数退避的数学形式

Postfix 使用以下算法确定第 n 次重试的等待时间：

```
wait_n = min(maximal_backoff_time,
             minimal_backoff_time × 2^(n-1) + random(0, minimal_backoff_time × 0.5))
```

其中 n≥1 表示连续失败的次数。使用默认参数（min=300s, max=4000s）的退避轨迹如下：

表2：Postfix 默认退避序列

| 尝试次数 | 等待时间 | 累计耗时 | 说明 |
| 1 | ~300s | 5min | 首次失败立即回访 |
| 2 | ~600s | 15min | 双倍退避 |
| 3 | ~1200s | 35min | 适合跨越灰名单窗口 |
| 4 | ~2400s | 75min | 约 1 小时 |
| 5 | ~4000s | ~2.5h | 达到上限 |
| 6+ | ~4000s | 每 ~66 分钟 | 上限持平 |

### 3.3 针对特定错误的差异化退避

通过 transport\_maps 可对接收特定回复码的域使用更短或更长的退避：

```
# 对 Exchange Online 实施更长的退避
# transport 中通过 transport 参数覆盖退避
outlook.com    smtp:[mx1.hotmail.com]:25
   :minimal_backoff=1800
   :maximal_backoff=7200
```

但在标准 Postfix transport(5) 格式中，逐域覆盖 backoff 需要定制 policy daemon。更实用的方案是使用 postfix-policyd-spf-python 或 self-developed post-queue policy filter：

```
# 脚本方式：分析 mail.log 中的 deferred 记录
# 对收到大量 451 4.7.650 的域动态增加 delay
$ qshape deferred | awk '$1 ~ /outlook|hotmail|office365/ {print}'
$ grep "451 4.7.650" /var/log/mail.log | \
    awk '{print $NF}' | sort | uniq -c | sort -rn
```

## 4. Burst Traffic 背压处理

### 4.1 Burst 的定义与识别

Burst（突发流量）指出站在短时间内产生的远超平均水平的邮件量。典型场景：系统通知（超 70% 的 burst 来自自动化系统）、营销邮件批量推送、账号被入侵后的批量外发、大量退信循环。

识别 burst 的关键指标：

```
# qshape 输出的 deferred 队列
$ qshape deferred | head -25

# postqueue -p 的总数
$ postqueue -p | tail -1
-- 123456 Kbytes in 12345 Requests.

# 历史基线对比
$ cat /var/log/mail.log | grep "status=sent" | \
    awk -F' ' '{print $1,$2,$3}' | \
    awk -F: '{print $3}' | sort | uniq -c | tail -10
```

当 5 分钟内的出站量超过平均值的 3 倍标准差时，应触发背压机制。

### 4.2 背压策略

1. **自动降速（Auto-throttle）** — 当某个目标域的临时失败率达到阈值（如 ≥30% 的递送尝试返回 4xx），自动降低该域的并发连接和速率
2. **源端限流（Source Throttling）** — 从发件人/SASL 用户角度限制出站速度（与 anvil 不同，这里限制出站而非入站）
3. **水线保护（Watermark Protection）** — 当 deferred 队列大小超过设定阈值时，暂停低优先级递送

```
# 基于 postfix-policyd (cluebringer) 的出站速控
# /etc/policyd/cluebringer.conf
[Postfix Quotas]
# 限制每用户每小时出站量
DefaultQuota = 500/h
Greylist = enabled

# 限制每个域每日出站量
DomainQuota = 50000/d
```

### 4.3 出站队列水线告警

```
# 监控脚本：在 deferred 队列超过阈值时触发自动调优
#!/bin/bash
DEFERRED_COUNT=$(mailq | tail -1 | awk '{print $5}')
THRESHOLD=10000

if [ "$DEFERRED_COUNT" -gt "$THRESHOLD" ]; then
    # 降低默认并发，避免进一步放大问题
    postconf -e default_destination_concurrency_limit=5
    # 发送告警
    echo "Deferred queue $DEFERRED_COUNT > $THRESHOLD, throttled" | \
        mail -s "Queue Alert" admin@example.com
fi
```

## 5. 高级策略：基于成功率反馈的速率调优

### 5.1 成功率积压（Success Rate Feedback）

高级邮件系统在出站调度器中嵌入了成功率反馈环路。基本原理：

```
吞吐量 = 基准并发 × 成功率因子

成功率因子 = 成功投递数 / 总尝试数（窗口内）

当成功率 < 0.7 时，因子开始线性衰减
当成功率 < 0.3 时，因子归零 → 暂停该目标的递送
```

### 5.2 Postfix 内置的速率反馈

Postfix 3.7+ 引入了 `default_destination_rate_delay` 参数（替代早期的 `smtp_destination_rate_delay`），使管理员可为每个目标域配置延迟 [3]：

```
# 全局出站速率延迟
default_destination_rate_delay = 1s

# 按目标域覆盖
# /etc/postfix/transport:
newsletter.com smtp:[mx.newsletter.com]:25:rate_delay=5s
```

`rate_delay` 的工作原理是：Postfix 在连续发送两封邮件到同一域之间等待指定时长。此机制在每个传输进程中独立生效，因此实际平滑后的速率上限为：

```
实际速率 ≈ concurrency_limit / rate_delay
```

例如 `concurrency_limit=10, rate_delay=1s` → 理论上限每秒约 10 封。

## 6. 监控与调优工具

### 6.1 队列延迟监控

```
$ qshape inactive       # 查看 inactive 队列延迟分布
$ qshape deferred | sort -k2 -rn | head -10   # 输出 deferred 排名前 10 的目标域
$ mailq | grep -c "^[A-F0-9]"     # deferred 队列总数

# 获取延迟队列中每封邮件的 last_attempt_age
$ postqueue -j | python3 -c "
import sys,json
for line in sys.stdin:
    try:
        entry = json.loads(line)
        if entry['queue_name']=='deferred':
            age = entry.get('arrival_time',0)
            last = entry.get('last_attempt_time',0)
            print(f\"{entry['queue_id']} age={age} last={last}\")
    except: pass"
```

### 6.2 速率异常的根因定位

```
# 提取目标域临时失败集中的日志
$ grep "status=deferred" /var/log/mail.log | \
    grep -oP "to=<[^>]+@\K[^>]+" | sort | uniq -c | sort -rn | head -20

# 检查该域的增强状态码分布
$ grep "status=deferred" /var/log/mail.log | \
    grep "to=<.*@problem-domain.com" | \
    grep -oP "dsn=\S+" | sort | uniq -c | sort -rn
```

## 参考文献

1. IETF RFC 5321 §4.5.4 (2008) — Simple Mail Transfer Protocol: Minimum Retry Intervals and Queue Strategies
2. Google Email Sender Guidelines (2024), <https://support.google.com/mail/answer/81126>
3. Postfix Documentation — ADDRESS\_VERIFICATION\_README, <https://www.postfix.org/ADDRESS_VERIFICATION_README.html>
4. Postfix Documentation — transport(5), <https://www.postfix.org/transport.5.html>
5. Postfix Documentation — QSHAPE(1), <https://www.postfix.org/qshape.1.html>
6. IETF RFC 3463 (2003) — Enhanced Mail System Status Codes
7. IETF RFC 2821 §4.5.4 (2001) — Simple Mail Transfer Protocol (predecessor to RFC 5321)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-delivery-rate-control.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
