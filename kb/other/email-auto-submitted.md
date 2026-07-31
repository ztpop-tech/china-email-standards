---
title: "邮件头 Auto-Submitted 字段（RFC 3834/5968）有什么用？为何能区分“人发的信”与“机器自动信”？"
source: "https://ztpop.net/kb/email-auto-submitted.html"
license: CC-BY 4.0
---

# 邮件头 Auto-Submitted 字段（RFC 3834/5968）有什么用？为何能区分“人发的信”与“机器自动信”？

1
邮件头 Auto-Submitted 字段（RFC 3834/5968）有什么用？为何能区分“人发的信”与“机器自动信”？
▼

**字段**

Auto-Submitted: auto-replied / auto-notified / auto-generated / auto-forwarded 等，由自动系统在自己发出的信里声明“我是自动信”，供接收方策略识别（RFC 3834 §5，更新于 RFC 5968）。

**用途**

接收方（或个人过滤器）可据 Auto-Submitted 决定“不对该信再自动回复”（避免循环）、“降权处理通知类邮件”、“不计入活跃对话”。

**与 vacation**

自动回复（休假回复）应加 Auto-Submitted: auto-replied，并对“已是 auto-replied/auto-notified 的信”不再自动回复——这是 RFC 3834 断环的核心机制。

**注意**

Auto-Submitted 是“声明”不强制；合规系统（列表服务器、退信、日历邀请自动信）都应正确标注，便于下游治理与防循环。

参考：RFC 3834 §5（Auto-Submitted）；RFC 5968（更新）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-auto-submitted.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
