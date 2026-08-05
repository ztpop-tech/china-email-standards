---
title: "DMARC 聚合报告里一堆 fail，怎么分清哪些是真伪造、哪些是自己配错？"
source: "https://ztpop.net/kb/dmarc-failure-triage.html"
license: CC-BY 4.0
---

# DMARC 聚合报告里一堆 fail，怎么分清哪些是真伪造、哪些是自己配错？

1
DMARC 聚合报告里一堆 fail，怎么分清哪些是真伪造、哪些是自己配错？
▼

**先纠正最常见的理解偏差：DMARC 判的是「对齐」，不是「通过」**

大量分诊时间被浪费在这个误解上：「我的 SPF 明明是 pass，为什么 DMARC 还是 fail？」

原因在于 RFC 7489 引入的**标识对齐（identifier alignment）**。DMARC 关心的不是 SPF 或 DKIM 本身是否通过，而是**通过的那个域，是否与用户实际看到的 `From` 信头域相符**。具体地：

* **SPF 对齐**：SPF 校验的是信封发件人（RFC 5321 的 `MAIL FROM`）所属的域。这个域与 `From` 信头域（RFC 5322）经常不同，尤其在使用第三方代发时。SPF 通过了，但通过的是服务商的域，与 `From` 不对齐，DMARC 依然算失败。
* **DKIM 对齐**：DKIM 签名的 `d=` 标签标明了签名域。签名有效但 `d=` 是服务商域，同样不对齐。

DMARC 的通过条件是**「SPF 与 DKIM 中至少有一个既通过又对齐」**。理解了这一点，报告里的绝大多数 fail 就有了合理解释。

另外要注意对齐有宽松与严格两种模式，宽松模式下子域与组织域视为对齐，严格模式下要求完全一致。**很多「莫名其妙的 fail」只是因为对齐模式设成了严格，而实际发送使用的是子域。**分诊前先确认当前策略里的对齐模式是什么。

**三类 fail 的指纹：拿到报告先做这一步分类**

聚合报告的每一行本质上是「某个源 IP 以某个 `From` 域发送、认证结果如何、数量多少」。按下列指纹分类，绝大多数记录能被快速归位：

**A 类：自家未纳管的合法发送源。**典型指纹——

* 源 IP 属于可识别的服务商网段（营销平台、工单系统、监控告警、人力或财务 SaaS）；
* 发送量稳定、有明显的业务周期性；
* 通常 SPF 通过但不对齐，或者完全没有 DKIM 签名，或者签名域是服务商域。

**这一类是报告中数量最大的部分，也是唯一必须在收紧策略前彻底解决的部分。**处理方式是把它纳管，而不是把它加进例外。

**B 类：转发与邮件列表造成的失败。**典型指纹——

* **SPF 失败但 DKIM 通过且对齐**（转发改变了信封发件人，但没有破坏签名覆盖的内容），这是最干净的转发指纹；
* 或者两者都失败，但源是已知的邮件列表、学术机构、员工个人邮箱的自动转发；
* 数量通常不大，但长期稳定存在。

RFC 8617 定义的 ARC 协议正是为这一场景设计的：它让中间处理方把自己看到的认证结果以可验证的方式记录下来，供下游参考。**但 ARC 是否被采纳完全取决于接收方策略，它不能保证转发邮件一定被放行。**

**C 类：真正的伪造。**典型指纹——

* 源 IP 高度分散，且不属于任何已知服务商；
* 完全没有 DKIM 签名（伪造方拿不到你的私钥）；
* 量在短时间内突增然后消退，呈脉冲状；
* 常集中使用少数几个高价值的 `From` 地址（如财务、高管、通用对外地址）。

**分诊顺序：先把 A 类清零，再谈其他**

正确的顺序不是「先拦住坏人」，而是**「先认全自己人」**。理由很直接：在 A 类未清零之前收紧策略，第一个被打掉的一定是自家业务邮件，而这会导致策略被紧急回滚，从此再没人愿意推进。

清零 A 类的步骤：

1. **建立发送源清册。**把报告中出现的每一个源都归到一个「业务负责人」。**找不到负责人的源要单独标记**——它要么是被遗忘的老系统，要么就是 C 类。
2. **优先用 DKIM 而不是 SPF 来纳管。**原因是 DKIM 签名可以跨越转发存活，而 SPF 会被转发打断；而且 SPF 记录的 DNS 查询次数有上限（RFC 7208 对此有明确规定），把所有服务商都塞进 SPF 记录很快会触顶，一旦超限整条记录的评估结果会变为永久错误，**那是比不对齐严重得多的故障**。
3. **要求服务商用你的域签名。**即为服务商配置属于你的域的 DKIM 选择器，使 `d=` 对齐。这是纳管第三方代发的标准做法。
4. **确实无法签名的，才用 SPF 覆盖**，并注意查询次数预算。
5. **把子域纳入统一管理。**常被遗漏的是那些只用于发送、从不接收的子域，以及完全不发信的域——后者应当显式声明策略，避免被冒用。

**策略收紧的节奏：不要一步到 reject**

DMARC 策略从观察到强制，中间必须留出可观测的过渡。稳妥的推进节奏是：

1. **先设为仅观察（p=none）并开启聚合报告。**至少跑满一个完整业务周期，覆盖月末、季末等发信高峰。**不要在只观察了一周之后就下结论**——很多业务系统是月度触发的。
2. **A 类清零后转入隔离（p=quarantine）。**此时被影响的邮件进入收件人的垃圾箱而非被拒绝，仍然可找回，代价可控。
3. **用百分比参数做灰度。**DMARC 提供了对策略施加比例的参数，可以让策略先作用于一部分邮件。灰度期间重点观察的不是报告，而是**业务侧有没有人来报「对方收不到」**。
4. **观察窗稳定后再转入拒绝（p=reject）。**

两个实操提醒：

* **报告地址要单独设置且真实有人处理。**聚合报告是持续产生的，若投递到一个无人查看的邮箱，整个机制就退化成了摆设。跨域接收报告时还需要在报告接收域侧做相应的授权声明，否则发送方会拒绝投递报告。
* **子域策略要显式规划。**不显式声明时子域会继承组织域策略，这在多数情况下是想要的；但如果存在特殊子域，需要单独设置，**并且要意识到「给子域放松策略」会被冒用者优先利用。**

**聚合报告本身的解读陷阱**

报告是分诊的主要输入，但它有几处固有限制，不了解会得出错误结论：

* **报告不含邮件正文，也不含收件人。**它只提供源 IP、域、认证结果与计数。**因此报告能告诉你「有人在冒用」，但不能告诉你「他们发了什么、发给了谁」。**后者只能靠自家入站侧的检测。
* **覆盖面不完整。**只有实施了 DMARC 报告功能的接收方才会发报告。**报告里的量不是真实发送量，不能据此计算任何比例。**这也是本文不给出任何统计数值的原因。
* **时间粒度粗。**报告通常按天聚合，脉冲式攻击在报告里可能只是一行，且要到第二天才能看到。**报告适合做趋势与纳管，不适合做实时告警。**
* **源 IP 归属需要自行解析。**报告只给 IP，把 IP 归到「哪家服务商、哪个业务」是分诊中最耗时的部分，值得投入自动化。
* **失败报告涉及隐私。**逐封的失败报告会包含报文的部分内容，无论是发送还是接收这类报告都需要谨慎评估合规影响。[M3AAWG 已发布文档索引](https://www.m3aawg.org/published-documents) 中有针对报告处理的实践文档可作参考。

**入站侧的对应动作，以及别把 DMARC 当万能**

上面讲的都是保护自己的域不被冒用。反过来，作为接收方也要把判定结果留痕并用起来：

* **在边界统一添加 `Authentication-Results`（RFC 7601），并清理来自外部的同名信头。**不清理的话这个信头可以被伪造，反而成了误导来源。
* **对通过认证但来自陌生域的邮件不要放松检测。**这是一个常见的策略错误：认证通过只说明「这封邮件确实来自它声称的那个域」，**完全不说明那个域是善意的**。攻击者注册一个新域并为它正确配置 SPF、DKIM、DMARC 是完全可行的。
* **对方域策略为拒绝时，本地处置要尊重它**，但对内部转发场景要有例外处理，否则会打掉自家的转发链路。

最后要明确 DMARC 的能力边界：**它保护的是 `From` 信头域不被精确冒用，仅此而已。**它不防相似域名、不防显示名伪造、不防已被接管的真实账号发出的邮件——而这三种恰恰是资金诈骗类邮件最常用的形态。[英国 NCSC《Email security and anti-spoofing》指南集](https://www.ncsc.gov.uk/collection/email-security-and-anti-spoofing) 与 [NIST SP 800-177 Rev. 1《Trustworthy Email》](https://csrc.nist.gov/pubs/sp/800/177/r1/final) 都把域认证定位为基础层，而不是终点。**把 DMARC 收到 reject 是必要的一步，但如果因此认为邮件伪造问题已经解决，那是把地基当成了房子。**

参考：[RFC 7489《Domain-based Message Authentication, Reporting, and Conformance (DMARC)》](https://www.rfc-editor.org/rfc/rfc7489.html)，M. Kucherawy、E. Zwicky 编，2015 年 3 月 ；[RFC 7208《Sender Policy Framework (SPF) for Authorizing Use of Domains in Email, Version 1》](https://www.rfc-editor.org/rfc/rfc7208.html)，S. Kitterman，2014 年 4 月 ；[RFC 6376《DomainKeys Identified Mail (DKIM) Signatures》](https://www.rfc-editor.org/rfc/rfc6376.html)，D. Crocker、T. Hansen、M. Kucherawy 编，2011 年 9 月 ；[RFC 8617《The Authenticated Received Chain (ARC) Protocol》](https://www.rfc-editor.org/rfc/rfc8617.html)，K. Andersen 等，2019 年 7 月 ；[RFC 7601《Message Header Field for Indicating Message Authentication Status》](https://www.rfc-editor.org/rfc/rfc7601.html)，M. Kucherawy，2015 年 8 月 ；[RFC 8460《SMTP TLS Reporting》](https://www.rfc-editor.org/rfc/rfc8460.html)，D. Margolis 等，2018 年 9 月 ；[RFC 5321《Simple Mail Transfer Protocol》](https://www.rfc-editor.org/rfc/rfc5321.html)，J. Klensin，2008 年 10 月 ；[RFC 5322《Internet Message Format》](https://www.rfc-editor.org/rfc/rfc5322.html)，P. Resnick 编，2008 年 10 月 ；[NIST SP 800-177 Rev. 1《Trustworthy Email》](https://csrc.nist.gov/pubs/sp/800/177/r1/final) ；[英国 NCSC《Email security and anti-spoofing》指南集](https://www.ncsc.gov.uk/collection/email-security-and-anti-spoofing) ；[M3AAWG 已发布文档索引](https://www.m3aawg.org/published-documents)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/dmarc-failure-triage.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
