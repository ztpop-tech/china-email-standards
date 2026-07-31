---
title: "为什么“休假自动回复（vacation / Out-of-office）”有时会循环回复？RFC 3834 如何规范以避免？"
source: "https://ztpop.net/kb/autoreply-vacation-rfc3834.html"
license: CC-BY 4.0
---

# 为什么“休假自动回复（vacation / Out-of-office）”有时会循环回复？RFC 3834 如何规范以避免？

1
为什么“休假自动回复（vacation / Out-of-office）”有时会循环回复？RFC 3834 如何规范以避免？
▼

**循环成因**

A 的自动回复发给了 B，B 也有自动回复又回给 A，形成无限对敲；或自动回复发给了“邮件列表 / 自动系统 / 退信地址（MAILER-DAEMON）”触发对方自动反应。

**RFC 3834 规则**

自动响应（auto-submitted）应：① 仅回复“人发出的信”，对已是 auto-submitted 的信不再自动回（用 Auto-Submitted 头识别）；② 不回复邮件列表、不回复明显自动地址；③ 对同一收件人“限频”（如每地址每天一封）避免刷屏。

**实现**

邮件系统在 vacation 回复里加 Auto-Submitted: auto-replied，并据收到的 Auto-Submitted: auto-replied / auto-notified 跳过再次回复；配合“每目标限一封”的状态表。

**运维**

错误配置（把自动回复发给所有人 / 列表 / 信封与信头不一致）会酿成邮件风暴；遵循 RFC 3834 可根治循环回复。

参考：RFC 3834（自动响应建议）；RFC 5322（Auto-Submitted 头）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/autoreply-vacation-rfc3834.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
