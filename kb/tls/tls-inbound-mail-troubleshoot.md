---
title: "对方说邮件发不进来、报 TLS 错误，入站 TLS 该怎么一步步排查？"
source: "https://ztpop.net/kb/tls-inbound-mail-troubleshoot.html"
license: CC-BY 4.0
---

# 对方说邮件发不进来、报 TLS 错误，入站 TLS 该怎么一步步排查？

1
对方说邮件发不进来、报 TLS 错误，入站 TLS 该怎么一步步排查？
▼

**第一步：确定故障发生在哪一层，三条路径不要混**

「TLS 报错」这个描述本身没有定位价值，因为邮件系统里至少有三处独立的 TLS：

* **MTA 之间（25 端口，STARTTLS）。**由 RFC 3207 定义。**本质上是机会性的**——协商不成功通常会退回明文继续投递，而不是失败。因此这一层的「TLS 错误」往往表现为投递延迟或降级，而不是明确的拒绝。
* **用户提交（587 或 465）。**RFC 8314 要求提交与访问强制使用 TLS。**这一层的 TLS 失败会导致明确的、用户可见的发信失败。**
* **客户端访问（IMAP、POP）。**同样受 RFC 8314 约束，失败表现为客户端无法收信。

**定位问题的第一个提问是：报错的是对方的邮件服务器，还是某个用户的邮件客户端？**前者是第一层，后者是第二、三层。这两类问题的排查路径几乎没有交集，混起来查会浪费大量时间。

本文聚焦第一层，也就是外部 MTA 向你投递时的 TLS 问题，因为它最难排查——**失败发生在对方的系统上，你看不到，通常只能等对方来告诉你。**

**理解机会性 TLS 的性质，否则会误判故障**

RFC 3207 定义的 STARTTLS 是在已建立的明文 SMTP 会话中协商升级到 TLS。它的关键性质是：**协商失败时，发送方通常可以选择继续以明文投递。**这带来两个排查上的直接后果：

1. **「邮件还是收到了」不等于「TLS 正常」。**可能只是降级成明文了。**如果你的合规要求包含传输加密，那么「能收到邮件」根本不是验收标准。**
2. **真正会导致投递失败的，往往不是 STARTTLS 本身，而是叠加在其上的强制机制。**

强制机制主要有三种，排查时必须先确认对方或你自己启用了哪一种：

* **MTA-STS（RFC 8461）。**通过 DNS 记录与 HTTPS 上发布的策略文件，声明本域要求发送方使用经过验证的 TLS。**如果你的 MTA-STS 策略与实际证书或 MX 配置不一致，遵守该策略的发送方会直接投递失败**——而不遵守的发送方毫无感觉。这解释了一类典型现象：只有部分大型服务商发不进来。
* **DANE（RFC 7672 与 RFC 6698）。**通过 DNSSEC 保护的 TLSA 记录绑定证书。**它的失败模式更严格**：TLSA 记录与实际证书不匹配时，支持 DANE 的发送方会拒绝投递。**换证书时忘记同步更新 TLSA 记录，是这一机制最典型的事故。**
* **发送方要求（RFC 8689）。**SMTP Require TLS 选项允许发送方明确要求不得降级。这改变的是失败语义：**宁可不投递，也不明文发送。**

**排查时先问清楚对方用的是哪一种**，因为三者的失败原因定位方向完全不同。

**六步排查顺序：从外向内，逐层收敛**

1. **DNS。**确认 MX 记录指向的主机名都能正确解析到 A 或 AAAA 记录。**常见问题：MX 指向的主机名有拼写错误、指向了已下线的主机、或者存在多条 MX 而其中低优先级的那条早已失效。**另外确认本域没有误配 RFC 7505 定义的 Null MX 记录——该记录用于声明本域不接收任何邮件。如果启用了 MTA-STS 或 DANE，还要检查对应的 DNS 记录与策略文件是否可达且内容正确。
2. **连通性。**从外部网络确认目标端口可达。**注意要从多个不同的外部网络测**——某些运营商或云厂商的出向策略会造成部分来源不可达，而这类问题从单一测试点看不出来。
3. **能力宣告。**建立 SMTP 会话后，确认服务器在 EHLO 响应中宣告了 STARTTLS。**如果没有宣告，问题在服务端配置，与证书无关，可以立即收敛排查范围。**注意有些配置会在特定条件下不宣告 STARTTLS，例如证书加载失败时静默降级。
4. **握手。**确认协议版本与密码套件能达成一致。**这是双方策略交集为空时的失败点。**
5. **证书链。**确认服务器发送了完整的证书链，包括必要的中间证书。
6. **名称匹配。**RFC 7817 更新了邮件相关协议中 TLS 服务器身份校验的做法。要确认证书上的名称与发送方连接时使用的名称（通常是 MX 记录中的主机名）匹配。

**这个顺序不能打乱。**每一步失败都会让后面的步骤表现出误导性的症状——例如 DNS 指向了错误的主机时，你会在那台错误主机上看到一个「证书不匹配」的问题，然后在错误的方向上排查很久。

**高频根因清单：先查这几个**

* **中间证书缺失。**这是排名第一的根因，且具有极强的迷惑性：**你自己测试时一切正常，因为你的测试机器本地信任库里恰好有那张中间证书；而对方的系统没有，于是链验证失败。**验证方法是用一个干净的、不含额外中间证书的环境测试，或使用会明确报告链完整性的工具。
* **证书过期或即将过期。**基础但常见，尤其是自动续期机制部署后无人验证是否真正生效的情况。**监控应当覆盖所有对外的 MX 主机，而不只是网站证书。**
* **协议版本策略不兼容。**RFC 8996 已将 TLS 1.0 与 TLS 1.1 弃用，现代系统普遍不再支持。如果对方是长期未更新的老系统而只支持这些版本，握手会失败。**这种情况的正确处理是推动对方升级，而不是为其重新启用已弃用的版本。**RFC 9325 给出了 TLS 与 DTLS 的安全使用建议，RFC 8446 定义了 TLS 1.3，可作为配置基线的依据。
* **密码套件交集为空。**过度收紧的套件配置遇上老旧客户端时会出现。收紧配置时应当有观察期，而不是直接切换。
* **SNI 与证书不匹配。**一台主机承载多个域时，若 SNI 处理不当会返回默认证书，造成名称不匹配。
* **负载均衡器与后端策略不一致。**TLS 在均衡器终结时，实际生效的是均衡器上的配置，而运维往往在检查后端服务器的配置。**要确认自己检查的是真正对外提供 TLS 的那一层。**
* **多台 MX 主机配置漂移。**只有其中一台配置不一致时，故障表现为「时好时坏」，极难定位。**凡是出现间歇性 TLS 故障，第一件事就是逐台核对所有 MX 主机的配置与证书。**
* **MTA-STS 或 DANE 与实际配置不同步。**换证书、加主机、改 MX 之后忘记同步策略或 TLSA 记录。**这应当被写进变更清单，作为强制项。**

**用 TLS 报告把被动救火变成主动发现**

上述所有排查都有一个共同前提：**你已经知道出问题了。**而在机会性 TLS 的世界里，降级是静默的——对方降级成明文投递，邮件正常送达，没有任何人会来告诉你。

RFC 8460 定义的 SMTP TLS Reporting 解决的正是这个问题：**它让发送方把自己在与你建立 TLS 时遇到的成功与失败情况，以结构化报告的形式发回给你。**这意味着你能从对方的视角看到自己的问题，而不必等对方的运维恰好有空来联系你。

部署与使用要点：

* **通过 DNS 发布报告接收地址。**与 MTA-STS 通常一起部署。
* **报告地址要有人真正处理。**与 DMARC 报告同理，投到无人查看的邮箱等于没有部署。
* **重点关注失败类型的分布。**报告会区分证书问题、协议协商问题、策略不匹配等不同类别，**这直接指向根因，比自己盲测高效得多。**
* **把它作为变更的验证手段。**换证书、调整套件、增减 MX 主机之后，报告是确认变更未造成外部影响的客观依据。
* **报告的覆盖面同样不完整**，只有实施了该机制的发送方才会发报告。因此报告适合发现问题，不适合据此计算任何比例。

**排查之外：把配置管理做对，可以消灭大部分这类故障**

回头看高频根因清单会发现，其中大多数不是技术难题，而是**配置管理问题**：漂移、不同步、监控缺失。因此真正的改进方向是：

1. **把 TLS 配置纳入统一的配置管理。**所有 MX 主机使用同一份配置源，杜绝手工逐台修改造成的漂移。
2. **建立换证书的完整清单。**包含：所有 MX 主机、负载均衡器、以及需要同步更新的 DANE TLSA 记录与 MTA-STS 策略。**清单必须写下来，因为换证书的频率低到没有人能记住全部步骤。**
3. **监控要从外部视角做。**从组织网络外部定期检查每一台 MX 主机的 TLS 可用性、链完整性与证书有效期。**从内网检查会因为信任库与网络路径的差异而得出错误结论。**
4. **变更后有观察期。**收紧 TLS 策略属于会影响外部投递的变更，应当分批推进并保留快速回滚能力。
5. **参考通行基线。**[NIST SP 800-177 Rev. 1《Trustworthy Email》](https://csrc.nist.gov/pubs/sp/800/177/r1/final) 与 [英国 NCSC《Email security and anti-spoofing》指南集](https://www.ncsc.gov.uk/collection/email-security-and-anti-spoofing) 都给出了邮件传输加密方面的建议；具体实现层面，[Postfix TLS\_README 官方文档](https://www.postfix.org/TLS_README.html) 详细说明了各项 TLS 参数的语义与取舍，是配置时的直接依据。**不要凭记忆配置 TLS 参数，参数语义在版本之间会变化。**

参考：[RFC 3207《SMTP Service Extension for Secure SMTP over Transport Layer Security》](https://www.rfc-editor.org/rfc/rfc3207.html)，P. Hoffman，2002 年 2 月 ；[RFC 8461《SMTP MTA Strict Transport Security (MTA-STS)》](https://www.rfc-editor.org/rfc/rfc8461.html)，D. Margolis 等，2018 年 9 月 ；[RFC 8460《SMTP TLS Reporting》](https://www.rfc-editor.org/rfc/rfc8460.html)，D. Margolis 等，2018 年 9 月 ；[RFC 7672《SMTP Security via Opportunistic DNS-Based Authentication of Named Entities (DANE) Transport Layer Security (TLS)》](https://www.rfc-editor.org/rfc/rfc7672.html)，V. Dukhovni、W. Hardaker，2015 年 10 月 ；[RFC 6698《The DNS-Based Authentication of Named Entities (DANE) Transport Layer Security (TLS) Protocol: TLSA》](https://www.rfc-editor.org/rfc/rfc6698.html)，P. Hoffman、J. Schlyter，2012 年 8 月 ；[RFC 7817《Updated Transport Layer Security (TLS) Server Identity Check Procedure for Email-Related Protocols》](https://www.rfc-editor.org/rfc/rfc7817.html)，A. Melnikov，2016 年 3 月 ；[RFC 8996《Deprecating TLS 1.0 and TLS 1.1》](https://www.rfc-editor.org/rfc/rfc8996.html)，K. Moriarty、S. Farrell，2021 年 3 月，BCP 195 ；[RFC 8446《The Transport Layer Security (TLS) Protocol Version 1.3》](https://www.rfc-editor.org/rfc/rfc8446.html)，E. Rescorla，2018 年 8 月 ；[RFC 9325《Recommendations for Secure Use of Transport Layer Security (TLS) and Datagram Transport Layer Security (DTLS)》](https://www.rfc-editor.org/rfc/rfc9325.html)，Y. Sheffer 等，2022 年 11 月，BCP 195 ；[RFC 8689《SMTP Require TLS Option》](https://www.rfc-editor.org/rfc/rfc8689.html)，J. Fenton，2019 年 11 月 ；[RFC 8314《Cleartext Considered Obsolete: Use of Transport Layer Security (TLS) for Email Submission and Access》](https://www.rfc-editor.org/rfc/rfc8314.html)，K. Moore、C. Newman，2018 年 1 月 ；[RFC 5321《Simple Mail Transfer Protocol》](https://www.rfc-editor.org/rfc/rfc5321.html)，J. Klensin，2008 年 10 月 ；[RFC 7505《A Null MX No Service Resource Record for Domains That Accept No Mail》](https://www.rfc-editor.org/rfc/rfc7505.html)，J. Levine、M. Delany，2015 年 6 月 ；[NIST SP 800-177 Rev. 1《Trustworthy Email》](https://csrc.nist.gov/pubs/sp/800/177/r1/final) ；[英国 NCSC《Email security and anti-spoofing》指南集](https://www.ncsc.gov.uk/collection/email-security-and-anti-spoofing) ；[Postfix TLS\_README 官方文档](https://www.postfix.org/TLS_README.html)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/tls-inbound-mail-troubleshoot.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
