---
title: "SMTP 的标准命令集（RFC 5321）有哪些？各自干什么？"
source: "https://ztpop.net/kb/email-smtp-command-reference.html"
license: CC-BY 4.0
---

# SMTP 的标准命令集（RFC 5321）有哪些？各自干什么？

1
SMTP 的标准命令集（RFC 5321）有哪些？各自干什么？
▼

**握手/信封**

EHLO/HELO 自我介绍并显示能力；MAIL FROM 设信封发件人；RCPT TO 设收件人（可多个）；DATA 后传信体（以单独 . 结束）。

**控制**

RSET 中止当前事务（不清状态）；NOOP 保活/探测；QUIT 关闭；VRFY 验证邮箱（多禁用以防信息泄露）；ETRN 触发队列投递（拨号场景）。

**扩展**

STARTTLS 升级加密、AUTH 认证、SIZE/PIPELINING/CHUNKING/DSN 等为 EHLO 公布的扩展命令。

**实践**

理解命令流有助于排错（用 swaks/telnet 手演）与安全加固（禁用 VRFY/EXPN、限制命令频率）；邮件系统对话日志即这些命令的序列。

参考：RFC 5321 §4.1（SMTP 命令）；RFC 3207（STARTTLS）；RFC 4954（AUTH）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-smtp-command-reference.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
