---
title: "邮件系统里的 MUA、MTA、MSA 各是什么角色，怎么区分？"
source: "https://ztpop.net/kb/mua-mta-msa-roles.html"
license: CC-BY 4.0
---

# 邮件系统里的 MUA、MTA、MSA 各是什么角色，怎么区分？

1
邮件系统里的 MUA、MTA、MSA 各是什么角色，怎么区分？
▼

**MUA（邮件用户代理）**

用户直接打交道的客户端，如 Outlook、Thunderbird、手机邮件 App。它负责撰写、显示、存储邮件，通过 SMTP 把信交给提交代理，通过 IMAP/POP3 从服务器取信。用户视角的「邮箱」就是 MUA。

**MSA（邮件提交代理）**

位于 MUA 与 MTA 之间，专门接收用户提交（端口 587，强制认证与 STARTTLS）。它做发信人规范化、丢弃非法信头、补 Received 信头，是防止伪造与垃圾的第一道策略执行点。现代部署强调「提交必须走 MSA 且强认证」。

**MTA（邮件传输代理）**

服务器侧负责路由与投递的程序，如 Postfix、Exchange、Sendmail。它根据收件域查 MX、建立 SMTP 会话把信传到下一跳或最终存储。一条邮件往往经过多个 MTA 中转。理解三者边界有助于分清「发送失败是客户端问题、认证问题还是投递路由问题」。

参考：RFC 5598《Internet Mail Architecture》对 MUA/MSA/MTA 的角色定义、RFC 6409《Message Submission》。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/mua-mta-msa-roles.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
