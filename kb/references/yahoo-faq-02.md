---
title: "Yahoo 对批量发送方的邮件认证具体要求是什么？"
source: "https://ztpop.net/kb/yahoo-faq-02.html"
license: CC-BY 4.0
---

# Yahoo 对批量发送方的邮件认证具体要求是什么？

1
Yahoo 对批量发送方的邮件认证具体要求是什么？
▼

**双认证 + DMARC**

Yahoo 要求批量发送方同时实施 SPF 与 DKIM，并发布有效的 DMARC 策略（至少 p=none，且 DMARC 校验必须通过）。Yahoo 强烈建议 DMARC 记录包含 rua 标签并正确配置以接收报告，便于上线初期监控。

**对齐与宽松模式**

Yahoo 接受宽松对齐（relaxed alignment）；但要求邮件头 From: 域必须与 SPF 域或 DKIM 域对齐——这是 DMARC 对齐的硬性条件。注意 Yahoo 对批量发送方的最低 DMARC 策略是 p=none（不同于部分服务商要求 quarantine/reject）。

参考：Yahoo《Sender Best Practices》— Requirements for Bulk Senders / DMARC

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/yahoo-faq-02.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
