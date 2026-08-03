---
title: "SMTP 增强状态码（RFC 3463）如何解读？"
source: "https://ztpop.net/kb/smtp-enhanced-status-codes-rfc3463.html"
license: CC-BY 4.0
---

# SMTP 增强状态码（RFC 3463）如何解读？

1
SMTP 增强状态码（RFC 3463）如何解读？
▼

**结构：类.主题.细节**

增强状态码形如 `5.1.1`，由三段点分数字组成。第一段为「类（class）」：`2.X.X` 表示成功；`4.X.X` 表示持久性暂态失败（应重试）；`5.X.X` 表示永久失败（不应重试）。第二段为「主题（subject）」：`0` 其他、`1` 寻址、`2` 邮箱、`3` 邮件系统、`4` 网络/路由、`5` 协议、`6` 媒体、`7` 安全/策略。第三段「细节（detail）」给出该主题下的具体原因。

**常见示例**

`5.1.1` 收件人邮箱不存在（bad destination mailbox address）；`4.2.2` 邮箱已满（mailbox full，可重试）；`5.7.1` 投递未授权/被策略拒绝（delivery not authorized）；`4.4.1` 收件主机无响应（连接超时）；`5.4.6` 路由环路（routing loop detected）。结合 SMTP reply text 与增强码，运维可快速区分是寻址、容量还是策略问题。

**实践用途**

在退信（DSN，RFC 3464）的 `Status:` 信头中携带增强码，批量发信平台据此自动归类硬退/软退、触发列表清洗或告警。相比仅靠人类可读的英文回复文本，三段式编码更利于机器解析与跨语言一致处理。注意增强码由对端 MTA 生成，需双方实现 RFC 3463 才能完整呈现。

参考：RFC 3463《Enhanced Mail System Status Codes》、RFC 5248《常用邮件系统状态码对照》、RFC 3464《DSN 投递状态通知》。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/smtp-enhanced-status-codes-rfc3463.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
