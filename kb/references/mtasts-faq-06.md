---
title: "MTA-STS 处于 enforce 模式时，若无法与接收方建立 TLS 连接，邮件会怎样？"
source: "https://ztpop.net/kb/mtasts-faq-06.html"
license: CC-BY 4.0
---

# MTA-STS 处于 enforce 模式时，若无法与接收方建立 TLS 连接，邮件会怎样？

1
MTA-STS 处于 enforce 模式时，若无法与接收方建立 TLS 连接，邮件会怎样？
▼

**行为**

在 enforce 模式下，支持 MTA-STS 的发送方只会通过安全连接、向策略指定的 MX 投递；如果无法建立安全连接（如证书不匹配、对端不支持 STARTTLS），邮件将不会被投递，而是被推迟或退回。

**取舍**

这正是 MTA-STS 的安全价值——宁可短期不可达，也不让邮件以明文被窃听。因此上线 enforce 前务必确认所有合法 MX 都已正确配置 TLS。

参考：Cloudflare “Configure MTA-STS”（enforce 语义）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/mtasts-faq-06.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
