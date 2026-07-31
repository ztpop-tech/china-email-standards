---
title: "SPF 除了验“信封发件人(Mail From)”，还能验 HELO 身份吗？为何要做 HELO SPF？"
source: "https://ztpop.net/kb/email-spf-helo-check.html"
license: CC-BY 4.0
---

# SPF 除了验“信封发件人(Mail From)”，还能验 HELO 身份吗？为何要做 HELO SPF？

1
SPF 除了验“信封发件人(Mail From)”，还能验 HELO 身份吗？为何要做 HELO SPF？
▼

**双身份**

SPF（RFC 7208）可对两个身份做检查：① Mail From（信封发件域）；② HELO/EHLO 名（发送方自报的主机名）。对“空信封发件人（<>）的退信”只能查 HELO 身份。

**为何 HELO**

退信/DSN 用空发件人，没有 Mail From 域可查，此时用 HELO 名查 SPF（iprev + HELO SPF）判断是否可信源，挡掉伪造 HELO 的垃圾。

**实现**

接收方先 iprev 验证 HELO 名能反解到连接 IP，再用该 HELO 名查 SPF；二者都过才算 HELO 身份可信。

**实践**

正规发送服务器应“HELO 名可反解 + 该名有正确 SPF”，否则其退信/通知易被当成可疑；入站过滤把 HELO SPF 作为信誉信号之一。

参考：RFC 7208 §2.4（HELO 身份的 SPF 检查）；RFC 7208 §4.5（iprev）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-spf-helo-check.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
