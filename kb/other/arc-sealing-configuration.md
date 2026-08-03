---
title: "ARC 封签如何配置？"
source: "https://ztpop.net/kb/arc-sealing-configuration.html"
license: CC-BY 4.0
---

# ARC 封签如何配置？

1
ARC 封签如何配置？
▼

**为什么需要 ARC**

邮件经邮件列表、转发服务或网关时，`Subject`、`From`、信体常被改写，导致原 DKIM 签名失效、SPF 因转发跳转而失配，最终 DMARC 失败被拒收。ARC 让「诚实的中介」把收到的认证结果（含 DKIM/SPF/DMARC）封存下来，向最终接收方证明「此信在被改写前确已通过认证」，从而在被转发后仍可信任。

**三个核心信头**

ARC 由三组数据构成：`ARC-Authentication-Results`（AAR，复制收到时的认证结论）、`ARC-Message-Signature`（AMS，对当时信头/信体做 DKIM 式签名）、`ARC-Seal`（AS，对上述两项及之前所有 ARC 实例做链式签名）。多跳转发时以 `i=` 序号递增形成信任链，每一跳都封前一个跳的 ARC。

**配置要点**

在承担转发/列表角色的 MTA 或列表软件上启用 ARC 封签：生成专属 ARC 密钥对（类似 DKIM 选择器，如 `selector._domainkey` 发布公钥），配置签名域名与选择器，并确保仅在自身确实验证过入信认证后才封签（不可伪造 AAR）。接收方需支持按 AS 链式校验并在 DMARC 失败时回退采信 ARC。ARC 不替代 DMARC，而是为其补上「间接邮件流」的信任传递。

参考：RFC 8617《ARC Authenticated Received Chain》、RFC 6376《DKIM》、RFC 7489《DMARC》。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/arc-sealing-configuration.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
