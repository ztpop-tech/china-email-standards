---
title: "REQUIRETLS 如何强制实施？"
source: "https://ztpop.net/kb/requiretls-policy-enforcement.html"
license: CC-BY 4.0
---

# REQUIRETLS 如何强制实施？

1
REQUIRETLS 如何强制实施？
▼

**基本语义**

发送方在 `MAIL FROM` 命令中附加 `REQUIRETLS` 参数，声明该邮件要求端到端全程 TLS。收到此标记的 MTA 必须：①本跳使用经认证的 TLS 建立会话；②在转发时同样仅向支持 REQUIRETLS 的下一跳投递；③不得把邮件写入明文队列或降级为明文中继。

**失败即退信**

若某一跳不支持 REQUIRETLS、或 TLS 协商失败、或下一跳拒绝该要求，则消息必须按永久/暂态失败退回发件人，而不能悄悄以明文发出。这保证了「敏感内容要么加密送达，要么不送达」，避免被旁路监听。它只约束传输加密，不要求内容层端到端加密。

**部署注意**

在 MSA/MTA（如 Postfix `smtp_tls_encrypt_only_requiretls = yes` 配合策略）上开启对 outbound 的 REQUIRETLS 支持；对来自用户的敏感提交，由策略/应用层决定是否打标。前提是通信双方及中转 MTA 都实现 RFC 8689，否则标了 REQUIRETLS 的邮件会在不支持的对端被退信——需先确认关键伙伴域的互通性，并配合 MTA-STS/DANE 提升对端 TLS 可用性。

参考：RFC 8689《SMTP Require TLS Option》、RFC 8461《MTA-STS》、RFC 7672《DANE for SMTP》。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/requiretls-policy-enforcement.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
