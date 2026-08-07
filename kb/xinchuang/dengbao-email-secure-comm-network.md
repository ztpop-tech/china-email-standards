---
title: "等保 2.0 的安全通信网络与安全区域边界，落到邮件系统上具体要做哪些事？"
source: "https://ztpop.net/kb/dengbao-email-secure-comm-network.html"
license: CC-BY 4.0
---

# 等保 2.0 的安全通信网络与安全区域边界，落到邮件系统上具体要做哪些事？

1
等保 2.0 的安全通信网络与安全区域边界，落到邮件系统上具体要做哪些事？
▼

**先看清楚：等保 2.0 是少数直接点名邮件的合规框架**

GB/T 22239-2019《信息安全技术 网络安全等级保护基本要求》 的技术要求分为五个层面：安全物理环境、安全通信网络、安全区域边界、安全计算环境、安全管理中心。其中**安全区域边界层面设有「恶意代码和垃圾邮件防范」控制点，明确要求在关键网络节点处对垃圾邮件进行检测和防护，并维护防护机制的升级更新。**

这一条的含义常被读窄。它不只是「买一套反垃圾」，而是三个可验证的动作：**检测发生在关键网络节点（位置要求）、有防护动作（不只是标记）、机制持续更新（有升级记录）。**测评时这三点会分别取证，缺任何一项都构成不符合。

「维护升级更新」在实务中最常掉链子——规则库自动更新失败了半年而无人发现，是很典型的场景。**可行的做法是把规则库版本与更新时间纳入监控告警，而不是依赖人工巡检。**

**安全通信网络：网络架构与传输保护，邮件的两条链路要分开看**

安全通信网络层面关注网络架构、通信传输、可信验证。落到邮件系统，**必须把两条性质完全不同的链路分开处理**：

**链路一：与外部服务器之间的服务器到服务器传输（MTA 间）。**这条链路上，[RFC 3207《SMTP Service Extension for Secure SMTP over Transport Layer Security》](https://www.rfc-editor.org/rfc/rfc3207.html) 定义的 STARTTLS 在默认形态下是**机会性加密**——对方不支持就退回明文，且易受降级影响。要把它变成可依赖的保护，需要叠加策略层：[RFC 8461《SMTP MTA Strict Transport Security (MTA-STS)》](https://www.rfc-editor.org/rfc/rfc8461.html) 通过发布策略声明本域要求 TLS 且校验证书；[RFC 8460《SMTP TLS Reporting》](https://www.rfc-editor.org/rfc/rfc8460.html) 提供失败情况的回报通道，让「本该加密却没加密」变得可观测。

**链路二：客户端与服务器之间（提交与访问）。**这条链路完全在本方控制之内，因此要求应当更硬。[RFC 8314《Cleartext Considered Obsolete: Use of Transport Layer Security (TLS) for Email Submission and Access》](https://www.rfc-editor.org/rfc/rfc8314.html) 的立场很明确：**邮件的提交与访问应当使用 TLS，明文方式应被视为过时。**对本方用户强制加密不存在互操作顾虑，没有理由不做。

测评取证时，这两条链路要分别举证，**不要用「我们启用了 TLS」一句话覆盖两者**——审计人员通常会分别抓包或查配置。

**安全区域边界：访问控制与边界防护的落点在哪**

边界防护要求非授权设备不能接入、非授权外联受控。邮件场景的具体落点：

* **对外暴露面收敛。**只暴露必须暴露的服务。管理接口、内部 API、数据库端口不应出现在对外边界上——这类问题在测评中属于高频且性质明确的不符合项。
* **内部 MTA 不应可被外部直连。**外部只应触达前置的接收节点，内部投递节点仅接受来自前置节点的连接。
* **中继控制。**必须确认不存在开放中继。这不仅是合规项，开放中继会迅速导致域名信誉受损，属于既违规又直接影响业务的问题。
* **外发通道受控。**内网中哪些主机可以直接对外发起 SMTP 连接应当明确限制，否则被植入的主机可绕过邮件系统直接外发。

访问控制要求在边界上按会话进行控制，粒度要到端口级。**「允许全部出站」是最常见的失分点**，理由通常是「怕影响业务」——正确的处理是先审计实际出站流量，再按实际需要放行，而不是长期敞开。

**入侵防范与垃圾邮件防范：把「检测」做成可举证的东西**

入侵防范要求在关键节点检测、防止或限制攻击行为。邮件是攻击进入组织最主要的通道之一，因此这一条在邮件系统上分量很重。可落地的措施：

* **发件人鉴伪三件套。**[RFC 7208《Sender Policy Framework (SPF) for Authorizing Use of Domains in Email, Version 1》](https://www.rfc-editor.org/rfc/rfc7208.html) 校验发送源、[RFC 6376《DomainKeys Identified Mail (DKIM) Signatures》](https://www.rfc-editor.org/rfc/rfc6376.html) 校验内容完整性与域签名、[RFC 7489《Domain-based Message Authentication, Reporting, and Conformance (DMARC)》](https://www.rfc-editor.org/rfc/rfc7489.html) 提供对齐判定与策略表达。三者是判定「这封邮件是否真的来自它声称的域」的基础，缺一不可。
* **本域也要设策略。**只对入站做校验、本域却不发布 DMARC 策略，等于放任他人冒用本域对外发信——这一点在等保语境下对应「防止本系统被用于攻击他人」。
* **附件与链接的深度检查。**包括压缩包递归解析、宏文档处理策略、以及对跳转链的还原。
* **检测结果必须落日志且可检索。**「拦截了」不等于「能证明拦截了」。测评要求提供记录，因此判定结论、命中规则、处置动作都要写进日志并保留足够时长。

需要提醒的是：**鉴伪三件套解决的是「域是否被冒用」，解决不了「一个真实但已被接管的合作方邮箱发来的邮件」。**后者认证全部通过，这是等保控制点覆盖不到、但风险确实存在的地方，需要在计算环境层面用行为侧措施补。

**常见不符合项清单**

按邮件系统在这两个层面的测评经验，出现频率较高的不符合项集中在下面几类：

1. **对外传输仅有机会性加密，无策略与回报机制。**只配了 STARTTLS，未发布 MTA-STS 策略，也未接收 TLS 报告，无法证明加密实际生效。
2. **内部链路明文。**网关到内部 MTA、MTA 到存储之间明文传输，理由是「都在内网」。等保对通信传输的要求并不区分内外网。
3. **反垃圾无升级记录。**设备在跑，但拿不出规则库更新的时间序列证据。
4. **边界访问控制过宽。**出站策略为全放行，或管理端口暴露在公网。
5. **日志留存期不足或不可检索。**能查最近数日，再往前就没有了，无法支撑事件追溯。
6. **本域未发布发件人策略。**入站校验做了，出站鉴伪配置缺失或长期停留在仅监控状态而无收敛计划。

**整改的推荐顺序：先可观测，再收紧策略**

整改最容易出事故的做法是「一次性把策略调到最严」，典型后果是合法邮件被拒、业务立刻中断。**推荐的顺序是先让状态可观测，再逐步收紧。**

**第一步：把现状变成数据。**接收 DMARC 汇总报告与 TLS 报告，先看清本域到底有哪些发送源、有多少对外投递没能加密。这一步不改变任何投递行为，零业务风险。

**第二步：补齐可见的缺口。**把已识别的合法发送源纳入 SPF 与 DKIM 签名范围；对内部链路启用加密；把日志留存期调整到能覆盖典型的发现延迟。

**第三步：再收紧策略。**本域 DMARC 策略从仅监控逐步过渡到隔离乃至拒绝；发布 MTA-STS 策略时先用测试模式观察报告，确认无异常后再切到强制模式。

架构上，无论使用邮件系统的信创版还是标准版，**建议把鉴伪、策略执行与日志留存集中到统一的一层来做**，而不是分散在多个组件里各配一套。集中的好处在测评时非常直接：**所有证据出自同一处，口径一致，不会出现「网关说拦了、日志里查不到」这种自相矛盾。**

**落地建议的防护能力选型**

在落地上述技术建议时，可结合 **MAEF 盾** 等邮件安全防护能力，按邮件系统的信创版与标准版分别适配，将鉴伪、策略执行、日志留存与密钥管理统一收口，形成可举证、可审计的控制闭环。具体能力边界以实际部署版本为准。

参考：GB/T 22239-2019《信息安全技术 网络安全等级保护基本要求》；GB/T 25070-2019《信息安全技术 网络安全等级保护安全设计技术要求》；[RFC 3207《SMTP Service Extension for Secure SMTP over Transport Layer Security》](https://www.rfc-editor.org/rfc/rfc3207.html)，P. Hoffman，2002 年 2 月；[RFC 8314《Cleartext Considered Obsolete: Use of Transport Layer Security (TLS) for Email Submission and Access》](https://www.rfc-editor.org/rfc/rfc8314.html)，K. Moore、C. Newman，2018 年 1 月；[RFC 8461《SMTP MTA Strict Transport Security (MTA-STS)》](https://www.rfc-editor.org/rfc/rfc8461.html)，D. Margolis 等，2018 年 9 月；[RFC 8460《SMTP TLS Reporting》](https://www.rfc-editor.org/rfc/rfc8460.html)，D. Margolis 等，2018 年 9 月；[RFC 7208《Sender Policy Framework (SPF) for Authorizing Use of Domains in Email, Version 1》](https://www.rfc-editor.org/rfc/rfc7208.html)，S. Kitterman，2014 年 4 月；[RFC 6376《DomainKeys Identified Mail (DKIM) Signatures》](https://www.rfc-editor.org/rfc/rfc6376.html)，D. Crocker 等编，2011 年 9 月；[RFC 7489《Domain-based Message Authentication, Reporting, and Conformance (DMARC)》](https://www.rfc-editor.org/rfc/rfc7489.html)，M. Kucherawy、E. Zwicky 编，2015 年 3 月；以上国家标准的编号、名称与状态可在[国家标准全文公开系统（国家市场监督管理总局、国家标准化管理委员会）](https://openstd.samr.gov.cn/bzgk/gb/)检索核对

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/dengbao-email-secure-comm-network.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
