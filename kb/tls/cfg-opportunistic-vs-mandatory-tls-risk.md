---
title: "机会型 TLS 和强制 TLS 有什么区别？只开 STARTTLS 到底防不防中间人？"
source: "https://ztpop.net/kb/cfg-opportunistic-vs-mandatory-tls-risk.html"
license: CC-BY 4.0
---

# 机会型 TLS 和强制 TLS 有什么区别？只开 STARTTLS 到底防不防中间人？

**STARTTLS 的工作方式**

RFC 3207 给 SMTP 增加了 STARTTLS 扩展：连接先以明文建立，服务器在 EHLO 响应中通告 STARTTLS 能力，客户端发出 STARTTLS 命令后双方再升级为 TLS。协议还要求 TLS 握手完成后，客户端必须丢弃此前从服务器获得的所有信息并重新发送 EHLO，防止明文阶段的通告被复用。

**剥离攻击：问题出在通告本身是明文的**

RFC 3207 的安全考虑章节明确指出了这一风险：由于 EHLO 响应在加密之前传输，处于链路中间的主动攻击者可以把 STARTTLS 能力从响应里删掉。客户端看到对方「不支持 TLS」，便按机会型策略回落到明文继续投递，整封邮件随即以明文暴露。全过程双方都不会报错，这正是它难以被察觉的原因。

**机会型安全的真实边界**

RFC 7435 把这类设计概括为「机会型安全」：在能加密时加密、不能加密时回落到明文，目标是把加密的覆盖面从少数提升到多数。它的价值在于大幅抬高了被动、大规模窃听的成本。但必须清楚它的边界——机会型 TLS 防被动监听，不防有能力改写流量的主动攻击者。把「已开启 STARTTLS」直接写进合规结论、当作传输加密已达标，是常见的误判。

**判定逻辑：你的威胁模型里有没有主动攻击者**

如果威胁模型只包含链路上的被动嗅探，机会型 TLS 基本够用；但只要把「链路可被改写」纳入假设——例如跨境链路、经由不可控中间网络、或传输内容涉及需要强保护的数据——就必须要求可验证且不可降级的 TLS，即强制 TLS。

**升级到强制 TLS 的两条路径**

路径一是 MTA-STS（RFC 8461）：策略经 HTTPS 分发、由 WebPKI 证书背书，发送方缓存策略后拒绝降级；路径二是 DANE（RFC 7672）：TLSA 记录经 DNSSEC 签名，同样使降级可被检测。两者都把「是否加密」从每次连接的临时协商，变成了由收件域预先声明、发送方强制执行的约定，这才是机会型与强制型的本质分界。

**配置层面的常见遗漏**

一是只在入站开了 STARTTLS，出站仍是纯机会型；二是启用了 TLS 但未做服务器身份校验——RFC 7817 更新了邮件场景的身份核对流程，不校验证书名字的加密同样挡不住主动中间人；三是策略只覆盖主 MX，灾备 MX 与第三方代收节点被遗漏，攻击者只需把流量导向弱节点即可绕开。

参考：[RFC 3207 SMTP Service Extension for Secure SMTP over TLS](https://www.rfc-editor.org/rfc/rfc3207.html) ｜ [RFC 7435 Opportunistic Security: Some Protection Most of the Time](https://www.rfc-editor.org/rfc/rfc7435.html) ｜ [RFC 7817 Updated TLS Server Identity Check Procedure for Email](https://www.rfc-editor.org/rfc/rfc7817.html)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/cfg-opportunistic-vs-mandatory-tls-risk.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
