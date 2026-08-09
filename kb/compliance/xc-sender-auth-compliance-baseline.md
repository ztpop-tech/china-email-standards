---
title: "信创与等保背景下，本域 SPF/DKIM/DMARC 的合规基线怎么设？"
source: "https://ztpop.net/kb/xc-sender-auth-compliance-baseline.html"
license: CC-BY 4.0
---

# 信创与等保背景下，本域 SPF/DKIM/DMARC 的合规基线怎么设？

**三者分工：解决的不是同一个问题**

* **RFC 7208 Sender Policy Framework (SPF) for Authorizing Use of Domains in Email, Version 1**：声明**哪些 IP 有权以本域名义投递**，校验的是信封发件人域。弱点是**转发会破坏它**——邮件经中间转发后源 IP 改变，校验必然失败。
* **RFC 6376 DomainKeys Identified Mail (DKIM) Signatures**：用私钥对邮件头与正文签名，接收方用 DNS 中的公钥验签。优点是**与传输路径无关**，转发后通常仍能通过。
* **RFC 7489 Domain-based Message Authentication, Reporting, and Conformance (DMARC)**：在前两者之上定义**对齐检查、失败处置策略与报告机制**。它是唯一能让域名所有者「告诉全世界如何处理冒用本域的邮件」的手段。

**关键点：只配 SPF 和 DKIM 而不配 DMARC，等于做了检测但没有处置，也拿不到任何报告数据。**三者必须同时具备。

**配置要点：几个高频出错的细节**

**SPF 侧：**

* 一个域只能有**一条** SPF 记录，多条会导致校验直接失败。合并时务必检查历史遗留记录。
* 注意 DNS 查询次数上限，过多的嵌套引用会导致校验因超限而失败。
* 结尾策略建议用硬失败而非软失败，但**切换前必须确认全部合法发送源已纳入**。
* 不发信的域名同样要发布记录，明确声明「本域不发信」。**闲置域名与子域名是冒用的重灾区。**

**DKIM 侧：**

* 为不同发送源使用不同选择器，便于独立轮换与故障定位。
* 建立密钥轮换机制：新选择器先发布并生效，确认无误后再停用旧的，避免验签中断。
* 签名覆盖的头字段应包含关键字段，避免中间环节改动导致验签失败。

**DMARC 的收敛路径：用报告数据做判定，不要凭感觉**

策略从仅监控收敛到拒绝，每一步都应有数据依据：

1. **发布仅监控策略并配置报告接收地址**。此阶段不影响任何投递，唯一目的是收集数据。
2. **用汇总报告梳理全部发送源**。报告会暴露出大量你不知道的发信来源：历史业务系统、外包供应商、市场活动平台、以及真实的冒用行为。**这一步几乎总会发现「意料之外的合法发送源」，这正是它的价值。**
3. **逐一处理**：合法的纳入 SPF 授权并配置 DKIM 签名；不再使用的关停；冒用的记录下来作为威胁情报。
4. **收敛为隔离**，观察一个业务周期，确认无合法邮件受影响。
5. **收敛为拒绝**。同时对子域策略作明确声明，防止攻击者转而冒用子域。

**进入下一步的判定条件：连续一个完整业务周期内，报告中通过率稳定且无新增的合法发送源出现。**业务周期要覆盖月末、季末等低频发信场景，否则会漏掉那些一季度才发一次的系统。

**强制化的管理范式：可借鉴的做法**

CISA Binding Operational Directive 18-01 提供了一个成熟的强制化范式：明确要求所辖域名部署发件人鉴伪与传输加密，**设定分阶段的合规时限**，并要求把报告集中汇总以验证落实情况。

对多域名、多下属单位的组织，这一范式的可迁移要点是：

* **建立域名台账**：包含全部在用与闲置域名。**没有台账就不可能有基线**，被冒用的往往是没人记得的闲置域名。
* **设定统一时限**，而非任由各单位自行掌握节奏。
* **报告集中收取**，由统一角色核验，避免「配了但没人看」。

**国密改造对这一层的影响边界：基本不重叠**

需要明确说明，避免规划时产生错误预期：

* **SPF 不涉及密码运算**，纯粹是 DNS 查询与 IP 比对，与国密改造无关。
* **DKIM 的签名算法取值受其算法注册机制约束**，接收方只会按已注册的算法验签。因此 DKIM 层面应继续使用已注册且被广泛支持的算法——**在此处改用未被对端支持的算法，结果是全球接收方都无法验签，等同于没有签名。**
* **国密的落点在传输层与内容层**（传输加密、S/MIME 内容签名加密），与发件人鉴伪层各司其职、互不替代。

**结论：国产化改造不应、也不能取消发件人鉴伪三件套。**

**与等保要求的对应关系与验证方法**

这一层同时支撑等保的多项要求：区域边界的入侵防范（防止伪造发件人的钓鱼进入）、计算环境的数据完整性（邮件来源可验证）、以及安全管理中心的集中监测（报告数据的集中收取与分析）。

**验证方法：**

1. 对全部在册域名逐一查询三类 DNS 记录，与台账比对，不得有遗漏。
2. 从外部发送一封伪造本域发件人的测试邮件，确认被按策略处置并有日志记录。
3. 检查报告接收地址是否确实在收取报告、是否有人定期查看并留有分析记录。
4. 抽查本域发出的邮件，确认签名有效、对齐检查通过。

通用实践可参考 NIST SP 800-177 Rev.1 Trustworthy Email。

参考：[RFC 7208 Sender Policy Framework (SPF) for Authorizing Use of Domains in Email, Version 1](https://www.rfc-editor.org/rfc/rfc7208.html) ｜ [RFC 6376 DomainKeys Identified Mail (DKIM) Signatures](https://www.rfc-editor.org/rfc/rfc6376.html) ｜ [RFC 7489 Domain-based Message Authentication, Reporting, and Conformance (DMARC)](https://www.rfc-editor.org/rfc/rfc7489.html) ｜ [CISA Binding Operational Directive 18-01](https://www.cisa.gov/news-events/directives/bod-18-01-enhance-email-and-web-security) ｜ [NIST SP 800-177 Rev.1 Trustworthy Email](https://csrc.nist.gov/pubs/sp/800/177/r1/final) ｜ [国家标准全文公开系统（GB/T 标准检索）](https://openstd.samr.gov.cn/bzgk/gb/)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/xc-sender-auth-compliance-baseline.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
