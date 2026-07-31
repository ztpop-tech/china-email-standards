---
title: "SMTP 问候横幅（Greeting Banner）检查是什么？为何它能过滤垃圾源？"
source: "https://ztpop.net/kb/smtp-greeting-banner.html"
license: CC-BY 4.0
---

# SMTP 问候横幅（Greeting Banner）检查是什么？为何它能过滤垃圾源？

1
SMTP 问候横幅（Greeting Banner）检查是什么？为何它能过滤垃圾源？
▼

**定义**

服务器在 TCP 连接建立、客户端发 EHLO/HELO 前，先回一行 220 横幅（banner），通常含主机名与软件标识。横幅检查是反垃圾的第一道关卡。

**检查项**

反垃圾设备常校验：横幅中的主机名是否与该 IP 的正向/反向解析（FCrDNS）一致；是否暴露过多版本信息（易被指纹攻击）；是否在黑名单 IP 上。不一致/暴露过多的主机更易被判为可疑。

**建议**

横幅用真实、与 PTR 一致的主机名；不要暴露详细版本/补丁号；保持 220 后换行规范，避免被误判为非常规 SMTP 实现。

**价值**

横幅与 FCrDNS 一致是“合法邮件服务器”的基础信号，能挡掉大量僵尸/动态 IP 垃圾源，是信誉第一印象。

参考：RFC 5321 §4.3.1（220 横幅）；FCrDNS 实践

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/smtp-greeting-banner.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
