---
title: "TXT 记录除了 SPF 还能放什么？SPF 的 255 字符与串接限制是什么？"
source: "https://ztpop.net/kb/dnsmail-faq-04.html"
license: CC-BY 4.0
---

# TXT 记录除了 SPF 还能放什么？SPF 的 255 字符与串接限制是什么？

1
TXT 记录除了 SPF 还能放什么？SPF 的 255 字符与串接限制是什么？
▼

**TXT 的多用途**

DNS 的 TXT 记录用于存放任意文本，邮件场景中最常见的是 SPF（v=spf1 …）、DKIM（selector.\_domainkey 的 p= 公钥）、DMARC（\_dmarc 的 v=DMARC1）、MTA-STS（\_mta-sts 的策略）以及 BIMI（\_bimi 的 VMC 指针）等。

**SPF 的 255 字符限制**

单条 TXT 记录的字符串段传统上限为 255 字符。较长的 SPF 策略可用多条带引号字符串“串接”成一个值（如 “v=spf1 …” “include:…”），解析时拼接为一条；但单段不能超过 255 字符。

**10 次 DNS 查询上限**

SPF 评估对 DNS 查询次数有上限（通常 10 次，含 include/redirect/a/mx 等机制累计），超出即评结果为 permerror。因此应避免过深的 include 嵌套，并合并重复机制。

参考：RFC 7208（SPF，TXT 与查询上限）；RFC 6376/7489（DKIM/DMARC TXT）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/dnsmail-faq-04.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
