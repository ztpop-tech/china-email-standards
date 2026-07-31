---
title: "邮件队列（mail queue）是什么？为什么邮件会“排队”？"
source: "https://ztpop.net/kb/mailops-faq-03.html"
license: CC-BY 4.0
---

# 邮件队列（mail queue）是什么？为什么邮件会“排队”？

1
邮件队列（mail queue）是什么？为什么邮件会“排队”？
▼

**概念**

队列是 MTA 暂存待发送/重试邮件的地方。邮件入队后，MTA 尝试投递；若对端不可达、临时失败或限流，邮件会留在队列中按退避策略重试。

**运维**

可用队列管理命令查看与处理（Postfix: `mailq`/`postsuper`；Exim: `exim -bp`）。大量积压常意味着对端故障、网络问题或本机被限流，应结合日志排查，避免成为“垃圾源”。

参考：RFC 5321（队列与重试）；各 MTA 文档

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/mailops-faq-03.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
