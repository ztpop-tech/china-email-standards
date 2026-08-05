---
title: "邮件是勒索软件的主要入口之一，投递面到底能收敛到什么程度？"
source: "https://ztpop.net/kb/ransomware-email-vector-mitigation.html"
license: CC-BY 4.0
---

# 邮件是勒索软件的主要入口之一，投递面到底能收敛到什么程度？

1
邮件是勒索软件的主要入口之一，投递面到底能收敛到什么程度？
▼

**先划清边界：邮件侧能做什么，不能做什么**

把勒索软件防护的期望全部压在邮件网关上，是一种常见且危险的资源错配。**邮件侧能做的是收窄投递面，不能做的是阻止执行、不能做的是保证恢复。**

[CISA StopRansomware（联合 FBI、NSA、MS-ISAC 发布的勒索软件防护指南汇总页）](https://www.cisa.gov/stopransomware) 汇总的联合指南采取的是分层视角：投递面收敛、初始访问阻断、横向移动限制、备份与恢复、以及事件响应，每一层各自承担一部分。邮件只占第一层的一部分。**如果备份不可用、终端无防护、权限过宽，那么邮件侧做到极致也只是把时间往后推。**

这个边界认知对运维有实际意义：它决定了当邮件侧的收敛与业务便利产生冲突时，应当把多少政治资本花在这里。**值得强硬坚持的是那些成本低、收益高、可解释的策略；不值得为了极小的边际收益去打一场会让业务全面反弹的仗**——因为一旦策略被业务压力整体回滚，你连基线都保不住。

**附件策略：必须按内容类型判定，不能只靠扩展名黑名单**

扩展名黑名单是最容易实现也最容易被绕过的方案。它的根本问题在于**扩展名是文件名的一部分，与文件的真实内容没有强制关系**；同时新的可执行载体形态在不断出现，黑名单永远滞后。

更稳健的设计原则：

* **基于真实内容类型判定，而不是基于声明的类型或扩展名。**MIME 的 `Content-Type`（RFC 5322 与 MIME 系列规范）是发送方声明的，不是事实。检测应当基于对内容的实际识别。
* **改为白名单思路。**列出业务确实需要的文档与媒体类型，其余默认阻断或转入更严格的处理路径。**这个清单比大多数人预期的要短**，值得实际测量一次再讨论。
* **递归处理容器。**压缩包、嵌套压缩、磁盘映像类文件、以及各类可携带引用或执行语义的容器格式，必须递归展开后按同样规则判定。**只检查最外层等于没检查。**
* **加密压缩包必须单独决策。**网关无法检查其内容，这是客观事实。可选项只有三个：一律阻断、一律放行、或者放行但强制附加显著标识并降低整封邮件的信任度。**回避这个决策等于默认选择了「放行」，而这通常不是有意识的选择。**
* **对文件名本身做规范化处理。**包含大量填充字符、双重扩展名、或使用可改变显示顺序的特殊字符的文件名，其目的通常就是让用户看到与实际不同的类型。**这类文件名本身就应当作为一个风险信号。**

**宏与活动内容：这一层的主战场在平台侧，不在邮件侧**

办公文档中的宏长期是主要的初始执行载体。**但这一层最有效的控制不在邮件网关，而在办公套件的平台配置上。**

[Microsoft 官方文档《Macros from the internet are blocked by default in Office》](https://learn.microsoft.com/en-us/deployoffice/security/internet-macros-blocked) 说明了对来自互联网的文件默认阻止宏运行的机制及其配套的组策略配置。这类平台侧默认策略的价值在于：**它不依赖检测，因此不会被新的混淆手法绕过。**邮件网关能做的检测总是有对抗空间，而「来自外部的文档中的宏一律不运行」是一条结构性的规则。

邮件侧需要与之配合的是：

* **确保文件的来源标记不被剥离。**如果邮件系统或中间环节在保存附件时丢失了「来自外部」这一属性，平台侧的默认策略就失效了。**这是一个非常容易被忽略的联动点，值得实际验证一次。**
* **对含有活动内容的文档提高检测强度**，并考虑对来自外部发件人的此类文档采取更严格的策略。
* **建立例外流程而不是全局放松。**确实需要使用宏的业务场景应当通过受控的分发渠道，而不是通过邮件附件。

**链接侧：收益真实，代价也真实**

URL 改写与点击时检测能覆盖「投递时无害、点击时恶意」的场景，这是静态检测无法覆盖的部分。**但它的代价必须被明确承认，而不是被供应商话术掩盖过去：**

* **破坏一次性链接。**密码重置、邮件确认、会议邀请中的一次性令牌，可能因为自动预取而被消耗掉，导致用户点击时链接已失效。**这类故障的表现是间歇性的，排查成本很高。**
* **改变了用户可见的 URL。**用户失去了通过悬停查看真实目标的能力，**这在一定程度上削弱了用户自身的判断能力**——一个长期被训练成「所有链接看起来都一样」的用户，在改写失效时更容易受骗。
* **引入了对外部服务的依赖与隐私考量。**点击行为会被记录，链接内容会被外部服务获取。涉及敏感业务时需要评估。
* **可用性成为单点。**改写服务不可用时，所有历史邮件中的链接可能同时失效。

结论不是「不要用」，而是**「用之前要把这四项代价写进决策记录，并准备好对应的处理流程」**。特别是一次性链接问题，应当事先建立例外机制。

**来源侧与差异化策略：把有限的严格用在对的地方**

对所有邮件一视同仁地施加最严格的策略，业务上不可持续。可行的做法是**按来源可信度做差异化**：

* **收紧本域的 DMARC 策略（RFC 7489）**，减少本域被冒用的空间。这不直接防勒索软件，但它消除了「看起来来自内部」这一最有效的诱导因素。
* **为外部邮件添加显著且不可伪造的标识。**注意标识必须由边界节点统一添加，并清理外部报文中已有的同类标识，否则会被反向利用。**另外要控制标识的滥用程度**——如果几乎每封邮件都带标识，用户很快就会忽略它。
* **对首次通信的外部域采取更严格的附件策略。**与长期合作方的通信模式是可测量的，首次出现的域天然值得更谨慎对待。
* **对高风险岗位单独加严。**财务、人力、行政等岗位的收信特征相对固定，可以为其配置更严格的规则集而不影响全员。RFC 5228 定义的 Sieve 提供了一种标准化的邮件过滤语言，可用于表达此类按收件人差异化的规则。

**被忽略的一项缓解：快速回答「还有谁收到了」**

假设已经有人执行了附件。此时邮件侧最有价值的能力不是检测，而是**在几分钟内给出完整的同批次收件人清单**。

理由很直接：勒索软件事件的损失与被感染终端的数量强相关，而阻止其余收件人执行是止损空间最大的动作。**这个窗口通常很短。**

要具备这项能力，需要事前准备：

1. **可按多种不变量检索的能力。**附件哈希、发送 IP、DKIM 签名域、链接主机名，至少要能按其中几项检索历史投递记录。
2. **检索范围要覆盖足够长的历史。**同一批次可能已断续投递多日。
3. **能批量隔离且可逆。**并且执行过程要留审计。
4. **结果要能直接交给终端侧。**收件人清单需要能快速转化为终端排查清单，这要求邮箱地址与终端资产之间有可用的对应关系。**这层对应关系通常在事发时才发现没有，值得提前打通。**

最后回到恢复。[NIST SP 800-184《Guide for Cybersecurity Event Recovery》](https://csrc.nist.gov/pubs/sp/800/184/final) 从事件恢复的角度强调恢复能力需要预先规划与验证。对邮件系统自身而言，需要单独回答的问题是：**如果邮件服务器或其存储被加密，邮件数据能否恢复、恢复到什么时间点、恢复需要多久，以及在恢复期间用什么方式维持基本通信。**这个问题应当在演练中被真实回答过一次，而不是停留在架构图上。

参考：[CISA StopRansomware（联合 FBI、NSA、MS-ISAC 发布的勒索软件防护指南汇总页）](https://www.cisa.gov/stopransomware) ；[CISA《Federal Government Cybersecurity Incident and Vulnerability Response Playbooks》](https://www.cisa.gov/resources-tools/resources/federal-government-cybersecurity-incident-and-vulnerability-response-playbooks) ；[NIST SP 800-61 Rev. 3《Incident Response Recommendations and Considerations for Cybersecurity Risk Management》](https://csrc.nist.gov/pubs/sp/800/61/r3/final) ；[NIST SP 800-184《Guide for Cybersecurity Event Recovery》](https://csrc.nist.gov/pubs/sp/800/184/final) ；[NIST SP 800-177 Rev. 1《Trustworthy Email》](https://csrc.nist.gov/pubs/sp/800/177/r1/final) ；[Microsoft 官方文档《Macros from the internet are blocked by default in Office》](https://learn.microsoft.com/en-us/deployoffice/security/internet-macros-blocked) ；[英国 NCSC《Phishing attacks: defending your organisation》指南集](https://www.ncsc.gov.uk/collection/phishing) ；[欧盟网络安全局 ENISA](https://www.enisa.europa.eu/) ；[RFC 7489《Domain-based Message Authentication, Reporting, and Conformance (DMARC)》](https://www.rfc-editor.org/rfc/rfc7489.html)，M. Kucherawy、E. Zwicky 编，2015 年 3 月 ；[RFC 5322《Internet Message Format》](https://www.rfc-editor.org/rfc/rfc5322.html)，P. Resnick 编，2008 年 10 月 ；[RFC 5228《Sieve: An Email Filtering Language》](https://www.rfc-editor.org/rfc/rfc5228.html)，P. Guenther 编、T. Showalter，2008 年 1 月

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/ransomware-email-vector-mitigation.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
