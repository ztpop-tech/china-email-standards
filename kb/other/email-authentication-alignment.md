---
title: "DMARC 标识符对齐（alignment）是什么？SPF/DKIM 的“通过”为何还不足以过 DMARC？"
source: "https://ztpop.net/kb/email-authentication-alignment.html"
license: CC-BY 4.0
---

# DMARC 标识符对齐（alignment）是什么？SPF/DKIM 的“通过”为何还不足以过 DMARC？

1
DMARC 标识符对齐（alignment）是什么？SPF/DKIM 的“通过”为何还不足以过 DMARC？
▼

**对齐含义**

DMARC（RFC 7489）要求“通过”的 SPF 或 DKIM 不仅要自身验证成功，还要与邮件头中的 RFC5322.From 域“对齐”（一致）。对齐分严格（exact match）与宽松（组织域相同）两种，由域策略指定。

**为何需对齐**

SPF 验证的是 envelope-from（Return-Path）域、DKIM 验证的是 d= 签名域，二者都可能与可见的 From 头域不同。攻击者可用自己通过 SPF/DKIM 的域发信，却把 From 伪造成受害者——单独 SPF/DKIM 通过拦不住这种“域不对齐的伪装”。

**两种对齐**

SPF 对齐：envelope-from 域与 From 域对齐；DKIM 对齐：d= 签名域与 From 域对齐。DMARC 只需其中一项“通过且对齐”即算认证通过。未对齐的通过视为无效。

**实践**

部署 DMARC 时先 p=none 收集报告，观察转发场景（如邮件列表会改 envelope-from 但保留 DKIM 或重签）下的对齐率；再逐步收紧到 quarantine / reject，避免误伤合法转发与外包发送。

参考：RFC 7489 §3.1（DMARC 标识符对齐）；SPF（RFC 7208）、DKIM（RFC 6376）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-authentication-alignment.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
