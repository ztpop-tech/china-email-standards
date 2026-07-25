---
title: "Postfix smtpd 全链路限制配置：HELO→SENDER→RECIPIENT→DATA→EOD 解析"
source: "https://ztpop.net/kb/postfix-smtpd-restrictions-guide.html"
license: CC-BY 4.0
---

# Postfix smtpd 全链路限制配置：HELO→SENDER→RECIPIENT→DATA→EOD 解析

## 1. 引言

Postfix 的 smtpd(8) 进程将入站 SMTP 会话拆分为五个可干预的阶段：HELO/EHLO、MAIL FROM、RCPT TO、DATA 和 DATA 结束（End-of-Data）。每个阶段对应一个 `_restrictions` 配置参数，管理员可在各阶段注入检查逻辑——DNSBL 查询、SPF 验证、正则匹配、访问表、自定义策略等[1]。

这五个限制阶段的进入顺序、评估时机和退出行为（REJECT/DEFER\_IF\_REJECT/DEFER/DUNNO/OK/PREPEND/PERMIT/IGNORE）决定了整个邮件接收管道的行为边界。误解或错误排列这些规则是 Postfix 投递问题最常见的根源之一。

## 2. 五大限制阶段概述

| 配置参数 | 触发位置 | 典型检查内容 | 拒绝后果 |
| --- | --- | --- | --- |
| smtpd\_helo\_restrictions | HELO/EHLO 之后 | HELO 域名格式、DNS 解析、黑名单 | 连接在 RCPT 阶段之前被拒，低开销 |
| smtpd\_sender\_restrictions | MAIL FROM 之后 | SPF 验证、发件人域访问表、空发件人策略 | 拒绝发生在发件人声明后 |
| smtpd\_recipient\_restrictions | RCPT TO 之后 | 收件人验证、DNSBL、relay 控制、permit\_mynetworks | 最常用的拒绝阶段，性能敏感 |
| smtpd\_data\_restrictions | DATA 命令后、MIME 内容前 | DATA 命令前的内容检查（头部大小、行数） | 已部分接收对方 MTA 投入 |
| smtpd\_end\_of\_data\_restrictions | DATA 内容接收完成后 | Milter 结果、内容过滤返回值 | MTA 已接收整个邮件，拒绝开销最大 |

## 3. 规则顺序与评估流

Postfix 内置的限制引擎逻辑如下[2]：

1. 先检查 `smtpd_client_restrictions`（客户端地址层面的预先检查，如 RBL）
2. 然后检查 `smtpd_helo_restrictions`
3. `smtpd_sender_restrictions`
4. `smtpd_recipient_restrictions`（最复杂，包含 relay 授权逻辑）
5. （仅如果上述均通过）`smtpd_data_restrictions`
6. `smtpd_end_of_data_restrictions`

需要特别说明：`smtpd_recipient_restrictions` 是 Postfix 中唯一内置了 `PERMIT`/`REJECT` 继电检查逻辑的阶段。如果 `smtpd_recipient_restrictions` 的末尾没有显式 `permit`，Postfix 会自动拒绝所有非本域收件人（即中继拒绝）。其他四个限制阶段在无显式规则时默认通过。

### 3.1 建议的规则编排顺序

```
# main.cf

# ===== 阶段 1: HELO 限制 =====
smtpd_helo_restrictions =
    permit_mynetworks
    permit_sasl_authenticated
    reject_invalid_helo_hostname
    reject_non_fqdn_helo_hostname
    check_helo_access pcre:/etc/postfix/helo_access.pcre
    reject_unknown_helo_hostname
    reject_rhsbl_helo dbl.spamhaus.org

# ===== 阶段 2: 发件人限制 =====
smtpd_sender_restrictions =
    permit_mynetworks
    permit_sasl_authenticated
    reject_non_fqdn_sender
    reject_unknown_sender_domain
    check_sender_access pcre:/etc/postfix/sender_access.pcre

# ===== 阶段 3: 收件人限制（关键阶段）=====
smtpd_recipient_restrictions =
    permit_mynetworks
    permit_sasl_authenticated
    reject_unauth_destination        # 中继控制 — 必须先于 DNSBL
    check_recipient_access pcre:/etc/postfix/recipient_access.pcre
    reject_rbl_client zen.spamhaus.org
    reject_rbl_client bl.spamcop.net
    reject_rhsbl_reverse_client dbl.spamhaus.org
    reject_rhsbl_sender dbl.spamhaus.org
    check_policy_service unix:private/policy
    permit

# ===== 阶段 4: DATA 限制 =====
smtpd_data_restrictions =
    permit_mynetworks
    permit_sasl_authenticated
    reject_unauth_pipelining

# ===== 阶段 5: 数据结束限制 =====
smtpd_end_of_data_restrictions =
    permit_mynetworks
    permit_sasl_authenticated
```

## 4. 各阶段深度分析

### 4.1 smtpd\_helo\_restrictions

HELO 阶段是代价最小的拒绝点——在对方 MTA 声明发件人之前就切断连接。检查项包括：

* **reject\_invalid\_helo\_hostname**：拒绝明显非法的 HELO（如纯 IP 地址、空格等）
* **reject\_non\_fqdn\_helo\_hostname**：拒绝非 FQDN 的 HELO 主机名
* **reject\_unknown\_helo\_hostname**：对 HELO 主机名执行 DNS A/AAAA 查询，无法解析则拒绝——注意此规则会触发 DNS 查询，影响性能
* **check\_helo\_access**：自定义白名单与黑名单，如已知合规发送方可在此阶段直接 `OK`

**性能考量**：`reject_unknown_helo_hostname` 每次都会触发 DNS 前向查询。如果 MTA 每秒处理 500 个入站连接，该规则每秒产生 500+ 额外 DNS 查询。建议配合 `permit_mynetworks`（跳过本域连接）置于前面来避免不必要查询。

### 4.2 smtpd\_sender\_restrictions

此阶段在接收到发件人地址后触发，可执行 SPF 检查及发件人域验证：

* `reject_non_fqdn_sender`：拒绝发件人地址不是 FQDN 格式的邮件
* `reject_unknown_sender_domain`：DNS 无法解析发件人域，通常为垃圾邮件
* `check_sender_access`：灵活的发件人级访问控制

**注意**：`smtpd_sender_restrictions` 中不应放置 SPF 检查——SPF 按 RFC 7208 设计用于评估邮件发送授权，其在 Postfix 中的标准位置是 `smtpd_recipient_restrictions` 或作为 milter 执行[3]。原因在于：SPF 的结果（如 `reject_spf_*`）取决于 Envelope From，而该信息只在 RCPT 阶段之前已就绪，但在 sender 阶段执行 SPF 会丢失后续 RCPT 阶段的信息（如收件人域）。

### 4.3 smtpd\_recipient\_restrictions

这是 Postfix 入站管道中最复杂的阶段，也是 **唯一具备内置继电器逻辑** 的阶段。其规则列表的评估结果决定了该连接是允许中继还是拒绝[2]：

**关键顺序规则**：

1. **permit\_mynetworks / permit\_sasl\_authenticated 必须置于首位**：确保受信任网络和认证用户在 DNSBL 等检查之前直接通过
2. **reject\_unauth\_destination 必须放在 DNSBL 之前**：否则 Postfix 会为合法接入但在 DNSBL 中误杀的连接报错。逻辑是：先确定收件人是否属于本域（即是否由本 MTA 负责投递），再由 DNSBL 决定是否拒绝
3. **DNSBL 之后放 check\_policy\_service**：自定义策略服务（如 Postfwd、policy-rbl）通常只在固定检查通过后执行
4. **末尾必须 permit**：使所有未被显式拒绝的 RCPT TO 指令通过

**常见陷阱**：将 `reject_rbl_client` 放在 `reject_unauth_destination` 之前——合法发往本域的邮件可能因误命中 DNSBL 而被拒；将 `permit` 放在规则列表中部——Postfix 遇到 permit 立即终止求值，其后的规则会被忽略。

#### 4.3.1 DNSBL 性能影响

每个 `reject_rbl_client` 规则在每个 RCPT 阶段产生一次 DNS TXT 查询。如果配置了 5 个 DNSBL，每封邮件的每个收件人会产生 5 次查询。对于有 50 个收件人的群发，单次连接会产生 250 次 DNS 查询。对于大量收件人的邮件，建议在 RCPT 阶段之前（如在 smtpd\_helo\_restrictions 或预检查）进行聚合判断，或在 `check_policy_service` 中执行批量查询。

### 4.4 smtpd\_data\_restrictions

此阶段在客户端发送 DATA 命令后、MIME 内容体传输之前执行。Postfix 在此时已获知邮件的基本头（Content-Type、MIME-Version），但尚未开始接收正文。此阶段最常用的规则是：

* **reject\_unauth\_pipelining**：识别垃圾邮件发送者利用的 ESMTP PIPELINING 违规行为。垃圾邮件程序常过早发送 DATA，在未收到 DATA 确认前就开始发送内容。该规则检查客户端是否在收到 DATA 确认前就开始发送数据，是有效的垃圾标识

除非有特殊的 MIME 头检查需求，此阶段通常不会部署太多规则——因为此处拒绝时，MTA 已经向对端发送了 "354 End data with <CRLF>.<CRLF>"，对端已表明要投入带宽资源传输内容。若在此处拒绝，对方MTA会感到困惑且需要重新建立连接。

### 4.5 smtpd\_end\_of\_data\_restrictions

这是开销最大的拒绝点——MTA 已经接收了完整邮件内容（头部+正文），所有 Milter 检查和内容过滤已完成。此阶段通常用于 Milter 的返回结果（如 milter 报告为垃圾邮件时 SMFIS\_REJECT）：

```
# 结合 Milter 使用的常见配置
smtpd_end_of_data_restrictions =
    permit_mynetworks
    check_policy_service unix:private/after-queue-filter
```

在此阶段拒绝的邮件不会进入队列，Postfix 直接向对端发出 5xx 响应（通常为 "554 5.7.1 Message rejected by content filter"）。对端 MTA 会认为投递失败并尝试后续 MX。

**重要**：较大的内容过滤服务（如 ClamAV + Amavisd-new 串联）在其处理完成时已到了 DATA 结束或队列后阶段。如果过滤器判定为垃圾，此时拒绝虽然有效但浪费了之前的带宽和 CPU。最佳实践是将浅层垃圾规则（如头发规则、RBL）放在 recipient 阶段，深层分析（如 Bayes、附件扫描）放在 end\_of\_data 或 after-queue。

## 5. 安全边界分析

### 5.1 限制泄漏（SMTP Fuzzing）

Postfix 各阶段的错误消息（454/550 拒绝）在默认配置下会暴露具体的拒绝原因。攻击者可以利用这些信息：

* `reject_unknown_helo_hostname` 失败时返回 "HELO host not found" → 攻击者知道该 MTA 在验证 HELO DNS
* `reject_rbl_client` 失败时返回 "Service unavailable" → 攻击者知道有 RBL 拦截

**缓解**：使用自定义拒绝消息掩盖具体原因：

```
# 自定义 550 响应内容
smtpd_delay_reject = yes
disable_vrfy_command = yes
access_map_reject_code = 554
unknown_address_reject_code = 550
unknown_helo_hostname_reject_code = 554
rbl_reply_maps = /etc/postfix/rbl_reply

# /etc/postfix/rbl_reply
zen.spamhaus.org	554 5.7.1 Message rejected due to policy.
bl.spamcop.net	554 5.7.1 Message rejected due to policy.
```

### 5.2 smtpd\_delay\_reject 延迟拒绝

默认 `smtpd_delay_reject = yes` 会将所有 HELO/SENDER 阶段的 REJECT 延迟到 RCPT 阶段之后才发送。目的：垃圾邮件发送者通常在 RCPT 之前就断开连接，延迟拒绝能节省带宽并减少对合法发送者的信息泄漏。但此设置也意味着 HELO 阶段的 REJECT 不会立即切断连接。

## 6. 常见配置陷阱

### 6.1 陷阱 1：recipient 规则末尾缺少 permit

这是最常见的 Postfix 配置错误。如果没有 `permit`，所有不在显式规则中通过的非本域收件人会被默认拒绝——即配置了一个隐形的 Open Relay 拒绝。

```
# 错误：缺少 permit，所有非本域收件人都会被拒绝
smtpd_recipient_restrictions =
    permit_mynetworks
    reject_unauth_destination
    reject_rbl_client zen.spamhaus.org
    # 缺少 permit！合法外域发往本域也通过不了

# 正确
smtpd_recipient_restrictions =
    permit_mynetworks
    reject_unauth_destination
    reject_rbl_client zen.spamhaus.org
    permit
```

### 6.2 陷阱 2：permit 放错位置

`permit` 一旦命中，之后的规则不再执行。下面配置中的 `reject_rbl_client` 永远不会被评估：

```
# 错误：permit 在 reject_rbl_client 前，后者永远不会生效
smtpd_recipient_restrictions =
    permit_mynetworks
    reject_unauth_destination
    permit                 # ← 所有符合前面规则的连接直接通过！
    reject_rbl_client zen.spamhaus.org
```

### 6.3 陷阱 3：HELO 规则过于激进

`reject_unknown_helo_hostname` 会拒绝所有 HELLO 主机名没有 DNS 记录的连接。一些邮件管理系统（尤其是邮件列表、批量发送器）使用无 DNS 记录的临时 HELO，会因此被拒绝。建议使用 `warn_if_reject reject_unknown_helo_hostname`——在日志中记录警告但不拒绝，观察一段时间后再决定是否开启真正拒绝。

### 6.4 陷阱 4：smtpd\_helo\_required = yes 的副作用

启用 `smtpd_helo_required = yes` 强制客户端在 MAIL FROM 前发送 HELO/EHLO。虽然这符合 RFC 5321 的建议行为，但部分不合规的 MTA 会直接发送 MAIL FROM 而不发 HELO——启用了该选项后这些连接会被拒绝。有些供应链集成系统（如扫描仪直发邮件、设备告警）依赖这种行为，需特别注意。

## 7. 性能调优指南

| 限制阶段 | 典型查询 | 每次查询耗时 | 优化建议 |
| --- | --- | --- | --- |
| HELO | DNS A 查询（unknown\_helo\_hostname） | 10-50ms | 使用 DNS 缓存（如 dnsmasq/unbound） |
| SENDER | DNS 域名解析 | 5-20ms | permit\_mynetworks 前置 |
| RECIPIENT | DNSBL × N + SPF + 策略服务 | 50-500ms | 限制 DNSBL 数量至 3 个以内；使用 check\_policy\_service 聚合 |
| DATA | （很少涉及网络查询） | <1ms | 仅放必要的 MIME 头检查 |
| EOD | Milter 过滤 | 100ms-5s | 使用浅层过滤器前置；EOD 仅处理深度分析 |

对于高吞吐场景（>1000 连接/秒），建议：

1. 将 DNSBL 放在 `smtpd_recipient_restrictions` 后段，确保非本域邮件在前面被拒绝
2. 使用 `smtpd_client_event_limit_exceptions` 为信任客户端放宽限制
3. 启用 Postfix 的 `smtpd_client_connection_rate_limit` 防止单个 IP 的洪水攻击

## 参考文献

1. Postfix SMTP Server (smtpd) — Postfix Configuration Manual. smtpd(8) Man Page. <https://www.postfix.org/smtpd.8.html>
2. Postfix SMTPD Access Policy Delegation — Postfix Documentation. RESTRICTION\_CLASSES\_README.html, Section 2 (Restriction Evaluation Order). <https://www.postfix.org/RESTRICTION_CLASSES_README.html>
3. RFC 7208 — Sender Policy Framework (SPF) for Authorizing Use of Domains in Email, Version 1. IETF, April 2014. Section 9 (Implementation Considerations).
4. RFC 5321 — Simple Mail Transfer Protocol. IETF, October 2008. Section 3.2 (HELO/EHLO), Section 4.1.1.4 (MAIL FROM).
5. Postfix Performance Tuning — Postfix Documentation. TUNING\_README.html, Section 3 (Limiting Resource Usage). <https://www.postfix.org/TUNING_README.html>
6. RFC 2821 — Simple Mail Transfer Protocol. IETF, April 2001. Section 4.1.1.4 (SMTP Relay Behavior).

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/postfix-smtpd-restrictions-guide.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
