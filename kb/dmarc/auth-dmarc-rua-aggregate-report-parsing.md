---
title: "DMARC 聚合报告（RUA）该怎么读？XML 里哪些字段最能说明问题？"
source: "https://ztpop.net/kb/auth-dmarc-rua-aggregate-report-parsing.html"
license: CC-BY 4.0
---

# DMARC 聚合报告（RUA）该怎么读？XML 里哪些字段最能说明问题？

1
DMARC 聚合报告（RUA）该怎么读？XML 里哪些字段最能说明问题？
▼

**报告从哪来、多久一份**

RFC 7489 第 7.2 节（Aggregate Reports）规定，聚合报告用于向域名所有者提供其域被使用情况的精确视图。报告由接收方按周期生成并发送到 `rua` 指定的地址；周期由 `ri` 标签建议，常见为一天一份。

**注意：**报告是**按接收方组织分别出具**的，同一天你会收到多份来自不同接收方的报告。分析时必须先按报告来源分开看，再做汇总，否则容易把某一家的策略特性误当成全网现象。

**报告的三层结构：先搞清楚在看哪一层**

按第 7.2 节与附录 C（DMARC XML Schema）定义的结构，一份报告自上而下是：

* **报告元数据**（report\_metadata）：出报告的组织、报告 ID、时间范围。**先看时间范围**，避免把两个不同窗口的数据混算。
* **被评估的策略**（policy\_published）：接收方当时读到的你的记录内容——域名、`p`、`sp`、`adkim`、`aspf`、`pct`。
* **记录集合**（record）：按源 IP 聚合的行，每行含消息数量、评估结果与各机制的原始结果。

**实用技巧：**policy\_published 是「接收方眼中的你」。如果它和你以为自己发布的记录对不上，说明 DNS 变更未生效或存在解析差异，这比分析后面的数据更优先。

**最关键的对照：policy\_evaluated 与 auth\_results**

每条 record 里有两组结果，混淆二者是读报告最常见的错误：

* **auth\_results**：SPF 与 DKIM 的**原始校验结果**，含各自校验的域名（DKIM 的 `d=`、SPF 的信封域）。
* **policy\_evaluated**：DMARC 层的**对齐后结论**（dkim / spf 各自是否算通过）与实际处置（disposition）。

**诊断黄金组合：**当 auth\_results 显示 SPF 为 pass，而 policy\_evaluated 中 spf 为 fail，几乎可以断定是**对齐问题**而非 SPF 配置问题——信封发件人域与 From 域不一致。这一条对照能解决大部分排障。

**按源 IP 归类：三桶分类法**

把所有 record 按源 IP 分成三桶，是最高效的分析方式：

1. **已知且通过。**自有出口与已纳管的第三方，DMARC 通过。这部分只需监控数量是否骤变。
2. **已知但失败。**能认出是自家或合作方的源，但对齐失败。**这是待办工作清单**——补 DKIM 签名或修正信封域，逐个清零。
3. **未知且失败。**完全不认识的源在用你的域发信。若数量持续且分散，通常指向冒用。**这一桶正是收敛策略要压制的对象。**

**推进原则：**只有当第二桶清空、第三桶稳定可解释时，才具备收紧策略的条件。

**处理建议与常见坑**

* **报告是压缩附件**，解析前先解压；建议入库后按周做趋势图，单看一天极易被偶发流量误导。
* **数量字段是消息条数**，不是会话数，做占比统计时要以它为权重，否则会被大量小流量源稀释判断。
* **接收方覆盖度有限。**只有实现了 DMARC 报告的接收方才会出报告，因此报告反映的是「部分视图」，不能当作发送总量。
* **rua 指向外部域时需授权。**RFC 7489 第 7.1 节（Verifying External Destinations）要求接收方验证外部报告地址的接收意愿，若报告地址不在本域下，必须在目标域配置相应的授权记录，否则收不到报告。

参考：[RFC 7489 Domain-based Message Authentication, Reporting, and Conformance (DMARC)](https://www.rfc-editor.org/rfc/rfc7489.txt)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/auth-dmarc-rua-aggregate-report-parsing.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
