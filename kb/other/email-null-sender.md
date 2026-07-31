---
title: "什么是“空信封发件人（Null Sender，MAIL FROM:<>，RFC 5321 §4.5.5）”？它用在哪？"
source: "https://ztpop.net/kb/email-null-sender.html"
license: CC-BY 4.0
---

# 什么是“空信封发件人（Null Sender，MAIL FROM:<>，RFC 5321 §4.5.5）”？它用在哪？

1
什么是“空信封发件人（Null Sender，MAIL FROM:<>，RFC 5321 §4.5.5）”？它用在哪？
▼

**定义**

空信封发件人指 SMTP MAIL FROM 后为空尖括号 <>；按 RFC 5321 它“不能接收邮件”，专门用于“不能产生二次退信”的信。

**用途**

① DSN/退信本身用空发件人发出（退信不能再被退）；② 自动系统通知、探测信；③ 某些健康检查。接收方不应向 <> 回退信。

**坑**

反垃圾策略若“要求 MAIL FROM 非空”会误杀正当退信；SPF 检查空发件人需用 helo/iprev 而非 SPF（因无域名）。

**实践**

邮件系统发退信/DSN 必须用空发件人；入站过滤要把“<> 发来的 DSN”识别为合法退信而非伪造，避免误判。

参考：RFC 5321 §4.5.5（Null Sender 定义）；RFC 3464（DSN 用空发件人）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-null-sender.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
