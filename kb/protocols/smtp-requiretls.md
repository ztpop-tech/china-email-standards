---
title: "REQUIRETLS（RFC 8689）是什么？它如何强制端到端邮件加密、防止降级？"
source: "https://ztpop.net/kb/smtp-requiretls.html"
license: CC-BY 4.0
---

# REQUIRETLS（RFC 8689）是什么？它如何强制端到端邮件加密、防止降级？

1
REQUIRETLS（RFC 8689）是什么？它如何强制端到端邮件加密、防止降级？
▼

**动机**

即使双方都支持 STARTTLS，机会型协商仍可能被中间人 STRIPTLS 降级为明文，且无法保证整条投递链每一跳都加密。RFC 8689 的 REQUIRETLS 让发件方显式要求“端到端必须 TLS”。

**机制**

发件 MTA 在 MAIL FROM 后加 REQUIRETLS 参数；下游每一跳都必须以 TLS 收/发，且禁止使用明文回落；任何一跳无法提供 TLS 时整条投递失败并回退（而非降级）。这防止了单跳明文泄漏。

**语义保证**

REQUIRETLS 规定接收方不得把邮件以明文转发、不得存储于未加密通道，且要求对 TLS 失败做强处理。它可与 DANE/MTA-STS 协同，进一步校验对端证书，抵抗证书伪造。

**适用**

适用于法务、医疗、金融等敏感邮件，要求全链路机密性；普通批量营销邮件通常不需要，因其会提高投递失败率。运维需在策略层对特定发件域/用户启用，而非全局强制。

参考：RFC 8689（SMTP Requirement for TLS Transmission）；与 DANE（RFC 7672）、MTA-STS（RFC 8461）协同

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/smtp-requiretls.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
