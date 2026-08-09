---
title: "怎么判定一个发件人可疑？发件人信誉看哪些信号？"
source: "https://ztpop.net/kb/gw-sender-reputation-signals.html"
license: CC-BY 4.0
---

# 怎么判定一个发件人可疑？发件人信誉看哪些信号？

**信誉是多信号加权，不是单一黑名单**

Exchange 的发件人信誉（由协议分析代理计算）综合了多类观测得出发件人信誉级别，再据此决定是否临时封禁该发送方，而不是只查一张列表。自建网关应沿用同一思路：任何单一信号都有误判，加权后设阈值才稳定。

四类信号按获取成本从低到高排列：连接级、协议级、身份级、行为级。前两类在会话早期即可获得，可用于低成本前置过滤；后两类更准确但需要历史积累。

**连接级信号**

包括：源 IP 的反向解析是否存在、反向解析与正向解析是否一致、PTR 名是否具备动态住宅地址特征、该 IP 所在网段的历史投递质量、是否命中公开信誉列表。

判定要点是不要把「无 PTR」当成硬拒绝条件。RFC 5321 并未要求发送方必须具备 PTR，很多合法的中小企业出口就没有。它只应作为一个加分项参与打分。

**协议级信号**

包括：EHLO 标识是否为合法域名（伪造成收件方自身域名或本机 IP 是强负面信号）、是否在收到应答前抢先发送命令（pipelining 违规）、单连接内的无效收件人比例、RSET 与 NOOP 的异常频次。

无效收件人比例是性价比最高的一条：同一连接或同一源在短时间内命中大量不存在的收件人，几乎可以确定为目录收割，应立即降级并限速。

**身份级信号**

包括：SPF 校验结果（RFC 7208 定义的 pass/fail/softfail/neutral 等）、DKIM 签名域与验证结果、DMARC 对齐情况。这里有一条常被误用的规则：SPF pass 只说明「这台机器被授权代表该域发送」，不代表该域可信——攻击者完全可以在自己控制的域上配置正确的 SPF。

因此身份信号的正确用法是「把信誉绑定到经过验证的身份上」：对通过 DKIM 验证的签名域累积历史信誉，比对源 IP 累积更稳定，因为发送方换 IP 不会绕开它。

**行为级信号与处置分级**

包括：该发送域或 IP 历史上的用户举报率、隔离释放率、发送量的突变幅度、发送时间分布是否呈机器特征。

处置应分级而非二值：轻度降级只做限速与加严评分；中度降级把邮件强制进入隔离；重度才在会话内拒收。每一级都必须带自动过期时间与恢复条件——信誉系统若只降不升，长期会积累大量无法自愈的误判。

同时保留申诉路径：为被拒的合法发送方在拒绝应答中给出可识别的错误标识（而非泛化的「spam」字样），便于对方定位并联系。这也是降低误判损失的最后一道保障。

参考：[Microsoft Learn：Exchange Server 反垃圾邮件保护](https://learn.microsoft.com/en-us/exchange/antispam-and-antimalware/antispam-protection/antispam-protection) ｜ [RFC 5321 Simple Mail Transfer Protocol](https://www.rfc-editor.org/rfc/rfc5321.html) ｜ [RFC 7208 Sender Policy Framework (SPF)](https://www.rfc-editor.org/rfc/rfc7208.html)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/gw-sender-reputation-signals.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
