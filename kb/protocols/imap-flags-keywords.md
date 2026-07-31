---
title: "IMAP 的“标志（Flags）”与“关键字（Keywords）”是什么？系统标志与自定义标记如何工作？"
source: "https://ztpop.net/kb/imap-flags-keywords.html"
license: CC-BY 4.0
---

# IMAP 的“标志（Flags）”与“关键字（Keywords）”是什么？系统标志与自定义标记如何工作？

1
IMAP 的“标志（Flags）”与“关键字（Keywords）”是什么？系统标志与自定义标记如何工作？
▼

**系统标志**

IMAP 预定义标志如 \Seen（已读）、\Answered（已回复）、\Flagged（星标）、\Deleted（待删）、\Draft（草稿）、\Recent（新到，已废弃），由服务器维护、跨客户端同步。

**关键字**

除系统标志外 IMAP 允许多个“非系统关键字”（如 $label1、自定义标签），以 $ 或字母开头（RFC 3501）；现代客户端用关键字实现“标签”功能。

**操作**

STORE 命令设置/清除标志（如 STORE 1 +FLAGS (\Flagged)）；FLAGS 为私有，以 $ 开头的关键字为“共享”，服务端持久化供多端同步。

**实践**

\Deleted 需配合 EXPUNGE 才真正删，误删可 STORE -FLAGS (\Deleted) 撤销；邮件系统对关键字的支持度决定标签类功能是否跨端一致。

参考：RFC 3501 §2.3.2（Flags）/ §2.3.3（Keywords）；RFC 5788（IMAP4 关键字）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/imap-flags-keywords.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
