---
title: "ARC-Seal 中的 cv=（chain validation）取值 none / pass / fail 分别代表什么？"
source: "https://ztpop.net/kb/arc-faq-06.html"
license: CC-BY 4.0
---

# ARC-Seal 中的 cv=（chain validation）取值 none / pass / fail 分别代表什么？

1
ARC-Seal 中的 cv=（chain validation）取值 none / pass / fail 分别代表什么？
▼

**cv 取值**

`cv=none`：本跳是链的起点（之前没有 ARC），无法谈“链验证”；`cv=pass`：到本跳为止，前面所有 ARC set 验证通过、链完整；`cv=fail`：前面的链被判定为断裂或无效。

**用途**

接收方读取末跳 AS 的 cv：若为 pass，且链中某可信 hop 的 AAR 显示 DMARC 通过，则可据此对 DMARC 失败的邮件放行。

参考：RFC 8617（cv chain-validation 状态）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/arc-faq-06.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
