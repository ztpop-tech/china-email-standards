---
title: "VERP（可变信封返路径）是如何实现精准退信与列表清洗的？"
source: "https://ztpop.net/kb/verp-bounce-processing.html"
license: CC-BY 4.0
---

# VERP（可变信封返路径）是如何实现精准退信与列表清洗的？

1
VERP（可变信封返路径）是如何实现精准退信与列表清洗的？
▼

**原理**

普通群发所有邮件用同一个返路径（MAIL FROM），退信只能回到统一邮箱，难以判断是哪一位收件人不可达。VERP 为每位收件人生成形如 `bounce+user=dst.com@list.com` 的唯一信封发件人；对端退信时按信封返路径寄回，发送方据此精确识别失败的是哪一个订阅者。

**用途**

邮件列表与营销平台用它做自动化清洗：解析退信地址中的 user=domain 部分，对硬退收件人自动移出列表，对软退做重试计数。相比解析正文里的退信码，VERP 鲁棒得多，不受多语言退信模板影响。

**代价与注意**

每收件人一个唯一返路径会使队列中邮件数成倍增加（信封级去重失效），对超大列表有性能与存储开销；需在接收端配通配符地址捕获。发送方自身也必须配置正确的反向解析与认证，避免被当作伪造信封发件人。

参考：VERP 草案（Courier/Postfix 实现说明）、RFC 3464《DSN》退信格式、Postfix VERP 文档。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/verp-bounce-processing.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
