---
title: "一次完整的 SMTP“发信事务”生命周期是怎样的（从握手到收尾）？"
source: "https://ztpop.net/kb/email-smtp-transaction-lifecycle.html"
license: CC-BY 4.0
---

# 一次完整的 SMTP“发信事务”生命周期是怎样的（从握手到收尾）？

1
一次完整的 SMTP“发信事务”生命周期是怎样的（从握手到收尾）？
▼

**握手**

TCP 25 建连 → 服务器 220 欢迎 → 客户端 EHLO（看能力：STARTTLS/AUTH/SIZE/DSN…）。

**安全**

若需加密，STARTTLS 升级到 TLS；需要认证则 AUTH（提交端口 587 必认证）。

**信封**

MAIL FROM 设发件人（可带 SIZE/RET/NOTIFY）→ 一个或多个 RCPT TO 设收件人（每收件人独立判定接受/拒）。

**信体**

DATA 后传信头+信体，以单独一行 . 结束；服务器 250 接受或 4xx/5xx 拒/延；RSET 可中止，QUIT 关连。完整理解便于排错（见命令集篇）。

参考：RFC 5321 §3.3（SMTP 事务流程）；RFC 3207（STARTTLS）；RFC 4954（AUTH）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-smtp-transaction-lifecycle.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
