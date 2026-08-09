---
title: "邮件先过第三方网关再进 Exchange Online，为什么 IP 信誉和 SPF 都失效了？"
source: "https://ztpop.net/kb/cloud-enhanced-filtering-skiplist.html"
license: CC-BY 4.0
---

# 邮件先过第三方网关再进 Exchange Online，为什么 IP 信誉和 SPF 都失效了？

**根因：EOP 看到的「发件人」变成了你的网关**

邮件先到第三方网关、再由网关投给云端时，云端在 TCP 层面看到的连接来源**是你的网关 IP，而不是真实发送方**。由此连带失效的有：

* **连接筛选与 IP 信誉：**所有邮件看起来都来自同一个可信 IP，基于来源信誉的判定完全失去区分度。
* **SPF 校验：**SPF 校验的是**连接 IP 是否被发件域授权**。此时连接 IP 是你的网关，几乎所有外部域的 SPF 都会失败。
* **连带 DMARC：**SPF 侧失败后，DMARC 只能靠 DKIM 支撑；对方若未配 DKIM，DMARC 也随之失败。

典型表现是：接入前置网关后，大量正常邮件的认证结果集体变差，垃圾判定准确率明显下降。

**解法：增强筛选让 EOP 回溯真实源 IP**

增强筛选（也称跳过列表）的作用是**告诉云端「这些 IP 是我自己的中间跳，请忽略它们，继续往前找真正的外部来源」**。

云端据此解析接收链，跳过被声明的中间节点，把回溯到的那一跳当作真实来源，重新执行连接筛选与 SPF 判定。判据由此恢复有效。

**两种配置方式的选择**

* **按 IP 列举（推荐）：**明确列出你的网关全部出口 IP。精确、可控，网关扩容时需同步更新。
* **按跳数跳过：**指定跳过最后 N 跳。配置简单，但**前提是路径跳数绝对固定**——一旦网关侧新增或减少一个节点，回溯就会落在错误的位置，可能把某个中间节点当成真实来源。

能列 IP 就不要用跳数。跳数方式的失效是静默的，不会报错。

**配置后必须验证，且要验两个方向**

**正向验证：**找一封来自已知配置了正确 SPF 的外部域的邮件，确认其认证结果恢复为 `spf=pass`，且平台识别出的来源 IP 是真实外部 IP 而非你的网关 IP。

**反向验证（更重要）：**构造或找到一封**本应被判定失败**的邮件（例如来自未授权 IP 的伪造），确认它现在能被正确判失败。

只做正向验证的风险在于：配置错误可能表现为「一切都 pass」——那不是配好了，而是判定被整体绕过了。

**三个高频配置错误**

* **只列了部分网关 IP：**网关有多个出口时漏列，表现为部分邮件恢复正常、部分依旧异常，排查时极易误判为随机故障。
* **把不属于自己的 IP 列入跳过：**相当于声明「这个外部节点不算来源」，会让攻击者可以通过该节点绕过来源判定。**跳过列表里只能出现你自己控制的节点。**
* **连接器作用域与跳过配置不匹配：**跳过设置生效于特定连接器，若邮件实际走的是另一条连接器，配置不会生效。

**架构层面的取舍**

增强筛选是**补救措施**，它恢复了判据但没有消除链路复杂度。在决定是否保留前置网关时，值得重新评估：

* 前置网关提供的能力，云端是否已经覆盖？重复投入的部分能否精简？
* 两层过滤各自的隔离区是否都有人看？**两个互不相通的隔离区是运维负担的主要来源**，也是误报长期得不到处理的根源。
* 邮件流排查是否需要同时查两套日志？这会显著拉长故障定位时间。

参考：[Microsoft Learn：Enhanced Filtering for Connectors](https://learn.microsoft.com/en-us/exchange/mail-flow-best-practices/use-connectors-to-configure-mail-flow/enhanced-filtering-for-connectors)、[Microsoft Learn：Configure connection filtering](https://learn.microsoft.com/en-us/defender-office-365/connection-filter-policies-configure)、[RFC 7208：Sender Policy Framework (SPF), Version 1](https://www.rfc-editor.org/rfc/rfc7208.html)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/cloud-enhanced-filtering-skiplist.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
