---
title: "ARC 由哪三个邮件头字段组成？"
source: "https://ztpop.net/kb/arc-faq-02.html"
license: CC-BY 4.0
---

# ARC 由哪三个邮件头字段组成？

1
ARC 由哪三个邮件头字段组成？
▼

**三件套**

每个 ARC“实例（set）”由三个头字段组成：  
① `ARC-Authentication-Results`（AAR）：复制本跳的 Authentication-Results；  
② `ARC-Message-Signature`（AMS）：类似 DKIM 的签名，覆盖邮件及之前各 ARC set；  
③ `ARC-Seal`（AS）：把 AMS 与 AAR 绑定并对整条链加封。

**作用**

三者配合，使接收方既能验证“链未被篡改”，又能看到“更早的跳是否通过认证”。

参考：RFC 8617 第 4 节（ARC header fields）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/arc-faq-02.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
