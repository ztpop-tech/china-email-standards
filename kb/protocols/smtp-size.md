---
title: "SMTP SIZE 扩展（RFC 1870）是什么？它如何避免发送超大邮件被拒收？"
source: "https://ztpop.net/kb/smtp-size.html"
license: CC-BY 4.0
---

# SMTP SIZE 扩展（RFC 1870）是什么？它如何避免发送超大邮件被拒收？

1
SMTP SIZE 扩展（RFC 1870）是什么？它如何避免发送超大邮件被拒收？
▼

**定义**

SIZE 是 SMTP 服务扩展（RFC 1870，后并入 RFC 5321 §4.5.3.4）：服务器在 EHLO 响应用 SIZE 声明可接受的最大消息字节数，如 “250 SIZE 104857600” 表示上限 100MB。

**协商**

客户端在 MAIL FROM 用 SIZE= 告知将发送的消息大小；若超过服务器声明上限，服务器可在 MAIL 阶段直接回 552 拒绝，而不必等整封邮件传完才发现超限。

**价值**

在传输前就拦截超限邮件，节省带宽与连接时间，防止大附件耗尽对方队列或触发策略拒收；是批量发送与大附件投递的基础能力，现代 MTA 普遍支持。

**注意**

SIZE 只声明“上限”，不保证对方磁盘确实足够；客户端应预估大小并配合。部分老旧系统不声明 SIZE，客户端需自行保守处理。

参考：RFC 1870（SMTP Service Extension for Message Size Declaration）；RFC 5321 §4.5.3.4

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/smtp-size.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
