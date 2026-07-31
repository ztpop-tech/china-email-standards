---
title: "DKIM 签名是如何生成的？一次签名的完整流程（RFC 6376）是怎样的？"
source: "https://ztpop.net/kb/dkim-signature-process.html"
license: CC-BY 4.0
---

# DKIM 签名是如何生成的？一次签名的完整流程（RFC 6376）是怎样的？

1
DKIM 签名是如何生成的？一次签名的完整流程（RFC 6376）是怎样的？
▼

**准备**

发送域发布选择器公钥于 DNS（.\_domainkey. TXT，含 p=公钥、k=算法等标签）；签名端持有对应私钥。

**规范化**

RFC 6376 定义两种规范化（simple/relaxed）分别作用于 header 与 body；body 先按算法（sha256）哈希，头部按选定头字段列表哈希，二者组合成待签数据。

**签名**

用私钥对“body hash + 头 hash”签名，生成 DKIM-Signature 头（含 v、a=rsa-sha256、c=规范化、d=域、s=选择器、bh=body hash、h=参与签名的头列表、b=签名值）。

**验证**

接收方查 DNS 取公钥，重算 body/头哈希并与 bh/b 比对；任一不符即验证失败。签名覆盖的头（h=）越全越抗篡改，但越易因中转改写失效（故常用 relaxed）。

参考：RFC 6376 §3（DKIM-Signature 头）；§5（验证）；§3.4/3.5（规范化与哈希）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/dkim-signature-process.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
