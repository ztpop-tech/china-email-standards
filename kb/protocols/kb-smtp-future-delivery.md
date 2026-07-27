---
title: "SMTP 未来投递机制：RFC 1326 / RFC 2822 延迟投递深度解析"
source: "https://ztpop.net/kb/kb-smtp-future-delivery.html"
license: CC-BY 4.0
---

# SMTP 未来投递机制：RFC 1326 / RFC 2822 延迟投递深度解析

## 概述

邮件系统的"定时发送"（Scheduled Send / Future Delivery）需求由来已久——用户希望在指定未来时间点投递邮件，而非立即发出。然而，SMTP 协议在设计时就未将"未来投递时间"作为一等公民纳入协议规范。这一缺位导致延迟投递的实现必须依赖 MUA-MTA 之间的应用层约定和 MTA 的队列控制能力。

## 概念与标准

### RFC 1326 — Future Message Support (1992, Experimental)

RFC 1326 是 IETF 最早尝试标准化"未来消息支持"的实验性文档[1]。它提出了 SMTP 扩展命令 `SCHEDULE`，允许 MUA 在 SMTP 会话中指定一个投递时间。接收 MTA 收到 SCHEDULE 后，在指定时间到达后才将邮件放入投递队列。SCHEDULE 命令的语法定义如下：

```
C: SCHEDULE 19920503120000 +0800
C: MAIL FROM:<sender@example.com>
C: RCPT TO:<recipient@example.com>
C: DATA
```

时间戳格式为 `YYYYMMDDHHMMSS` 后跟时区偏移。该提案最终停留在 Experimental 状态，从未进入 Standards Track——主要原因是增加了 SMTP 会话状态的复杂性，且 MTA 需维护大量定时器。目前没有主流 MTA 实现 SCHEDULE 扩展。

### RFC 2822 §3.6.4 — Message-ID 与 Date 的时间语义

RFC 2822 [2] 定义了邮件消息头中 `Date:` 和 `Message-ID:` 字段的语义。其中 `Date:` 字段标识"邮件创建时间"（creation timestamp），`Message-ID:` 是全局唯一标识符，通常包含时间戳成分以确保唯一性。这两个时间戳仅表示邮件创建时刻。

```
Date: Fri, 24 Jul 2026 12:00:00 +0800
Message-ID: <20260724120000.A1B2C3@mail.example.com>
```

关键点在于：RFC 2822 明确 Date 字段不携带"预期投递时间"语义。任何试图在 Date 中编码未来时间的做法都是对协议的误解——MTA 和接收端不应基于 Date 字段延迟或优先投递。

### RFC 5321 §4.5 — MTA 队列控制与投递尝试间隔

RFC 5321 §4.5 [3] 规定了 MTA 对暂时投递失败邮件（4xx）的队列管理要求。MTA 必须将邮件放入 deferred 队列并在后续重试。重试间隔应遵循指数退避策略，最短间隔 ≥ 30 分钟。MTA 的 deferred 队列是实现延迟投递的天然机制——通过将邮件标记为"暂缓直到指定时间"，可以模拟未来投递。

## 原理与实现

### 架构模式：MUA 寄信 → MTA 持有 → 定时释放

由于 SMTP 没有原生的"定时发送"命令，实际的延迟投递系统采用分层架构：

1. **MUA 层**：用户在邮件客户端中选择延迟投递时间，MUA 将邮件提交到 MSA 或邮件存储（IMAP Drafts/Scheduled 文件夹），不在 SMTP 会话中传递"未来时间"信息
2. **后端存储层**：MUA 或邮件服务器将邮件保存到存储后端，附带计划投递元数据（X-ZTpop-Scheduled-Delivery 等自定义头）
3. **调度器层**：独立的定时调度进程在计划时间到达后将邮件从存储中取出并提交给 MTA
4. **MTA 层**：Postfix 等 MTA 提供有限的原生支持（future\_delivery），或通过 hold queue + manual release 实现

### Message-ID 中的时间戳：标识 vs 语义

Message-ID 常见的格式为 `left-part@domain`，其中 left-part 通常包含时间戳以确保唯一性。许多 MUA（如 Outlook、Thunderbird）的 Message-ID 生成器中使用了 `pid.counter.YYYYMMDDHHMMSS` 格式。但这纯粹是标识符生成约定，不是协议语义。接收端绝不应从 Message-ID 中提取投递时间信息。RFC 5322 §3.6.4 明确 Message-ID 的语义限定为"标识特定消息的唯一消息 ID"[4]。

## Postfix 延迟投递实践

### 方案 A：hold queue + 定时释放

Postfix 的 `hold` 命令可将队列中的邮件临时冻结。结合 cron 定时任务可实现最基本的延迟投递功能：

```
# 1. 正常提交邮件到 Postfix
# 2. 立即将所有符合条件的邮件 hold 住
postsuper -h ALL deferred

# 3. 在计划投递时间释放
#    /etc/cron.d/scheduled-release
# 0 9 * * * root postsuper -r ALL && postqueue -f

# 4. 或者用条件筛选释放（需配合内容过滤）
# 只释放含有特定 X-Header 的邮件
# 使用 content_filter + 自定义 filter 实现
postcat -q QUEUE_ID | grep -q "X-Scheduled-Delivery" && postsuper -r QUEUE_ID
```

注：粗粒度的 `postsuper -h ALL` 会影响正常邮件，生产环境应通过 content\_filter 或外部调度器实现精确控制。

### 方案 B：Postfix future\_delivery 配置

Postfix 从 3.x 开始通过 `future_delivery` 配置参数提供有限的延迟投递支持。当启用时，Postfix 在 DNS MX 查询后缓存路由信息但不立即建立连接，在计划时间到达后才发起投递。

```
# /etc/postfix/main.cf
# 启用未来投递（默认 off）
future_delivery = yes

# 设置最大未来投递窗口（默认 60 分钟）
future_delivery_window = 3600

# 结合 transport_maps 对特定域启用
# transport_maps = hash:/etc/postfix/transport
# example.com smtp:[mx.example.com]:25 delay=1800
```

```
# 发送未来投递邮件的示例
# 使用 envelope 中的 Delay 参数（需 MUA 支持）
sendmail -f sender@example.com \
  -xdelay=3600 \
  recipient@example.com
```

Postfix 的 future\_delivery 实现有显著限制：

* 最大延迟窗口受 `future_delivery_window` 限制（默认 1 小时）
* 不支持超过一天的长时间延迟
* 重启后状态丢失（不持久化到队列文件）

### 方案 C：外部调度器（推荐架构）

对于生产环境，推荐将延迟投递逻辑完全外移到调度器层：

```
# Python 调度器示例（基于 Redis + Postfix）
# scheduled_mail.py
# 将邮件元数据存入 Redis Sorted Set (score = 投递时间戳)
# 定时扫描到期邮件，通过 sendmail 提交给 Postfix

# Redis 数据结构
# ZADD scheduled:delivery 1721812800 "sender|recipient|body_path"

# 定时调度调用
# */1 * * * * python3 /usr/local/bin/scheduled_mail_deliver.py

# 到期投递逻辑
# import redis, subprocess
# r = redis.Redis()
# now = int(time.time())
# for item in r.zrangebyscore("scheduled:delivery", 0, now):
#     sender, recipient, body = item.split("|", 2)
#     subprocess.run(["sendmail", "-f", sender, recipient], input=body)
# r.zremrangebyscore("scheduled:delivery", 0, now)
```

## 实际限制与注意事项

| 限制维度 | 说明 |
| --- | --- |
| 协议级别 | SMTP 无原生延迟投递命令，RFC 1326 SCHEDULE 停留在 Experimental |
| 时间精度 | Postfix future\_delivery 精度约分钟级，外部调度器可达秒级 |
| 持久化 | Postfix 原生 future\_delivery 重启丢失，建议外部调度 + 持久化存储 |
| 时区处理 | Date header 中的时区偏移不代表投递时间，调度器需统一使用 UTC 时间戳 |
| 队列优先级 | 延迟投递邮件不应与高优先级邮件混用同一队列，建议独立的 transport |

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/kb-smtp-future-delivery.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
