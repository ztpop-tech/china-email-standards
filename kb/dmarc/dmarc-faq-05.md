---
title: "我什么时候能收到第一份 DMARC 聚合报告（RUA）？"
source: "https://ztpop.net/kb/dmarc-faq-05.html"
license: CC-BY 4.0
---

# 我什么时候能收到第一份 DMARC 聚合报告（RUA）？

1
我什么时候能收到第一份 DMARC 聚合报告（RUA）？
▼

**说明**

聚合报告通常每天生成一次。在 DNS 中发布 DMARC 记录后，请至少等待 24 小时再期待首份报告。报告只会在该周期内确有邮件发往某 DMARC 接收方时才会生成。常见错误是 rua 地址漏写 mailto: 前缀，请检查记录语法。

**建议**

若第二天仍未收到，可向已知启用 DMARC 的接收方地址发一封测试邮件。报告体积可能很大（许多站点限制为 10MB），请确保反垃圾过滤器接受 ZIP 类型大附件及含 ".com" 的文件名，避免被正则规则误拦。

参考：DMARC.org FAQ · RFC 7489 §7.2（RUA）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/dmarc-faq-05.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
