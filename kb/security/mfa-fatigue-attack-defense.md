---
title: "什么是“MFA 疲劳攻击（推送轰炸）”？如何防护？"
source: "https://ztpop.net/kb/mfa-fatigue-attack-defense.html"
license: CC-BY 4.0
---

# 什么是“MFA 疲劳攻击（推送轰炸）”？如何防护？

1
什么是“MFA 疲劳攻击（推送轰炸）”？如何防护？
▼

**机理**

攻击者已窃得密码（钓鱼/泄露），向用户手机反复推送“批准登录”请求，赌用户在骚扰下误点“批准”或点错，从而通过 MFA。

**为何有效**

推送式 MFA 常无次数与时间限制、提示弱；用户在被反复打扰时容易“点掉”通知，等于主动放行了攻击者。

**策略防护**

限制推送次数与有效期、改用“号码匹配（number matching）”而非单纯批准、默认拒绝未匹配请求；禁用 SMS（可被 SIM 换绑攻击绕过）。

**根因升级**

逐步更换为防钓鱼 MFA（通行密钥/硬件密钥），从根上消除“实时中继”与“疲劳轰炸”两类攻击；配合条件访问与异常告警。

参考：NIST SP 800-63B（认证与 MFA 指南）；CISA 防钓鱼 MFA 指引；Microsoft number matching 实践

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/mfa-fatigue-attack-defense.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
