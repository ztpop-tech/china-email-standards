---
title: "Sieve 的 include 扩展（RFC 6609）如何“复用公共规则/分模块管理过滤”？"
source: "https://ztpop.net/kb/email-sieve-include-rfc6609.html"
license: CC-BY 4.0
---

# Sieve 的 include 扩展（RFC 6609）如何“复用公共规则/分模块管理过滤”？

1
Sieve 的 include 扩展（RFC 6609）如何“复用公共规则/分模块管理过滤”？
▼

**机制**

include 扩展允许一个 Sieve 脚本“引入”另一个脚本（全局/个人/必需），实现规则模块化与复用，避免每条规则重复写。

**作用域**

可分 global（管理员发布的公共规则，如公司级拒收/归档）、personal（用户私有片段）；optional/include 控制缺失时是否报错。

**价值**

企业可下发“全局合规规则”让用户脚本 include，统一管理又不剥夺用户自定义；运维改一处全局即生效全部用户。

**实践**

邮件系统若支持 Sieve include，可做“管理员模板 + 用户片段”的分层过滤；注意沙箱与循环 include 防护。

参考：RFC 6609（Sieve Include 扩展）；RFC 5228（Sieve 基础）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-sieve-include-rfc6609.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
