---
title: "邮箱“自动转发”为何会被滥用？如何检测与限制？"
source: "https://ztpop.net/kb/email-auto-forwarding-abuse.html"
license: CC-BY 4.0
---

# 邮箱“自动转发”为何会被滥用？如何检测与限制？

1
邮箱“自动转发”为何会被滥用？如何检测与限制？
▼

**风险**

攻击者攻陷邮箱后悄悄建立“自动转发规则”，把邮件（含验证码与机密）副本发到外部，长期潜伏窃密；也可借此绕过 MFA（把重置码转走）。

**手法**

通过 IMAP/收件箱规则、Exchange 收件箱规则或“中转别名”把敏感信转发到攻击者邮箱；用户往往不自知。

**检测**

定期审计转发规则与收件箱规则；监控“向新外部域外发”的异常转发；用 CASB/邮件安全网关对“自动转发到外部”告警或默认阻断。

**实践**

默认禁止或审批“转发到外部域”；必须转发者限定目标白名单；账号异常时批量清理规则；启用登录告警与 MFA。

参考：NIST SP 800-53（AC / AU 控制）；CISA 账户接管防护；Exchange Online / Gmail 转发规则审计实践

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-auto-forwarding-abuse.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
