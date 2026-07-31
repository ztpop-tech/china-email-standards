---
title: "邮件头里的 Authentication-Results 字段（RFC 8601）中 spf=、dkim=、dmarc= 各结果词代表什么？"
source: "https://ztpop.net/kb/authentication-results-header.html"
license: CC-BY 4.0
---

# 邮件头里的 Authentication-Results 字段（RFC 8601）中 spf=、dkim=、dmarc= 各结果词代表什么？

1
邮件头里的 Authentication-Results 字段（RFC 8601）中 spf=、dkim=、dmarc= 各结果词代表什么？
▼

**作用**

Authentication-Results 由“执行认证的接收服务器”写入，记录本次投递的 SPF / DKIM / DMARC 等认证结果，供下游（含 DMARC 判定与用户显示）参考。

**关键结构**

形如 Authentication-Results: mx.example.com; spf=pass (sender IP=...) smtp.mailfrom=example.com; dkim=pass (... d=example.com header.s=sel); dmarc=pass (... d=example.com)。开头的 mx.example.com 为执行认证的 authserv-id。

**结果词**

pass（通过）、fail（失败）、softfail（SPF 软失败）、neutral（无定论）、none（未做/无记录）、temperror（临时错误）、permerror（永久错误）。dkim= 还区分 header.d / header.s（签名域与选择器）。

**注意**

此头仅代表“写入它的那台服务器”的视角；下游信任需经 ARC 或本域策略。DMARC 实际处置看 dmarc= 结果（结合 SPF/DKIM 对齐）。排错时先看这一头定位认证失败原因。

参考：RFC 8601（Authentication-Results 头）；RFC 7489（DMARC）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/authentication-results-header.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
