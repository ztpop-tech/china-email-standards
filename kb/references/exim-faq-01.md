---
title: "Exim 崩溃（crash）了，应该如何排查与上报？"
source: "https://ztpop.net/kb/exim-faq-01.html"
license: CC-BY 4.0
---

# Exim 崩溃（crash）了，应该如何排查与上报？

1
Exim 崩溃（crash）了，应该如何排查与上报？
▼

**原则**

Exim 设计上不应崩溃。作者希望了解每一次崩溃以便诊断修复，但在上报前，请先确认你运行的是最新版 Exim，因为问题可能已被修复。

**排查手段**

若崩溃可复现（例如由某特定邮件触发），保留该邮件副本。可用调试选项定位：用 `exim -d -M 消息ID` 强制投递并输出调试信息；用 `exim -bh 客户端IP` 模拟一次入站 SMTP 会话、查看各项策略检查结果；用 `exim -d -bt 地址` 查看本地地址如何被路由。严重运行问题会写入 paniclog。

参考：Exim FAQ Q0001（exim.org/exim-html-4.40/doc/html/FAQ\_0.html）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/exim-faq-01.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
