---
title: "SMTP 重试退避（Backoff，RFC 5321 §4.5.4.1）如何工作？为何要指数退避？"
source: "https://ztpop.net/kb/smtp-retry-backoff.html"
license: CC-BY 4.0
---

# SMTP 重试退避（Backoff，RFC 5321 §4.5.4.1）如何工作？为何要指数退避？

1
SMTP 重试退避（Backoff，RFC 5321 §4.5.4.1）如何工作？为何要指数退避？
▼

**定义**

当投递遇临时失败（4xx 或连接超时），MTA 把邮件留在队列并按“重试间隔”重投。RFC 5321 建议采用递增（指数）退避而非固定频密重试。

**指数退避**

第一次失败 30 分钟后重试，之后 1 小时、2 小时、4 小时……间隔翻倍，避免对“暂时不可用”的对方造成雪崩式重试（thundering herd），也省自身资源。

**上限**

建议至少持续重试 4–5 天（常见 2–7 天）才放弃转退信；期间若对方恢复（如维护结束）能自动补投，平衡“不丢信”与“不占队列”。

**配合**

退避与速率限制、队列管理联动：延迟邮件按退避调度，避免与正常新信争抢连接。

参考：RFC 5321 §4.5.4.1（重试间隔与退避建议）；RFC 3463/3464（DSN）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/smtp-retry-backoff.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
