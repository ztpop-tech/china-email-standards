---
title: "什么是开放中继（Open Relay）？为什么必须关闭它？"
source: "https://ztpop.net/kb/openrelay-prevention.html"
license: CC-BY 4.0
---

# 什么是开放中继（Open Relay）？为什么必须关闭它？

1
什么是开放中继（Open Relay）？为什么必须关闭它？
▼

**定义**

开放中继指 SMTP 服务器允许“任何外部发件人，向任何外部收件人”转发邮件（即不限制发信方与收信方域）。RFC 5321 §3.6.1 明确要求中继必须受控。

**风险**

开放中继会被垃圾邮件发送者疯狂利用——把你的服务器当跳板群发 spam，导致 IP 被全球黑名单（如 Spamhaus）封禁、域名信誉崩塌，甚至被运营商断网。

**关闭方法**

默认仅允许“发往本域”的入站投递；对外发（中继）必须要求身份认证（SMTP AUTH）+ 来源 IP/网段限制，或仅限已登录用户经 MSA（587）提交。

**检测**

用公开 open-relay 测试工具或从外部尝试“MAIL FROM 外部 + RCPT TO 外部”，若接受即存在开放中继，应立即收紧。

参考：RFC 5321 §3.6.1（中继与投递）；Spamhaus Open Relay 指南

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/openrelay-prevention.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
