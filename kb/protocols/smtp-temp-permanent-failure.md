---
title: "SMTP 临时失败与永久失败决策 — 521/541 vs 450/451 的队列管理最佳实践"
source: "https://ztpop.net/kb/smtp-temp-permanent-failure.html"
license: CC-BY 4.0
---

# SMTP 临时失败与永久失败决策 — 521/541 vs 450/451 的队列管理最佳实践

## 1. SMTP 状态码核心语义：4xx vs 5xx 的协议定义

RFC 5321 §4.2.1 规定 SMTP 回复码由三位数字构成 [1]。首位数字决定基本语义：

* **2xx** — 成功（Positive Completion）
* **3xx** — 中间回复（Positive Intermediate），需要后续命令
* **4xx** — 临时失败（Transient Negative Completion），请求未成功，但客户端应重试
* **5xx** — 永久失败（Permanent Negative Completion），请求未成功，且不应重试

这一分类是整个邮件投递系统的基石。发送 MTA 收到 4xx 必须将邮件放入 deferred 队列等待后续重试；收到 5xx 则必须生成退信（bounce）或丢弃。

但现实远非如此简单。RFC 3463 定义的增强状态码（Enhanced Mail System Status Codes）提供了第二位和第三位的细化分类 [2]。实际的失败决策需要结合基础码 + 增强码 + 上下文综合判断。

## 2. 常见临时失败（4xx）的分类决策

### 2.1 450 — 邮箱临时不可用

**含义：** 邮箱因临时原因不可用（如邮箱满、IO 错误、复制延迟）。

**典型场景：**

* `450 4.2.1 Mailbox busy` — 收件人邮箱正在执行大型操作（如索引重建），发送方应等待后重试
* `450 4.2.2 Mailbox full` — 收件人邮箱存储配额已满，但应为 452
* `450 4.7.1 Service unavailable` — 接收 MTA 内部策略拒绝，可重试

**决策：** 无脑重试。Postfix 默认将 450 放入 deferred 队列，按`maximal_backoff_time`（默认 4000s）等策略递增退避。连续 4xx 超过`bounce_queue_lifetime`（默认 5d）后自动退信。

### 2.2 451 — 本地错误导致的临时失败

**含义：** 接收端因自身原因无法处理请求，但希望发送方稍后重试。

**典型场景：**

* `451 4.3.0 Internal server error` — MTA 内部错误（数据库连接中断、磁盘 I/O 超时等）
* `451 4.4.0 Timeout` — 连接下一跳 MTA 时超时
* `451 4.7.650 Exchange Online 速率限制` — Microsoft 365 对高频发件人的临时限流，要求至少 30 分钟后重试
* `451 4.7.1 Greylisting` — 灰名单机制要求首次发送的三元组（发件人 IP、发件人、收件人）在指定时间内重试

**决策：** 应重试，且建议配合指数退避。对于特定场景（如 451 4.7.650），推荐首次退避间隔不低于 30 分钟。Greylisting 场景下首次失败后 5-15 分钟重试即可通过。

### 2.3 452 — 存储配额不足

**含义：** 接收端存储空间不足，无法接收邮件。

**典型场景：**

* `452 4.2.2 Over quota` — 收件人配额已满
* `452 4.3.1 Insufficient system storage` — 磁盘空间不足

**决策：** 应重试，但重试间隔建议大于普通 4xx（1h+），因为存储问题需要人工介入。建议开启`additional_mailbox_quota_threshold` 这类机制在配额达到阈值时提前发送警告而非直接拒绝。

## 3. 常见永久失败（5xx）的分类决策

### 3.1 521 — 服务器不接受任何邮件（特殊 5xx）

**含义：** RFC 5321 §3.3 定义的 521 是一个特殊状态码——接收服务器正式声明自己不为任何域接收邮件 [1]。这一状态码不应出现在正常邮件系统之间，而是用于守护型 MTA（如邮件安全网关的入站端口、蜜罐系统）或已废弃的域名。

**典型场景：**

* `521 5.1.0 This system does not accept mail` — 接收方明确拒绝
* `521 5.1.0 Domain does not accept mail` — 域名不提供邮件接收服务

**决策：** 不重试，直接退信。521 的语义是永久且不可撤销的——接收方明确声明自己不做 MX 服务，重试一千次也不会改变。Postfix 收到 521 后直接将邮件投入 bounce 队列。

### 3.2 541 — 中继拒绝（特殊 5xx）

**含义：** 541 是一个历史上定义的回复码（RFC 821 时代），表示"接收方拒绝为发送方转发"。RFC 5321 已将其置于历史备注中，目前更普遍的是 550 5.7.1 + 增强状态码来标识中继拒绝 [1]。

实际部署中，541 极少出现。如果遇到，应将其视为完整的中继拒绝——不重试、直接退信。

### 3.3 550 — 邮箱不可用

最常见的 5xx 码，但原因五花八门：

表3：550 回复码的常见细分

| 增强码 | 含义 | 退信决策 |
| 5.1.1 | 用户不存在 | 直接退信（不可重试） |
| 5.1.6 | 邮箱已迁移 | 尝试新地址后退信 |
| 5.2.1 | 邮箱禁用/已停止 | 直接退信 |
| 5.5.1 | SMTP 命令语法错误 | 确认发送端无问题后重试 |
| 5.7.1 | 策略拒绝（RBL/SPF/DMARC 等） | **按场景决策**（详见下文） |
| 5.7.26 | TLS 强制要求（MTA-STS） | 配置修正后重试 |

### 3.4 553 — 邮箱名语法错误

发送方邮箱地址格式不合法。例如：`553 5.1.3 From address not accepted`。决策：立即退信，同时修复发件人地址的生成逻辑。

### 3.5 554 — 事务失败（通用代码）

554 是最宽泛的永久失败码，涵盖策略拒绝、内容过滤、反垃圾规则等：

* `554 5.7.1 Message rejected due to content (Rspamd/SA)` — 邮件内容被判定为垃圾
* `554 5.7.9 Message rejected per DMARC policy (p=reject)` — DMARC 认证失败
* `554 5.7.1 Blocked by RBL` — 发送方 IP 在拒绝列表中

**决策：** 对于内容过滤相关的 554，如果发送方有改善信心（如修复认证配置、清除邮件内容中的恶意特征），可尝试重投——但原样发送很可能再次被拒。建议转入人工审核队列而非自动重试。

## 4. 队列管理的 Retry 策略（RFC 5321 §4.5.4.1）

RFC 5321 §4.5.4 对 MTA 的重试行为有明确要求 [1]：

> MUST 在首次失败后至少 30 分钟内保留邮件；SHOULD 在 4-6 小时内至少尝试一次；MUST 在 4-5 天后仍未成功时生成退信。

这与 RFC 5321 §4.5.4.1 的 Minimum Retry Intervals 共同构成了基本的 retry 框架 [1]。Postfix 的实现通过以下参数控制：

```
# /etc/postfix/main.cf
# 队列访问间隔（默认 1000s，约 16 分钟）
queue_run_delay = 1000

# 最小回退时间（初始退避时间，默认 300s）
minimal_backoff_time = 300

# 最大回退时间（最大退避时间，默认 4000s）
maximal_backoff_time = 4000

# 延迟队列生命周期（超过后转为退信，默认 5d）
bounce_queue_lifetime = 5d

# 最大退信计数上限（超过后静默丢弃）
bounce_size_limit = 50000
```

### 4.1 指数退避行为

Postfix 的退避算法遵循 RFC 5321 §4.5.4.1 的指引：每次失败后，实际等待时间介于`minimal_backoff_time`和`maximal_backoff_time`之间，时间随连续失败次数的增加呈指数增长。具体公式为：

```
实际等待时间 = min(maximal_backoff_time, minimal_backoff_time × 2^(failure_count-1) + random_jitter)
```

示例如下：

表4：退避时间示例（minimal=300s, maximal=4000s）

| 连续失败次数 | 理论退避 | 实际退避（含 jitter） | 累计耗时 |
| 1 | 300s | ~300s | 5 min |
| 2 | 600s | ~600s | 15 min |
| 3 | 1200s | ~1200s | 35 min |
| 4 | 2400s | ~2400s | 75 min |
| 5 | 4000s（cap） | ~4000s | ~2.5h |
| 6+ | 4000s（cap） | ~4000s | 每 66 分钟一次 |

### 4.2 针对特定错误码的差异化策略

451 4.7.650（Exchange Online 速率限制）和 452（配额满）应使用更长的退避间隔：

```
# /etc/postfix/main.cf

# 对特定目标域或 IP 段的覆盖
transport_maps = hash:/etc/postfix/transport

# /etc/postfix/transport:
# 对 Exchange Online 域赋予更长的间隔
outlook.com    smtp:[mx1.hotmail.com]:25:minimal_backoff=1800,maximal_backoff=7200
hotmail.com    smtp:[mx1.hotmail.com]:25:minimal_backoff=1800,maximal_backoff=7200
office365.com  smtp:[mx*.mail.protection.outlook.com]:25:minimal_backoff=1800,maximal_backoff=7200

# 对大容量内部系统的覆盖
myinternal.com smtp:[10.0.0.5]:25:minimal_backoff=60,maximal_backoff=600
```

更细粒度的策略可借助 policy server：

```
# 使用 pfixtables 或自建 prescreen 实现基于失败码的策略分发
smtp_reply_filter = maps:/etc/postfix/smtp_reply_filter
```

## 5. 退信阈值决策模型

当一个邮件在 deferred 队列中耗尽生命周期时，Postfix 按以下逻辑决定退信级别：

```
永久失败（5xx）  → 立即退信（DSN 5.x.x）
临时失败（4xx）  → 进入 deferred 队列
  重试 → 上限时间到 → 最后一次尝试
    如果最后尝试仍为 4xx → 生成 DSN 4.x.x 延迟通知 + 退信（DSN 5.x.x）
    如果最后尝试为 5xx → 直接退信（DSN 5.x.x）
```

关键退信阈值参数：

```
# 队列生命周期（默认 5d）
bounce_queue_lifetime = 5d
# 最大退信数量（超出后静默丢弃，防退信风暴）
bounce_size_limit = 50000

# 延迟通知参数
delay_warning_time = 4h
# 注意：Postfix 仅首次延迟和退信时发送通知
```

## 6. 常见决策陷阱

### 6.1 被 450 欺骗的 550

某些接收 MTA 会在负载高时返回 550 而非 450（实现缺陷）。如果邮件确实重要，观测日志模式：

```
$ grep "status=sent" /var/log/mail.log | awk '{print $NF}' | sort | uniq -c | tail -20
$ grep "status=deferred\|status=bounced" /var/log/mail.log | \
    awk '{for(i=1;i<=NF;i++) if($i~/^dsn=/) print $i}' | sort | uniq -c | sort -rn
```

若发现某个目标持续在 450 和 550 之间波动，极可能是接收 MTA 负载敏感的逻辑缺陷。此时不应直接配置退信——建议通过 transport\_maps 设置更长的 minimal\_backoff 并启用 extra 监控。

### 6.2 灰名单与临时失败的循环

如果出站队列中大量邮件返回 450 4.7.1（greylisting），且退避策略过短（如默认 300s），可能在 5 分钟内重试 3 次都撞上灰名单窗口——对方甚至还没进入 relaxed 模式。建议对出现大量灰名单响应的域单独配置更长的退避间隔（≥900s）。

### 6.3 退信风暴防范

当发件人账户被入侵（被利用批量发送），接收 MTA 的 RBL 拦截面会返回大量 550/554，触发退信风暴。Postfix 的`bounce_size_limit`只能限制退信数量的绝对上限，但不能区分正常退信与风暴退信。建议配合以下方案：

* 设置 `maximal_queue_lifetime = 2d`（而非默认 5d）以减少风暴持续窗口
* 使用 qshape 实时监控 deferred 趋势，自动触发告警
* 结合 SASL 认证的用户发送行为基线，检测异常出站模式

## 参考文献

1. IETF RFC 5321 (2008) — Simple Mail Transfer Protocol, §4.2.1, §4.5.4, §4.5.4.1
2. IETF RFC 3463 (2003) — Enhanced Mail System Status Codes
3. IETF RFC 3462 (2003) — The Multipart/Report Content Type for the Reporting of Mail System Administrative Messages
4. IETF RFC 6409 (2011) — Message Submission for Mail
5. Postfix Documentation — QSHAPE(1), <https://www.postfix.org/qshape.1.html>
6. Postfix Documentation — bounce(5), <https://www.postfix.org/bounce.5.html>

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/smtp-temp-permanent-failure.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
