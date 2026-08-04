---
title: "RFC 9156 的 DNS QNAME 最小化是什么？对邮件域名解析有何影响？"
source: "https://ztpop.net/kb/rfc9156-dns-qname-minimisation.html"
license: CC-BY 4.0
---

# RFC 9156 的 DNS QNAME 最小化是什么？对邮件域名解析有何影响？

1
RFC 9156 的 DNS QNAME 最小化是什么？对邮件域名解析有何影响？
▼

**先正名：RFC 9156 的真实主题**

需要先澄清一个常见误标：**RFC 9156 的标题是《DNS Query Name Minimisation to Improve Privacy》（通过查询名最小化改善 DNS 隐私），由 ICANN 的 P. Hoffman 等人于 2021 年 11 月发布，并非「邮件可达性」专门文档**。它取代了此前的 RFC 7816。之所以与邮件强相关，是因为 SPF、DKIM、DMARC、MX、MTA-STS、TLSA 等邮件基础设施**全部依赖递归解析器完成大量 DNS 查询**，QNAME 最小化会直接改变这些查询的发出方式与数量，从而影响邮件域名的解析行为与可达性表现。

**核心思想（§2）**

QNAME 最小化的出发点是**把解析器泄露给权威名称服务器的隐私敏感数据降到最低**。传统做法是：解析器无法从缓存作答时，就把**客户端原始的完整 QNAME 与原始 QTYPE**原封不动发给权威服务器。但事实上，**只有对目标记录真正权威的那台服务器才需要完整 QNAME 与 QTYPE**；解析途中被查询的其他服务器只需拿到「足以给出委派（delegation）」的那部分 QNAME 即可，这些服务器上的 QTYPE 毫无意义，因为它们本来就无权威作答。因此，实现 QNAME 最小化的解析器在向「未知是否对原始 QNAME 负责」的权威服务器发查询时，会同时**遮蔽 QNAME 与 QTYPE**：QTYPE 由解析器自行挑选以掩盖原始 QTYPE；QNAME 则裁剪为**「该服务器已知权威的最长匹配域名」再多一个标签**。

**QTYPE 的选择（§2.1）**

本文**放宽了 RFC 7816 中「用 NS 类型掩盖原始 QTYPE」的建议**。用 NS 仍然允许，但并无额外价值：NS 记录的权威在子区一侧，父区面对 NS 查询同样只会像对其他 QTYPE 一样返回引荐（referral）。可用的 QTYPE 是任何「权威始终位于区切割之下」的类型（因此排除 DS、NSEC、NSEC3、OPT、TSIG、TKEY、ANY、MAILA、MAILB、AXFR、IXFR），前提是**所选 QTYPE 与传入 QTYPE 之间不存在关联**。文档推荐 **A 或 AAAA**：它们最不容易在不完整支持所有 QTYPE 的 DNS 软件与中间盒上触发问题，而且能混入非最小化解析器的正常流量中，**使外部更难观察到该解析器正在使用 QNAME 最小化**。

**区切割未知时的逐标签探测（§2.2）**

最小化解析器在**已知区切割位置**时工作得最完美，但区切割并不必然存在于每个标签边界上。以 `www.foo.bar.example` 为例，切割可能存在于 “foo” 与 “bar” 之间，却不在 “bar” 与 “example” 之间。假设解析器已知 `example` 的名称服务器，当收到「`www.foo.bar.example` 的 AAAA 记录是什么」时，它并不知道切割在哪，于是先向 `example` 的名称服务器查 `bar.example`；若得到的是非引荐答复，就**再加一个标签继续查**，如此逐级逼近。

**查询数量上限：性能与攻击面（§2.3）**

这是运维必须重视的一节。收到的 QNAME 标签数会直接影响解析器外发的查询数量，**既构成攻击面，也可能拉低性能**。因此**支持 QNAME 最小化的解析器 MUST 实现「限制每次用户请求外发查询数」的机制**。

文档以 `www.host.group.department.example.com` 为例：若 `host.group.department.example.com` 就托管在 `example.com` 的名称服务器上，非最小化解析器一次查询即可拿到明确引荐或答案；而**冷缓存下的最小化解析器要按标签逐个发查询**（这类深层域名在 `ip6.arpa` 下尤为常见）。缓存预热后差距会缩小。

更危险的是可被主动利用：假设 `*.example.com` 通配记录托管于该域名称服务器，一条含**超过 100 个标签**、以 `example.com` 结尾的查询将导致每个标签一次查询；**攻击者用随机标签即可绕过缓存，迫使解析器持续向上游发出大量查询**。RFC 8198 在部分情况下可缓解此攻击。文档建议的缓解手段之一是：对标签数很多的 QNAME，**每次迭代追加多个标签而非仅一个**，并设定最大迭代次数上限。

**对邮件基础设施的实际影响**

结合上述机制，邮件运维需关注三点：其一，SPF 的 `include`/`a`/`mx`/`exists` 链、DKIM 选择器（`<selector>._domainkey.<domain>`）、DMARC（`_dmarc.<domain>`）、TLS-RPT（`_smtp._tls.<domain>`）、DANE（`_25._tcp.<mx>`）均为**多标签的下划线子域**，在冷缓存下会显著增加迭代查询次数；其二，若上游递归解析器的「每请求查询数上限」设置过紧，这类深层名称的解析可能提前中止，表现为**邮件认证记录「时好时坏」的偶发 temperror**；其三，部分不规范的权威服务器或中间盒对非完整 QNAME 的中间查询响应异常，这也是选用 A/AAAA 作为最小化 QTYPE 的原因之一。排障时应把解析器是否启用 QNAME 最小化、其查询数上限设置一并纳入检查项。

参考：RFC 9156《DNS Query Name Minimisation to Improve Privacy》，https://www.rfc-editor.org/rfc/rfc9156 —— 章节 2 / 2.1 / 2.2 / 2.3 / 3

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/rfc9156-dns-qname-minimisation.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
