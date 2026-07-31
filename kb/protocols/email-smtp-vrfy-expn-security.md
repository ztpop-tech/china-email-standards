---
title: "SMTP 的 VRFY / EXPN 命令为何常被“禁用”？它们泄露了什么？"
source: "https://ztpop.net/kb/email-smtp-vrfy-expn-security.html"
license: CC-BY 4.0
---

# SMTP 的 VRFY / EXPN 命令为何常被“禁用”？它们泄露了什么？

1
SMTP 的 VRFY / EXPN 命令为何常被“禁用”？它们泄露了什么？
▼

**命令**

VRFY 查询“某地址是否为有效邮箱”，EXPN 展开“某邮件列表有哪些成员”；本为方便，但会泄露用户/成员名单。

**风险**

攻击者用 VRFY 枚举有效账号做暴力破解或社工；EXPN 泄露内部通讯录/列表成员；是信息泄露面。

**处置**

多数现代 MTA 默认禁用或返回“不可枚举”（如 252 但不给真实信息）；公网入站尤其应关，内部可酌情保留。

**实践**

邮件系统安全加固清单必含“关 VRFY/EXPN 对外暴露”；排错用日志而非开放这些命令；合规也常要求不暴露账号枚举面。

参考：RFC 5321 §4.1.1（VRFY/EXPN 语义）；安全加固实践

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-smtp-vrfy-expn-security.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
