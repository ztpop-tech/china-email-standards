---
title: "大语言模型写的钓鱼邮件还能靠「语病和错别字」识别吗？"
source: "https://ztpop.net/kb/ai-llm-phishing-detection.html"
license: CC-BY 4.0
---

# 大语言模型写的钓鱼邮件还能靠「语病和错别字」识别吗？

**先接受一个前提：语言质量不再是判据**

过去十余年的用户培训把「拼写错误、语法生硬、翻译腔」当作钓鱼邮件的第一识别信号。这一判据的成立条件是**攻击者的语言生产能力受限**。当文本生成能力可被低成本获取后，这个前提不再成立：措辞得体、行文专业、术语准确的邮件，与真实业务邮件在语言层面已无法稳定区分。

**直接结论：**任何把「读起来像不像真的」作为主要判据的流程，都必须重构。CISA Phishing Guidance: Stopping the Attack Cycle at Phase One 在其防护建议中，也是把重点放在技术控制与身份验证，而非依赖收件人对文本的主观判断。

**把研判基线迁移到三层可验证信号**

可执行的替代方案是只采信**攻击者难以伪造或伪造成本极高**的信号，按以下三层排序：

* **第一层：身份鉴别结果（机器可判）。**RFC 7208 Sender Policy Framework (SPF), Version 1、RFC 6376 DomainKeys Identified Mail (DKIM) Signatures、RFC 7489 Domain-based Message Authentication, Reporting, and Conformance (DMARC) 的校验结论，以及 RFC 8601 Message Header Field for Indicating Message Authentication Status 定义的 Authentication-Results 头部记录。这一层输出的是「这封信是否确实来自它声称的域」。
* **第二层：关系与历史（机器可判）。**该发件地址与本组织的历史通信是否存在、首次通信时间、以往是否讨论过该主题、回复链是否连续。
* **第三层：请求语义（人机协同）。**这封信要求收件人做什么——变更收款账号、提供凭据、点击外部链接、绕过既定审批。

**判定顺序很关键：**先看第一层，再看第二层，最后才评估第三层。反过来做（先读内容、被内容带着走）正是社会工程学生效的路径。

**需要落到日志里的字段清单**

上述研判要成立，前提是网关侧真的采集了这些字段。缺一项，对应的判据就变成拍脑袋：

* 信封发件人（RFC 5321 Simple Mail Transfer Protocol 的 MAIL FROM）与头部发件人（RFC 5322 Internet Message Format 的 From），**两者是否一致必须单独记一个布尔字段**。
* SPF / DKIM / DMARC 三项各自的判定结果与对齐（alignment）结论，而不是只记一个总分。
* 发件域的首次出现时间、与本组织的历史邮件计数。
* Reply-To 与 From 是否不同域；显示名中是否包含内部人员姓名而域名为外部。
* RFC 5322 Internet Message Format 定义的 Message-ID，用于把网关、投递、存储三段日志串成同一条链路。

**高信号组合：显示名冒充 + 外部域 + 首次通信**

在实践中最稳定的一个组合判据是：**显示名与某内部高管或财务人员姓名匹配，但发件域为外部域，且该域与本组织此前无通信历史。**这三个条件同时成立时，与文本写得多好完全无关，应直接进入高风险处置。

**可操作配置：**在网关侧维护一份关键人员显示名清单（高管、财务、人事、采购），对「显示名命中清单但发件域非本域」的邮件强制加标记或转人工。这一条规则的实现成本很低，覆盖的却是危害最大的一类攻击。

**避免走向另一个极端：不要把「写得好」当成可疑**

有团队在意识到语言判据失效后，反向设置规则——把行文过于流畅、结构过于工整的邮件标为可疑。这是**错误的补偿**：正常商务邮件同样流畅工整，这类规则只会制造大量误判，并让研判人员对告警脱敏。

**正确做法：**语言特征降级为「辅助参考」，不参与自动拦截决策，只在人工复核界面上作为背景信息展示。自动决策权重全部交给身份鉴别与关系历史这两层可验证信号。

**落地检查表**

1. 本域是否已发布 SPF、DKIM、DMARC 策略，并对入站邮件执行校验与记录。
2. 网关日志是否包含信封发件人与头部发件人的一致性字段。
3. 是否维护关键人员显示名清单并配置了冒充检测规则。
4. 是否记录发件域的首次通信时间，使「首次接触」可被自动识别。
5. 用户培训材料中「看错别字」类内容是否已下线并替换为流程性判据。

参考：[CISA Phishing Guidance: Stopping the Attack Cycle at Phase One](https://www.cisa.gov/resources-tools/resources/phishing-guidance-stopping-attack-cycle-phase-one) ｜ [RFC 7489 Domain-based Message Authentication, Reporting, and Conformance (DMARC)](https://www.rfc-editor.org/rfc/rfc7489.html) ｜ [RFC 8601 Message Header Field for Indicating Message Authentication Status](https://www.rfc-editor.org/rfc/rfc8601.html) ｜ [ENISA Threat Landscape 2025](https://www.enisa.europa.eu/publications/enisa-threat-landscape-2025)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/ai-llm-phishing-detection.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
