---
title: "Deferred（延迟）与 Bounced（退信）有什么区别？何时邮件被最终退回？"
source: "https://ztpop.net/kb/deferred-vs-bounced.html"
license: CC-BY 4.0
---

# Deferred（延迟）与 Bounced（退信）有什么区别？何时邮件被最终退回？

1
Deferred（延迟）与 Bounced（退信）有什么区别？何时邮件被最终退回？
▼

**定义**

Deferred 是“临时失败”（4xx 响应或连接超时）：邮件留在队列按退避策略重试，根因可能是对方忙、网络抖、限流；Bounced 是“永久失败”（5xx）触发的退信。

**5xx 与退信**

收到 5xx（如 550 无此用户、554 被拒）即认为不可投递，MTA 生成退信（NDR/bounce）发回发件人并将原信移出队列。

**重试边界**

RFC 5321 建议至少重试 4–5 天（常见 2–7 天）后才放弃 deferred 转退信；过早判死会丢信，过晚则占队列。重试间隔用指数退避。

**运维**

监控 deferred 年龄分布；长期 deferred 多为目标域问题或限流，应自然超时退信，不要手动强删。

参考：RFC 5321 §4.5.4（重试与退信）；RFC 3463/3464（DSN 状态码）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/deferred-vs-bounced.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
