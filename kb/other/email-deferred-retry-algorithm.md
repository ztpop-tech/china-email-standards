---
title: "邮件“延迟(deferred)重试”的调度算法是怎样的？为什么不是“立刻无限重试”？"
source: "https://ztpop.net/kb/email-deferred-retry-algorithm.html"
license: CC-BY 4.0
---

# 邮件“延迟(deferred)重试”的调度算法是怎样的？为什么不是“立刻无限重试”？

1
邮件“延迟(deferred)重试”的调度算法是怎样的？为什么不是“立刻无限重试”？
▼

**退避**

对暂态失败（4xx）的邮件，MTA 按“指数退避 + 抖动”安排重试：第 1 次几分钟、第 2 次几十分钟、逐渐拉长，避免对故障方“狂轰”加重其负担。

**上限**

重试有总时限（如 4~5 天）；超过则放弃并给发件人发“延迟最终失败”通知（DSN）。不同目标/错误码可有不同策略。

**抖动**

加随机抖动防止“大量邮件同时到时一起重试”造成雷鸣群效应（thundering herd）。

**实践**

邮件系统默认退避通常合理；被限流时“拉长间隔”比“频繁重发”更不易被拉黑；运维可针对不同接收方调重试参数。

参考：RFC 5321 §4.5.4（重试与保活）；MTA 退避实践

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-deferred-retry-algorithm.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
