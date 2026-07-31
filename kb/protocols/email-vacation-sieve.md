---
title: "用 Sieve 的 Vacation 扩展（RFC 5230）做“自动回复/外出通知”有何讲究？"
source: "https://ztpop.net/kb/email-vacation-sieve.html"
license: CC-BY 4.0
---

# 用 Sieve 的 Vacation 扩展（RFC 5230）做“自动回复/外出通知”有何讲究？

1
用 Sieve 的 Vacation 扩展（RFC 5230）做“自动回复/外出通知”有何讲究？
▼

**机制**

Vacation 扩展提供 vacation 动作：对来信自动回一段“我正在外出”通知；可设 主题前缀、回复间隔（避免对同一发件人刷屏）、排除列表/自动信。

**防滥**

关键防护：① 对同一发件人冷却期只回一次；② 不为“自动信/退信/列表邮件”回复（检测 Precedence/Auto-Submitted）；③ 不回复空信封发件人（<>）。

**对比**

比老式 .forward+vacation 程序更可控、可条件化；与 RFC 3834（Auto-Submitted）规范一致，避免“自动回复风暴”。

**实践**

邮件系统开启 Sieve Vacation 后，用户设外出通知即可；网关层也应遵循 Auto-Submitted 头，防止 vacation 与自动系统互相触发循环。

参考：RFC 5230（Sieve Vacation 扩展）；RFC 3834（自动回复行为准则）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-vacation-sieve.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
