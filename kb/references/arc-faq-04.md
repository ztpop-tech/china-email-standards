---
title: "ARC-Message-Signature（AMS）与 ARC-Seal（AS）有什么区别？"
source: "https://ztpop.net/kb/arc-faq-04.html"
license: CC-BY 4.0
---

# ARC-Message-Signature（AMS）与 ARC-Seal（AS）有什么区别？

1
ARC-Message-Signature（AMS）与 ARC-Seal（AS）有什么区别？
▼

**AMS**

AMS 类似 DKIM 签名：对邮件正文/头（含此前所有 ARC set）计算签名，证明“本跳收到并转发的邮件内容未被篡改”。

**AS**

AS 是“封印”：它对 AMS 与本跳 AAR 签名，并把本实例与前一实例链接起来，形成Chain。接收方验证 AS 即可判断整条 ARC 链是否连续、完整。

参考：RFC 8617（AMS 与 AS 头字段）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/arc-faq-04.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
