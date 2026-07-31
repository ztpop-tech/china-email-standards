---
title: "邮件传输的 TLS 版本该如何“取舍”？为什么应禁用 TLS 1.0/1.1？"
source: "https://ztpop.net/kb/email-tls-version-deprecation.html"
license: CC-BY 4.0
---

# 邮件传输的 TLS 版本该如何“取舍”？为什么应禁用 TLS 1.0/1.1？

1
邮件传输的 TLS 版本该如何“取舍”？为什么应禁用 TLS 1.0/1.1？
▼

**演进**

TLS 1.0/1.1 已因已知弱点（BEAST/POODLE 等）被 RFC 8996 正式废弃；现代应至少 TLS 1.2，优先 TLS 1.3（更快、默认前向安全）。

**邮件侧**

STARTTLS 协商时，MTA 应“只宣告并 accept TLS 1.2+”，对仅支持老版本的对方要么降级明文（不推荐）要么拒——需权衡“安全 vs 可达”。

**现实**

仍有老旧系统只支持 TLS 1.0/1.1；一刀切拒会丢信，故常“最低 TLS 1.2 但保留明文兜底”，并推动对端升级。

**实践**

邮件网关配置“禁用 TLS 1.0/1.1、启用 1.2/1.3、优先 ECDHE 前向安全”；用 TLS-RPT（见 TLS-RPT 篇）监控协商失败，定位需升级的对端。

参考：RFC 8996（弃用 TLS 1.0/1.1）；RFC 8461（TLS-RPT 监控）；RFC 3207（STARTTLS）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-tls-version-deprecation.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
