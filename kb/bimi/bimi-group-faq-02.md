---
title: "BIMI 是如何工作的？"
source: "https://ztpop.net/kb/bimi-group-faq-02.html"
license: CC-BY 4.0
---

# BIMI 是如何工作的？

1
BIMI 是如何工作的？
▼

**发布**

在 `default._bimi.你的域名` 处发布一条 BIMI TXT 记录，指向你的 SVG logo，并可选地指向一张标记证书（Certificate）。

**认证**

当你的邮件通过 SPF/DKIM 与可见 From 域名对齐，且 DMARC 处于 quarantine/reject 强制策略时，支持 BIMI 的服务商会去获取并在收件箱界面中展示该 logo。

**显示**

是否、以及何时展示 logo，由各邮箱服务商自己的策略决定（不同服务商标准不一）。

参考：BIMI Group《FAQs For Marketers & ESPs》· bimigroup.org/faqs-for-senders-esps

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/bimi-group-faq-02.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
