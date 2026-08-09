---
title: "Exchange Online 为什么必须为自定义域启用 DKIM？两条 selector CNAME 有什么用？"
source: "https://ztpop.net/kb/cloud-m365-dkim-selector.html"
license: CC-BY 4.0
---

# Exchange Online 为什么必须为自定义域启用 DKIM？两条 selector CNAME 有什么用？

**默认状态下签名域与 From 域不对齐**

租户未对自定义域启用 DKIM 时，出站邮件仍会被签名，但签名域（DKIM-Signature 的 `d=` 标签）是租户的初始域，而不是你实际对外使用的发件域。

后果很具体：DMARC 要求通过校验的机制与 **From 头部域**对齐。`d=` 与 From 域不一致 ⇒ **DKIM 侧无法为 DMARC 提供对齐通过**，整个 DMARC 判定只能靠 SPF 一条腿撑着。

**单靠 SPF 的致命场景：转发**

这是必须启用 DKIM 的核心运维理由。邮件被转发时（邮件列表、用户设置的自动转发、合作方内部再分发），最后一跳的发送 IP 变成了转发方的服务器，**SPF 几乎必然失败**。

而 DKIM 签名覆盖的是邮件头与正文本身，只要转发过程没有改写被签名的内容，签名在多跳之后依然可验证。SPF 与 DKIM 在 DMARC 下是「或」的关系——有 DKIM 兜底，转发才不会把你的邮件打成 DMARC 失败。

**两条 selector CNAME 的作用是密钥轮转**

启用自定义域 DKIM 时需要在 DNS 发布**两条** CNAME 选择器记录，指向托管的密钥。很多人只发布一条就以为完事，这会在轮转时出事。

**机制：**任一时刻只有一个 selector 在实际签名，另一个是待命位。轮转时新密钥在待命 selector 上生效，签名切换过去，旧 selector 退为待命。两条都存在，才能做到**轮转期间签名不中断、且在途邮件仍可验证**——因为收件方可能在几小时甚至几天后才去查询公钥。

**对齐模式：relaxed 与 strict 的实际差别**

DMARC 的 DKIM 对齐有两档。`adkim=r`（relaxed，默认）只要求 `d=` 与 From 域属于同一组织域，因此 `mail.example.com` 签名可以为 `example.com` 的 From 对齐；`adkim=s`（strict）要求完全一致。

**建议：**存在子域发信的组织先用 relaxed 落地，不要一上来就 strict，否则子域发送源会被判为不对齐。

**验证是否真的生效**

不要只看门户里的开关状态，要看实际邮件头。取一封外发邮件，检查接收方写入的 Authentication-Results（RFC 8601 定义的头部），确认同时满足：

* 存在 `dkim=pass`；
* 其 `header.d=` 的值是**你的自定义发件域**，而不是租户初始域；
* `dmarc=pass`，且对齐来源包含 DKIM。

三条同时成立，才算真正配好。只满足第一条属于典型的「假通过」。

**旁路发送源同样需要签名**

租户内的邮件由平台签名，但用你的域对外发信的第三方平台不会自动获得这个能力。每个第三方发送源都需要单独完成 DKIM 配置（各自的 selector 与公钥记录）。

遗漏的表现是：日常办公邮件 DMARC 全绿，唯独营销或系统通知邮件持续失败。排查时按 `d=` 的取值就能立刻定位是哪一路。

参考：[Microsoft Learn：Set up DKIM to sign mail from your Microsoft 365 domain](https://learn.microsoft.com/en-us/defender-office-365/email-authentication-dkim-configure)、[RFC 6376：DomainKeys Identified Mail (DKIM) Signatures](https://www.rfc-editor.org/rfc/rfc6376.html)、[RFC 8601：Message Header Field for Indicating Message Authentication Status](https://www.rfc-editor.org/rfc/rfc8601.html)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/cloud-m365-dkim-selector.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
