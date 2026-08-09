---
title: "退信怎么分类？硬退和软退如何按状态码判定？"
source: "https://ztpop.net/kb/gw-bounce-code-classification.html"
license: CC-BY 4.0
---

# 退信怎么分类？硬退和软退如何按状态码判定？

**判定应基于增强状态码，而非文字描述**

退信正文的措辞由各家 MTA 自定义，不可作为判定依据。RFC 3463 定义的增强状态码是 `class.subject.detail` 三段式：class 为 2 表示成功，4 表示持久性暂时失败（软退），5 表示永久失败（硬退）。这是唯一稳定的机器判定入口。

subject 段给出失败归属：1 为收件人地址问题，2 为邮箱问题（如满、禁用），3 为接收系统问题，4 为网络与路由，5 为协议错误，6 为消息内容与媒体，7 为安全与策略。RFC 7372 又在 7.x 下补充了认证相关的状态码，用于区分因 SPF/DKIM/DMARC 策略导致的拒收。

**从 DSN 报文里取字段**

RFC 3464 规定 DSN 是 `multipart/report; report-type=delivery-status`，其中第二部分 `message/delivery-status` 是结构化的。解析时取 per-recipient 字段：`Final-Recipient`（实际收件人）、`Action`（failed/delayed/delivered）、`Status`（增强状态码）、`Diagnostic-Code`（远端原始应答）。

工程上的顺序是：先看 `Action` 是 failed 还是 delayed；failed 时读 `Status` 首位定硬软；`Diagnostic-Code` 只作人工排查参考，不进入自动判定逻辑。若报文不含 message/delivery-status（部分系统只发纯文本退信），退化为从 `Diagnostic-Code` 文本里正则提取 `[45]\.\d+\.\d+`，取不到则标记为「无法判定」单独归档，不要默认按硬退处理。

**硬退：立即抑制**

class 5 且 subject 为 1（如 `5.1.1` 收件人不存在、`5.1.2` 域名不存在）应当立即把该地址加入抑制列表，不再投递。继续对不存在的地址发送会持续拉低发送信誉，这是发送方最常见的自伤方式。

例外是 `5.7.x` 安全与策略类：它表示「这次被策略拒了」，往往是发送方自身认证配置或内容问题，而非收件人地址无效。这类不应抑制收件人，而应触发发送侧配置告警。把 5.7.1 当成地址失效清理掉，会在策略修复后造成大批可用地址被误删。

**软退：限次重试后转判**

class 4（如 `4.2.2` 邮箱满、`4.3.2` 系统不接收、`4.4.1` 无响应）应进入重试队列。重试策略用指数退避，并设置总时长上限；Postfix 侧对应 `maximal_queue_lifetime` 与 `bounce_queue_lifetime`。

关键判定：连续多个投递周期（例如 7 天内每次投递均软退）后应把该地址转为「软退转硬退」并抑制。长期软退的地址在统计上与无效地址无异，持续重试同样消耗信誉与队列资源。

**分类结果要能回流**

退信分类的价值在于闭环：硬退回流到地址抑制表，5.7.x 回流到认证与策略告警，4.x 集中在单一对端时回流到该对端的连通性排查（可能是对方在限流你）。把这三条回流路径固化成自动流程，退信才从「噪音」变成「投递质量的观测信号」。

参考：[RFC 3463 Enhanced Mail System Status Codes](https://www.rfc-editor.org/rfc/rfc3463.html) ｜ [RFC 3464 An Extensible Message Format for Delivery Status Notifications](https://www.rfc-editor.org/rfc/rfc3464.html) ｜ [RFC 7372 Email Authentication Status Codes](https://www.rfc-editor.org/rfc/rfc7372.html)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/gw-bounce-code-classification.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
