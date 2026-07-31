---
title: "IMAP 的 UNSELECT（RFC 3691）是什么？它和普通关闭邮箱有何不同？"
source: "https://ztpop.net/kb/imap-unselect-rfc3691.html"
license: CC-BY 4.0
---

# IMAP 的 UNSELECT（RFC 3691）是什么？它和普通关闭邮箱有何不同？

1
IMAP 的 UNSELECT（RFC 3691）是什么？它和普通关闭邮箱有何不同？
▼

**问题**

CLOSE 会“永久删除”当前邮箱的 \Deleted 标记信件；有时只想“离开当前邮箱但不删信”，标准 CLOSE 做不到。

**UNSELECT**

UNSELECT（非选中）让客户端“脱离当前邮箱”而“不执行 EXPUNGE”（不删 \Deleted 信），相当于“安静退出”。

**价值**

用户在“标记删除但尚未确定”时切换文件夹，避免被 CLOSE 误删；是 CLOSE 的“安全替代”。

**实践**

邮件系统支持 UNSELECT 后，客户端“切换箱不删信”更顺手；注意并非所有旧服务器支持，客户端需探测能力。

参考：RFC 3691（IMAP UNSELECT 扩展）；RFC 3501（CLOSE 对比）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/imap-unselect-rfc3691.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
