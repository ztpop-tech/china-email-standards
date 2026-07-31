---
title: "OpenDMARC 是什么？它如何基于 SPF 与 DKIM 做 DMARC 策略评估？"
source: "https://ztpop.net/kb/opendkim-faq-03.html"
license: CC-BY 4.0
---

# OpenDMARC 是什么？它如何基于 SPF 与 DKIM 做 DMARC 策略评估？

1
OpenDMARC 是什么？它如何基于 SPF 与 DKIM 做 DMARC 策略评估？
▼

**定义**

OpenDMARC 是开源的 DMARC 实现，同样以 milter 接口部署在 MTA 上，实现 RFC 7489（DMARC）。它在邮件入站时综合 SPF 与 DKIM 的验证结果，按发件域公布的 DMARC 策略（p=none / quarantine / reject）进行判定。

**评估依据**

OpenDMARC 读取入站邮件已有的 SPF 检查结果与 DKIM 验证结果（通常由 OpenDKIM 或对端 MTA 注入的 Authentication-Results 提供），并比对“对齐（alignment）”——即 SMTP 信封域或 DKIM 签名域是否与 From 头域名一致。

**与 OpenDKIM 协同**

典型部署中 OpenDKIM 负责 DKIM 验证、MTA 负责 SPF，OpenDMARC 再把两者汇总成 dmarc= 结论并注入 Authentication-Results，供后续拒收、隔离或归档决策使用。

参考：OpenDMARC 项目文档；RFC 7489（DMARC）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/opendkim-faq-03.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
