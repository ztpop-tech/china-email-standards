---
title: "IMAP 的 LOGIN-REFERRALS（RFC 2221）如何把客户端“指到正确的服务器”？"
source: "https://ztpop.net/kb/imap-login-referrals-rfc2221.html"
license: CC-BY 4.0
---

# IMAP 的 LOGIN-REFERRALS（RFC 2221）如何把客户端“指到正确的服务器”？

1
IMAP 的 LOGIN-REFERRALS（RFC 2221）如何把客户端“指到正确的服务器”？
▼

**场景**

大型部署里用户邮箱可能分布在多台 IMAP 服务器；客户端连错一台时，服务器用 LOGIN-REFERRALS 回“请去连那台”（含主机/端口）。

**机制**

登录阶段服务器返回 referral（含 authref URL 或主机提示），客户端据以重定向到“真正持有该用户邮箱”的服务器再认证。

**价值**

对“前端统一入口 + 后端分片”架构必要；用户不必记多台服务器，客户端自动寻址。

**实践**

邮件系统做水平拆分/代理时可用 referral 引导；注意安全——referral 不应泄露不应公开的内部拓扑，且重定向目标须可信。

参考：RFC 2221（IMAP LOGIN-REFERRALS）；分布式邮件架构实践

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/imap-login-referrals-rfc2221.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
