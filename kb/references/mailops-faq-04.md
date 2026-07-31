---
title: "SMTP 的 HELO/EHLO 与 STARTTLS 分别起什么作用？"
source: "https://ztpop.net/kb/mailops-faq-04.html"
license: CC-BY 4.0
---

# SMTP 的 HELO/EHLO 与 STARTTLS 分别起什么作用？

1
SMTP 的 HELO/EHLO 与 STARTTLS 分别起什么作用？
▼

**HELO/EHLO**

会话开始时，客户端用 `HELO`（或扩展的 `EHLO`）向服务器声明身份。EHLO 后服务器会列出支持的扩展（如 STARTTLS、SIZE、AUTH）。

**STARTTLS**

`STARTTLS` 命令把已建立的明文 SMTP 连接升级为 TLS 加密连接；若一方不支持或被中间人剥离，连接会退回明文——这正是一只有 MTA-STS/DANE 才能防住的“降级”风险。

参考：RFC 5321（HELO/EHLO）；RFC 3207（STARTTLS）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/mailops-faq-04.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
