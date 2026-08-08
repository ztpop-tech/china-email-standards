---
title: "邮件经邮件列表转发后 DMARC 校验失败，ARC 链式认证怎么救回来？"
source: "https://ztpop.net/kb/arc-chain-authentication.html"
license: CC-BY 4.0
---

# 邮件经邮件列表转发后 DMARC 校验失败，ARC 链式认证怎么救回来？

1
邮件经邮件列表转发后 DMARC 校验失败，ARC 链式认证怎么救回来？
▼

ARC（RFC 8617）解决的是**「邮件被转发 / 经邮件列表后，SPF 因跳板 IP 失效、DKIM 被改写而 DMARC 失败」**的经典难题。

#### 一、三组新增头部

* `ARC-Authentication-Results`（AAR）：复制该跳板看到的认证结果。
* `ARC-Message-Signature`（AMS）：对原始信头与信体做 DKIM 式签名。
* `ARC-Seal`（AS）：把前面所有 ARC 头一次性密封，形成不可篡改的链。

#### 二、链式序号 i=

每经过一个支持 ARC 的跳板，就追加一组头部，序号 `i=1, i=2, …` 递增。ARC-Seal 既签当前内容，也签前一组 ARC 头，因此**整条链相互绑定**，任何篡改都会令密封失效。

#### 三、接收方怎么判定

当收件方自己的 DMARC 校验失败时，可回退校验 ARC：若最外层 AS 有效、且链中某跳的 AAR 显示原始 DMARC/SPF/DKIM 曾通过，即可**采信该原始结果**，放行经由可信转发路径来的邮件。ARC 本身不校验来源可信度，需配合对转发方的信任策略。

参考：https://www.rfc-editor.org/rfc/rfc8617

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/arc-chain-authentication.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
