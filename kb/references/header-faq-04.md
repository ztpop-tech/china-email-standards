---
title: "Authentication-Results 头怎么读（spf= / dkim= / dmarc= / arc=）？"
source: "https://ztpop.net/kb/header-faq-04.html"
license: CC-BY 4.0
---

# Authentication-Results 头怎么读（spf= / dkim= / dmarc= / arc=）？

1
Authentication-Results 头怎么读（spf= / dkim= / dmarc= / arc=）？
▼

**头的来源**

Authentication-Results 由受信任的入站网关/过滤器写入，汇总对这封邮件所做的各项认证结论。其 authserv-id 指明是哪个服务器做出的判定（须是受信任的上游，见 OpenDMARC 的 TrustedAuthRes）。

**结果取值**

常见取值：pass（通过）、fail（失败）、softfail、neutral、none（未做/无策略）、temperror（临时错误）、permerror（永久错误）。

**各方法含义**

spf= 是信封域的 SPF 校验；dkim= 是 DKIM 签名验证；dmarc= 是综合 SPF/DKIM 对齐后的 DMARC 结论；arc= 是 ARC 链式认证（用于邮件经合法转发后仍保留原始认证结论）。

**怎么用**

排查投递/进垃圾箱时，先看 dmarc= 与 dkim=/spf=：若 dmarc=fail 且对端策略为 reject，邮件应被拒收；若 dkim=pass 但域名非声称域名，则显示名不可信。

参考：RFC 7001（Authentication-Results 头）；RFC 7489（DMARC）；RFC 8617（ARC）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/header-faq-04.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
