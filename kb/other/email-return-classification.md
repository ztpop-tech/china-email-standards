---
title: "邮件退信（return/bounce）如何分类？硬退信与软退信有什么区别？"
source: "https://ztpop.net/kb/email-return-classification.html"
license: CC-BY 4.0
---

# 邮件退信（return/bounce）如何分类？硬退信与软退信有什么区别？

1
邮件退信（return/bounce）如何分类？硬退信与软退信有什么区别？
▼

**分类维度**

退信按 SMTP 状态码分：5.x 永久失败=硬退信（hard bounce），4.x 暂态失败=软退信（soft bounce）。RFC 5321 §4.2 与 RFC 3463 定义了回复码与增强状态码语义。

**硬退信**

收件人不存在(5.1.1)、域不可达(5.1.2)、被策略永久拒收(5.7.x)等属永久失败。硬退通常不应重试，应把该地址标记为无效并停止发送，以免持续失败损害发信信誉。

**软退信**

邮箱满(4.2.2)、服务器临时不可用(4.3.x)、超时(4.2.1)、灰名单临时拒收(4.x)等属暂态失败。软退可重试，多数 MTA 按 RFC 5321 重试队列在一段时间内多次尝试后再放弃。

**处置**

邮件系统应统计退信率：硬退立即清理、软退多次失败转硬退；高退信率会拉低域名信誉、触发更多进垃圾箱。结合 VERP/ARF 实现退信自动化闭环。

参考：RFC 5321 §4.2（SMTP 回复码）；RFC 3463（增强状态码）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-return-classification.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
