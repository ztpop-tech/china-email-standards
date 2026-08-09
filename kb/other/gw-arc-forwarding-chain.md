---
title: "邮件转发导致 DMARC 失败，ARC 能解决吗？怎么部署？"
source: "https://ztpop.net/kb/gw-arc-forwarding-chain.html"
license: CC-BY 4.0
---

# 邮件转发导致 DMARC 失败，ARC 能解决吗？怎么部署？

**先看清转发为什么会破坏 DMARC**

RFC 7960 系统梳理了间接邮件流带来的互操作问题。转发场景下两条认证路径分别失效：SPF 失效是因为转发后连接来自转发方的 IP，而该 IP 不在原始域的 SPF 授权范围内；DKIM 失效是因为邮件列表等转发方常会修改内容（在主题加前缀、在正文附加页脚、重写头字段），破坏了签名覆盖的内容。

两条都断，DMARC 自然判定为 fail。此时若原始域发布了 reject 策略，最终收件方会拒收——邮件本身完全合法，被拒的原因纯粹是链路结构。

**ARC 做的是「保存现场」，不是「重新认证」**

RFC 8617 定义的 ARC 让每一跳中间方在转发时记录下自己看到的认证结果，并对这份记录签名。核心是三组头字段：`ARC-Authentication-Results`（本跳看到的认证结果，格式沿用 RFC 8601）、`ARC-Message-Signature`（本跳对消息的签名）、`ARC-Seal`（对整条链此前所有 ARC 头的签名，保证链不可被篡改或截断）。

每组头带实例号 `i=`，从 1 递增。最终接收方可以顺着链回溯到第一跳，看到「在被修改之前，这封邮件的 DKIM 是通过的」。

必须明确一点：ARC 只是提供了额外证据，它不强制接收方接受。是否放行取决于接收方是否信任链上的中间方。

**接收侧的判定条件**

验证 ARC 链需要依次确认：链的完整性（实例号连续、每个 ARC-Seal 均验证通过、最新一跳的 `cv=` 值反映了此前链的有效性）、链上各签名域的身份、以及你是否对这些域建立了信任。

判定逻辑应是：DMARC 直接通过则放行；DMARC 失败但存在有效 ARC 链，且链上最早记录了 pass 的那一跳来自你信任的转发方，则可以覆盖 DMARC 的失败处置，转为放行或降级为标记。若链上没有任何可信方，ARC 不提供任何额外信任——攻击者同样可以给伪造邮件加一条自签的 ARC 链。

所以信任列表是 ARC 落地的真正难点，也是它无法「配好就自动生效」的原因。实践上先从明确的内部转发链路与已知合作方的邮件列表开始建立信任，而不是无条件信任任意 ARC 链。

**部署顺序**

分两个角色。作为转发方（你的网关会转发他人邮件、或运营邮件列表）：在修改邮件之前完成入站认证，再按 RFC 8617 追加三组 ARC 头，并保证签名密钥通过 DNS 正确发布。这一侧成本低、收益给下游，应尽早做。

作为最终接收方：先只做验证与记录，把 ARC 链的验证结果写进 `Authentication-Results`，观察一段时间——统计有多少 DMARC 失败的邮件带有有效 ARC 链、这些链来自哪些域。有了这份分布再决定信任哪些方，然后才开启覆盖逻辑。

**不要把 ARC 当作放宽策略的借口**

两个常见误用。其一，为了让转发不失败而把自己域的 DMARC 策略退回 none——这等于放弃了防冒用能力，方向完全错了。其二，无条件信任所有 ARC 链，使 ARC 成为绕过 DMARC 的通道。

正确的定位：ARC 是为「已知的、结构性会破坏签名的合法链路」保留的例外通道，例外必须有名单、有观测、可撤销。同时对本域的转发行为，优先考虑减少对邮件内容的修改（不改主题、不加正文页脚），从源头保住 DKIM 签名有效，这比依赖 ARC 更可靠。

参考：[RFC 7960 Interoperability Issues between DMARC and Indirect Email Flows](https://www.rfc-editor.org/rfc/rfc7960.html) ｜ [RFC 8617 The Authenticated Received Chain (ARC) Protocol](https://www.rfc-editor.org/rfc/rfc8617.html) ｜ [RFC 8601 Message Header Field for Indicating Message Authentication Status](https://www.rfc-editor.org/rfc/rfc8601.html)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/gw-arc-forwarding-chain.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
