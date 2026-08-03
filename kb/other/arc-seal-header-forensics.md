---
title: "ARC-Seal 信头在邮件取证中如何应用？"
source: "https://ztpop.net/kb/arc-seal-header-forensics.html"
license: CC-BY 4.0
---

# ARC-Seal 信头在邮件取证中如何应用？

1
ARC-Seal 信头在邮件取证中如何应用？
▼

**为何需要 ARC**

邮件经邮件列表、转发服务等中介后，原始 DKIM 签名可能因信头改写而失效、发件 IP 改变使 SPF 失配，DMARC 随之失败。ARC 在转发前由可信中介把**当时的认证结果**做链式签名固化下来，让最终接收方即便原始校验失败，也能参考 ARC 携带的历史结论。

**三段信头**

* `ARC-Authentication-Results (AAR)`：复制转发时的 Authentication-Results；
* `ARC-Message-Signature (AMS)`：对邮件头部与正文做的签名；
* `ARC-Seal (AS)`：对前述 AAR、AMS 及上一跳 AS 整体密封，形成链式信任。

**取证核验方法**

取证时按 `i=` 实例号从大到小核对：验证最新 AS 是否覆盖其 AAR/AMS 且能链回上一跳 AS，全部验签通过则证明转发路径未被篡改，原始认证结论可信。示例：`ARC-Seal: i=1; a=rsa-sha256; t=...; cv=none; d=lists.x.com; s=arc; b=...`，其中 `cv=` 为链验证状态（none/pass/fail）。

参考：RFC 8617《Authenticated Received Chain (ARC)》、RFC 6376 DKIM、RFC 7489 DMARC。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/arc-seal-header-forensics.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
