---
title: "发现某同事邮箱被入侵（自动转发、可疑收件箱规则、已发垃圾邮件），按什么顺序处置？"
source: "https://ztpop.net/kb/compromised-account-incident-response.html"
license: CC-BY 4.0
---

# 发现某同事邮箱被入侵（自动转发、可疑收件箱规则、已发垃圾邮件），按什么顺序处置？

1
发现某同事邮箱被入侵（自动转发、可疑收件箱规则、已发垃圾邮件），按什么顺序处置？
▼

**先识别：常见被入侵症状**

Microsoft 列出与 Microsoft 365 邮箱关联账户可能已被入侵的症状：邮箱被禁止发信；可疑活动（如邮件丢失或删除）；可疑收件箱规则（自动转发到未知地址、或把邮件移到 Notes/Junk Email/RSS Subscriptions 文件夹）；已发送/已删除文件夹含可疑邮件；全局地址列表（GAL）中该用户的联系人被改（姓名、电话、邮编）；频繁改密码或莫名锁户；近期新增外部邮件转发；可疑邮件签名（如虚假银行或处方药签名）。出现任一项都应启动处置流程。

**立即遏制：先断访问**

Microsoft 强调：攻击者获得访问后，需尽快阻断该账户访问。Step 1 首选**禁用受影响用户账户**（调查期间保持禁用），无法禁用时再重置强密码（大小写+数字+特殊字符、不要经邮件把新密码发给用户、不用最近 5 次用过的密码、AD 同步账户需在 AD 中重置两次以缓解 pass-the-hash），并强烈建议启用并强制 MFA。Step 2 撤销用户访问：通过 Microsoft Graph PowerShell 执行 Revoke-MgUserSignInSession，立即使所有活动登录会话与刷新令牌失效，防止攻击者继续访问或操作。

**修复：Step 3 到 Step 6**

依次：Step 3 审查受影响用户的 MFA 注册设备，移除攻击者添加的可疑设备与未识别的 MFA 方法；Step 4 审查用户已授予同意的应用，移除不应允许的；Step 5 审查分配给用户的管理员角色，移除不应允许的；Step 6 审查邮件转发，移除攻击者添加的转发（检查 Get-Mailbox 的 ForwardingAddress/ForwardingSmtpAddress，以及 Get-InboxRule -IncludeHidden 中的隐藏重定向规则）。

**调查与收尾**

调查需查 Microsoft Entra 登录日志（IP、位置、时间、成败）、Azure 审计日志、Defender 门户审计日志、Defender 的 Message Trace 核验已发邮件。调查完成后：若期间禁用了账户，则重置密码并重新启用（按 Step 1）；若账户曾发垃圾导致被禁发，需把该用户从 Restricted entities 页面移除。

参考：https://learn.microsoft.com/en-us/defender-office-365/responding-to-a-compromised-email-account

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/compromised-account-incident-response.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
