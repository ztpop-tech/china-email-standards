---
title: "SMTP 投递状态通知（DSN）全面解读 · RFC 3461"
source: "https://ztpop.net/kb/smtp-dsn-rfc3461.html"
license: CC-BY 4.0
---

# SMTP 投递状态通知（DSN）全面解读 · RFC 3461

## 一、引言

投递状态通知（Delivery Status Notification，DSN）是邮件系统中最重要的反馈机制之一。当一封邮件发送出去后，发件人需要知道邮件是否成功投递、被延迟、被拒收或无法送达。RFC 3461（2003 年 1 月发布，obsolotes RFC 1891）定义了 SMTP 的 DSN 服务扩展，使得 SMTP 客户端可以精确控制何时收到状态通知、通知中是否包含邮件原文，以及如何将通知关联到原始邮件事务。

RFC 3461 是 [SMTP 协议](/kb/smtp-protocol-deep-dive.html)体系中的核心补充，它与 RFC 5321 一起构成了现代邮件中继的基础设施。

## 二、DSN 的核心参数

### 2.1 NOTIFY 参数（RCPT TO 命令）

NOTIFY 参数允许发件人为每个收件人指定触发 DSN 的条件。RFC 3461 第 4.1 节定义了四个可能的值：

* **NEVER** — 无论投递结果如何，都不返回 DSN。适用于邮件列表场景以避免回弹炸弹。
* **SUCCESS** — 仅在投递成功时通知。
* **FAILURE** — 仅在投递失败时通知（默认行为）。
* **DELAY** — 当投递因临时错误被延迟时通知。延迟的判定取决于 MTA 的本地策略，典型超时在 1 至 24 小时之间。

SUCCESS、FAILURE 和 DELAY 可以组合使用，例如 `NOTIFY=SUCCESS,FAILURE` 表示成功或失败都通知。

### 2.2 RET 参数（MAIL FROM 命令）

RET 参数控制 DSN 中是否包含原邮件的内容。RFC 3461 第 4.3 节定义了两种模式：

* **FULL** — 返回完整邮件内容。
* **HDRS** — 仅返回邮件头部。

出于隐私性和带宽考虑，大部分 MTA 默认使用 HDRS 模式。

### 2.3 ENVID 参数（MAIL FROM 命令）

ENVID（Envelope ID）是一个由发件人 MUA 或 MSA 分配的字符串，用于标识原始邮件事务。当 DSN 返回时，DSN 中的 "original-envelope-id" 字段会回传该值，使发件人能够将 DSN 与原始邮件关联。RFC 3461 第 4.4 节要求 ENVID 在发送 MTA 的范围内唯一。

### 2.4 ORCPT 参数（RCPT TO 命令）

ORCPT（Original Recipient Address）用于保存收件人的原始地址（即发件人输入时的格式），以解决地址改写（如别名展开、大小写规范化）后无法匹配的问题。RFC 3461 第 4.2 节指定 ORCPT 的格式为 `地址类型;地址值`，例如 `rfc822;user@example.com`。

## 三、DSN 消息格式（RFC 3464）

DSN 本身使用 MIME 封装的多部分报告格式，由 RFC 3464 定义。标准 DSN 包含以下部分：

* **第一部分（text/plain）** — 人类可读的投递状态文本。
* **第二部分（message/delivery-status）** — 结构化字段集合，包含 per-message 字段（如 original-envelope-id、reporting-mta）和 per-recipient 字段（如 final-recipient、action、status、remote-mta）。
* **第三部分（可选，message/rfc822 或 text/rfc822-headers）** — 原始邮件的全文或头部，取决于 RET 参数。

状态码采用 RFC 3463（后由 RFC 5248 更新）定义的三级增强状态码格式 `class.subject.detail`，例如 `5.1.1` 表示永久失败（5）、收件人相关问题（1）、邮箱不存在（1）。

## 四、实践配置与排错

### 4.1 Postfix 中的 DSN 支持

Postfix 从早期版本就开始支持 RFC 3461。关键配置包括：

* `notify_classes` — 控制 Postfix 自身生成的 DSN 类别（bounce、delay、success 等）。
* `bounce_queue_lifetime` — 控制延迟通知的等待时间。
* `enable_dsn` — 启用或禁用 RFC 3461 DSN 扩展。

### 4.2 常见问题

**延迟通知风暴**：当远程 MTA 临时不可达时，如果 NOTIFY=DELAY 被广泛启用，每个延迟的收件人都可能生成 DSN。建议在 MTA 层面设置合理的延迟检测间隔和通知频次上限。

**回弹炸弹**：当攻击者伪造 MAIL FROM 地址发送大量邮件时，DSN 会返回到无辜的第三方邮箱。这是 NOTIFY=FAILURE 的默认行为导致的。部署 [SRS（Sender Rewriting Scheme）](/kb/srs-sender-rewriting.html)和 DMARC 验证是缓解此问题的有效措施。

**DSN 循环**：当两个 MTA 相互发送 DSN 时可能形成循环。遵循 RFC 3461 第 4.5 节的限制（DSN 不应再触发 DSN）可以避免此问题。

## 五、总结

RFC 3461 定义的 DSN 机制是邮件系统可靠性的基石。合理的 DSN 配置可以显著改善运维体验，帮助管理员及时发现投递异常。在信创邮件系统中，也建议完整实现 RFC 3461 和 RFC 3464 所定义的 DSN 规范，确保与全球邮件系统的互通性。

### 相关文章

* [SMTP 协议深度解析](/kb/smtp-protocol-deep-dive.html)
* [SMTP 退信码全解](/kb/smtp-bounce-codes.html)
* [邮件技术标准一览](/kb/email-standards-reference.html)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/smtp-dsn-rfc3461.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
