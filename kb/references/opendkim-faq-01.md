---
title: "OpenDKIM 是什么？它如何为邮件做 DKIM 签名与验证？"
source: "https://ztpop.net/kb/opendkim-faq-01.html"
license: CC-BY 4.0
---

# OpenDKIM 是什么？它如何为邮件做 DKIM 签名与验证？

1
OpenDKIM 是什么？它如何为邮件做 DKIM 签名与验证？
▼

**定义**

OpenDKIM 是开源的 DKIM 实现（由早期的 dkim-milter 演进而来），为 Sendmail、Postfix 等邮件传输代理（MTA）提供 DKIM 签名与验证能力，是邮件认证基础设施中最常用的开源组件之一。

**工作机制**

它通过 milter（邮件过滤器）接口挂接到 MTA：对出站邮件在计算好最终消息体后施加 DKIM-Signature 头并用私钥签名；对入站邮件则根据 DKIM-Signature 取 DNS 公钥验证 body hash 与头签名。验证结论写入 Authentication-Results 头的 dkim= 字段。

**标准符合**

OpenDKIM 实现 RFC 6376（DKIM 签名规范），可与 SPF、DMARC 共同构成完整的邮件认证链路。

参考：OpenDKIM 项目文档；RFC 6376（DKIM）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/opendkim-faq-01.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
