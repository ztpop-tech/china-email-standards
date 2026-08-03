---
title: "如何分析 Received 信头字段进行邮件溯源？"
source: "https://ztpop.net/kb/email-header-received-field-analysis.html"
license: CC-BY 4.0
---

# 如何分析 Received 信头字段进行邮件溯源？

1
如何分析 Received 信头字段进行邮件溯源？
▼

**信头排序规则**

一封邮件常携多个 `Received` 头，它们按**时间倒序**堆叠：最上方（最新）是收件方最终服务器收到的最后一段；最底部（最旧）是发件方 MSA/MTA 打的第一跳。溯源时应**自底向上**阅读，才能还原真实传输时序。

**核心令牌含义**

每个 Received 行通常含以下令牌：

* `from`：对端声明的主机名（HELO/EHLO 名），可被伪造，需与 rDNS 比对；
* `by`：本端接收服务器；
* `with`：传输协议，如 ESMTP、ESMTPS（带 TLS）；
* `for`：信封收件人；
* `id`：本跳队列 ID，便于在日志中定位；
* `date`：本跳接收时间（含时区），用于串起时间线。

**实战判定伪造**

若底层 Received 的 `from` 主机名与上游 Received 的 `by` 不一致（如上一跳说发往 mx.recipient.com，下一跳却声称 from 一个无关域名），即存在跳变，提示中转被伪造或信头被手工拼接。结合 TLS 标记（`ESMTPS` 与 `version=TLSv1.3 cipher=...`）可确认链路是否加密。

示例：`Received: from mail.x.com (mail.x.com [203.0.113.5]) by mx.y.com with ESMTPS id abc123 for <u@y.com>; Mon, 3 Aug 2026 09:12:01 +0800`

参考：RFC 5321《SMTP》3.6.7 节 Received 信头规范、RFC 5322《Internet Message Format》3.6.7 节。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-header-received-field-analysis.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
