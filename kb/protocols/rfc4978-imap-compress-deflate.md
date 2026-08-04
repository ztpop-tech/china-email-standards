---
title: "RFC 4978 的 IMAP COMPRESS 扩展如何工作，与 TLS 的层序为何重要？"
source: "https://ztpop.net/kb/rfc4978-imap-compress-deflate.html"
license: CC-BY 4.0
---

# RFC 4978 的 IMAP COMPRESS 扩展如何工作，与 TLS 的层序为何重要？

1
RFC 4978 的 IMAP COMPRESS 扩展如何工作，与 TLS 的层序为何重要？
▼

**规范定位（含常见误标澄清）**

RFC 4978 的标题是「The IMAP COMPRESS Extension」，摘要一句话概括其目的：COMPRESS 扩展让 IMAP 连接得以有效且高效地压缩。需要特别澄清的是，这份 RFC 与「二进制 ESMTP」无关——SMTP 侧传输大体量与二进制 MIME 消息的扩展（BDAT / CHUNKING / BINARYMIME）由另一份文档定义。查阅 rfc-editor.org 原文可直接核实这一点，本文按 RFC 4978 的真实主题撰写。

**COMPRESS 命令**

命令参数为压缩机制名称，**目前仅定义了 DEFLATE 一种**。命令本身不产生独立响应，结果分三种：`OK` 表示服务器将压缩其响应并期待客户端压缩其命令；`NO` 表示压缩已由其他层启用；`BAD` 表示命令未知、参数无效或未知，或 COMPRESS 已处于激活状态。

时序规则十分严格：客户端在看到 COMPRESS 的结果之前**不得**发送任何后续命令；若响应为 OK，客户端必须从 COMPRESS 之后的第一条命令起开始压缩；若响应为 BAD 或 NO，客户端**不得**开启压缩。服务器若因已知同一机制已激活（例如 TLS 已协商出相同机制）而返回 NO，必须发送 `COMPRESSIONACTIVE` 作为响应文本码，并宜在响应文本中说明是哪一层在压缩。服务器若返回 OK，必须从结束该带标记 OK 响应的 CRLF 之后立即开始压缩（在 OK 之前发出的响应自然仍是未压缩的）；若返回 BAD 或 NO，则不得开启压缩。就 DEFLATE 而言，压缩方可以在速度与压缩率之间权衡，而解压侧几乎没有这种权衡，因此客户端与服务器都可自行为各自发送的数据选择合适的压缩率。

**与 SASL、TLS 的层序**

这是本扩展最关键的互操作与安全约束：当 COMPRESS 与 TLS 或 SASL 安全层组合使用时，**发送方向的层序必须是——先 COMPRESS，再 SASL，最后 TLS**。即数据在传输前首先被压缩；其次，若已协商 SASL 安全层，则对压缩后的数据做签名与/或加密；再次，若已协商 TLS 安全层，则对上一步的结果做签名与/或加密。接收数据时处理顺序**必须**反过来。这一规定确保了「发送前总是先压缩后加密」，且与客户端发出 COMPRESS、AUTHENTICATE、STARTTLS 三条命令的先后次序无关。

规范给出的登录序列示例中，客户端先 `starttls`（此后一切加密），再 `login`，最后 `compress deflate`（此后一切在加密前先被压缩），直观体现了「命令次序」与「层序」是两回事。

**形式语法与安全考量**

形式语法在 RFC 3501 文法基础上扩充如下：

```
command-auth   =/ compress
compress       = "COMPRESS" SP algorithm
capability     =/ "COMPRESS=" algorithm
                  ;; 允许多个 COMPRESS 能力
algorithm      = "DEFLATE"
resp-text-code =/ "COMPRESSIONACTIVE"
```

由于能力名的语法约束，未来的算法名必须是 atom。IANA 已把 `COMPRESS=DEFLATE` 加入 IMAP 能力列表。

安全考量一节极为简短，原文只写明「同 TLS 压缩」，即指向 RFC 3749。其现实含义不容忽视：在加密通道内先压缩再加密的模式，会使密文长度随明文的可压缩性变化而泄露信息，这正是针对 TLS 压缩的一类已知侧信道风险的根源。运维上应据此评估：在承载敏感内容的 IMAP 连接上启用 COMPRESS 换取带宽收益时，需权衡该侧信道风险，尤其是当同一连接中混有攻击者可部分控制的内容时。

参考：IETF [RFC 4978《The IMAP COMPRESS Extension》](https://www.rfc-editor.org/rfc/rfc4978.txt)（Standards Track，2007-08）；层序安全参见其引用的 [RFC 3749](https://www.rfc-editor.org/rfc/rfc3749.txt)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/rfc4978-imap-compress-deflate.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
