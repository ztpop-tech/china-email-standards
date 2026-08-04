---
title: "公共后缀域（如某些多级顶级域）下的子域被冒用，能统一加策略吗？"
source: "https://ztpop.net/kb/psd-dmarc-public-suffix-domain-rfc9091.html"
license: CC-BY 4.0
---

# 公共后缀域（如某些多级顶级域）下的子域被冒用，能统一加策略吗？

1
公共后缀域（如某些多级顶级域）下的子域被冒用，能统一加策略吗？
▼

**先说清楚适用边界：这是一份实验性规范**

RFC 9091 的类别是 **Experimental（实验性）**，文档本身即声明它定义的是互联网实验协议。这一点必须先讲明白，因为它直接决定了该如何对待这套机制。

实验性意味着：**不能假定收件方普遍实现**，不能把它作为唯一的防护手段，也不应把它写进对外承诺的合规基线。它的正确定位是**对标准 DMARC 的补充实验**，适用于有条件、有能力承担运营复杂度的公共后缀运营方。

标准 DMARC 规范目前由 RFC 9989 承载，聚合报告与失败报告分别由 RFC 9990 与 RFC 9991 定义，这一组文档取代了此前的 RFC 7489。**常规组织在讨论 DMARC 时应以这一组为准，PSD 扩展是另一个层面的问题。**

**要解决什么问题：组织域之上那一层的空白**

标准 DMARC 的策略发现是围绕**组织域**展开的。这一设计留下了一个空白：**公共后缀之下、尚未被任何人注册的名字，没有任何人能为它发布策略。**

攻击者可以拿一个从未被注册过的名字来伪造发件人。由于该名字不存在，也就不存在对应的组织域策略；接收方按标准流程走完，找不到策略，只能按无策略处理。

RFC 9091 定义了几个关键概念来处理这一层：

* **公共后缀域（PSD）**：§2.4 给出的定义是，最长的 PSD 就是把组织域去掉一个标签后得到的域。
* **公共后缀运营方（PSO）**：§2.5 定义为管理某个公共后缀域运营的组织。
* **PSO 控制的域名**：§2.6 定义为由 PSO 管理、且不可被用作组织域的那些 DNS 名字。

规范并指出，DMARC 中所有对「域名所有者」的表述同样适用于 PSO。文档中还列出了两类适用此扩展的 PSO 类型。

**np 标签：针对不存在子域的策略**

RFC 9091 §3.2 引入了新的 **`np`** 标签，用于表达对**不存在的子域**所请求的接收方处置策略。

规范先给出了「不存在」的判定标准：**就 DMARC 而言，不存在的域是指对 A、AAAA 与 MX 记录的查询均返回 NXDOMAIN 或 NODATA 的域。**这是一个可操作的定义，实现时按此三项判定即可。

`np` 标签的语义规则包括：

* 它**只适用于所查询域的不存在子域**，不适用于该域本身。
* 其语法与取值同 `p` 标签。
* 若 `np` 缺失，则对不存在的子域**必须**适用 `sp` 标签所指定的策略；若 `sp` 也缺失，则适用 `p` 标签的策略。
* **`np` 会在不涉及 PSD 的 DMARC 记录中被忽略。**

接收方的处理流程也相应扩展：在按标准流程未找到策略后，若最长的 PSD 满足 RFC 9091 所列条件，则对匹配最长 PSD 的 DNS 域名查询 DMARC TXT 记录。规范以 `compute.cloudcompany.com.example` 作为最长 PSD 的示例，对应的查询目标是 `_dmarc.compute.cloudcompany.com.example`。

**反馈报告的信息泄露：这是采用前必须评估的风险**

RFC 9091 §5 用相当篇幅讨论了一个容易被忽略的问题：**向 PSO 提供反馈报告，在某些情况下会导致信息从组织内部泄露给 PSO。**

风险的来源在于：PSO 与组织域所有者是两个不同的主体，而聚合报告中包含发信源与认证结果等运营信息。若报告被同时发往 PSO，组织内部的邮件流信息就流出了组织边界。

规范据此给出的限制是：**对于组织型的 PSD，反馈必须限于不存在的域，特定情形除外。**规范还指出 PSD DMARC 采用的是**选择退出**模式——组织域通过发布自己的 DMARC 记录来退出 PSD 策略的覆盖。

另一面是，PSO 会收到关于不存在域的反馈，这类数据对于发现**近似仿冒域**有价值，但同样需要按数据最小化原则处理。

**实施结论：采用前必须先回答「哪些报告会流向 PSO、其中包含什么、组织能否接受」这三个问题。**如果答不上来，就不应该采用。

**对不同角色的建议**

* **普通组织域所有者：这套机制基本不需要你操作，但你需要知道它存在。**要点有二：其一，为自己实际使用的域名发布明确的 DMARC 记录，这本身就构成对 PSD 策略的选择退出；其二，如果发现自己的邮件被上层策略影响，检查方向应包括上层 PSD 是否发布了策略。
* **公共后缀运营方：先评估报告流向，再考虑策略。**建议顺序是——先只做监控、观察不存在域的伪造情况，再逐步收紧；期间持续核对报告内容是否触及了不该触及的组织内部信息。
* **接收方实现者：注意这是实验性扩展。**实现时应可开关、可观测，并明确记录判定依据（是命中了组织域策略还是 PSD 策略），否则一旦出现误拒，排错会非常困难。
* **所有角色：不要把它当成防仿冒的主要手段。**它覆盖的是「不存在的名字被冒用」这一特定场景。已注册的近似域名、显示名伪造、回复链劫持都不在其射程内，仍需依赖 SPF、DKIM、DMARC 主体机制与内容侧判定。
* **关注后续演进。**实验性文档的机制可能在后续标准化过程中调整。部署时应保留调整余地，避免把实验性行为硬编码进关键流程。

参考：RFC 9091《Experimental Domain-Based Message Authentication, Reporting, and Conformance (DMARC) Extension for Public Suffix Domains》§2.4、§2.5 Public Suffix Operator (PSO)、§2.6、§3.2、§4、§5，S. Kitterman、T. Wicinski 编，2021 年 7 月，Experimental，DOI 10.17487/RFC9091，https://www.rfc-editor.org/rfc/rfc9091.html ；RFC 9989《Domain-Based Message Authentication, Reporting, and Conformance (DMARC)》，T. Herr、J. Levine 编，2026 年 5 月，https://www.rfc-editor.org/rfc/rfc9989.html ；RFC 9990《Domain-Based Message Authentication, Reporting, and Conformance (DMARC) Aggregate Reporting》，2026 年 5 月，https://www.rfc-editor.org/rfc/rfc9990.html ；RFC 8020《NXDOMAIN: There Really Is Nothing Underneath》，S. Bortzmeyer、S. Huque，2016 年 11 月，https://www.rfc-editor.org/rfc/rfc8020.html ；RFC 7208《Sender Policy Framework (SPF) for Authorizing Use of Domains in Email, Version 1》，S. Kitterman，2014 年 4 月，https://www.rfc-editor.org/rfc/rfc7208.html

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/psd-dmarc-public-suffix-domain-rfc9091.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
