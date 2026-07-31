---
title: "VBR（RFC 5518）认证者列表是什么？它如何补充 IP/域信誉？"
source: "https://ztpop.net/kb/vbr-certification.html"
license: CC-BY 4.0
---

# VBR（RFC 5518）认证者列表是什么？它如何补充 IP/域信誉？

1
VBR（RFC 5518）认证者列表是什么？它如何补充 IP/域信誉？
▼

**定义**

VBR（Sender Policy Framework 之外的“认证者声誉”，RFC 5518）允许接收方在 SMTP 会话中查询“某发送方是否被权威认证机构（certifier）背书”，如 goodmail、行业认证计划。

**机制**

接收 MTA 在邮件入站时，向 VBR 服务查询该发件 IP/域是否被列于某 certifier 的“好发件人”列表；若被背书，可提升信任、降低 spam 评分或跳过部分过滤。

**价值**

在 IP 信誉（可能共享/漂移）与内容过滤之外，提供“第三方认证”维度，帮助合法批量发件人（新闻、账单）稳定送达；与 SPF/DKIM/DMARC 互补。

**注意**

VBR 依赖认证机构生态，覆盖面有限；它是对“信誉”的补充而非替代发信认证基础（SPF/DKIM/DMARC 仍是必须）。

参考：RFC 5518（VBR 认证者声誉）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/vbr-certification.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
