---
title: "邮件列表/归档常用什么“存储格式”？mbox 与 Maildir 有何区别？"
source: "https://ztpop.net/kb/email-mailing-list-archive-mbox.html"
license: CC-BY 4.0
---

# 邮件列表/归档常用什么“存储格式”？mbox 与 Maildir 有何区别？

1
邮件列表/归档常用什么“存储格式”？mbox 与 Maildir 有何区别？
▼

**mbox**

单文件顺序存多封信（每条以 From 分隔），简单、易整体备份/迁移，但并发写需锁、单文件损坏影响全部、大文件难处理。

**Maildir**

每封信一个独立文件（tmp/new/cur 目录结构），天然支持并发写入无锁、单信损坏不影响其它、易增量备份；现代邮件系统/列表归档多用。

**选型**

高并发/大列表场景偏好 Maildir；老旧归档或简单导出可能用 mbox（如标准 mboxo/mboxrd 变体）。

**实践**

邮件系统落地与列表归档应优先 Maildir（配合索引）以保证并发与可恢复；跨系统迁移注意格式转换与信封信息保留。

参考：mbox / Maildir 格式实践；Qmail/Courier Maildir 规范

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-mailing-list-archive-mbox.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
