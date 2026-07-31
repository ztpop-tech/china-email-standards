---
title: "如何用 OpenDKIM 验证入站邮件的 DKIM 签名？常见失败原因有哪些？"
source: "https://ztpop.net/kb/opendkim-faq-06.html"
license: CC-BY 4.0
---

# 如何用 OpenDKIM 验证入站邮件的 DKIM 签名？常见失败原因有哪些？

1
如何用 OpenDKIM 验证入站邮件的 DKIM 签名？常见失败原因有哪些？
▼

**验证过程**

OpenDKIM 读取邮件的 DKIM-Signature 头，提取选择器与签名域，向 DNS 查询 <选择器>.\_domainkey.<域> 的 TXT 公钥，随后校验头签名（含指定头字段）与 body hash 是否一致。

**常见失败一：DNS 问题**

签名域的 DKIM 公钥 TXT 记录未发布、格式错误或选择器写错，导致取不到公钥（DNS 查询空/格式异常）。

**常见失败二：内容被改动**

邮件在转发或多网关中转时被改动（如中转网关重写头、自动换行、增加脚注、信体被过滤器重写），会使 body hash 或头签名失配，DKIM 验证失败。

**常见失败三：密钥不一致**

签名用的私钥与 DNS 发布的公钥不是一对（密钥轮转未同步），或密钥已过期。验证结论通过 Authentication-Results 的 dkim= 暴露（none / pass / fail / neutral 等）。

参考：OpenDKIM 官方文档；RFC 6376（DKIM 验证）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/opendkim-faq-06.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
