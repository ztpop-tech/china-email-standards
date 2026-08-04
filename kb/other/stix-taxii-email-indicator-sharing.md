---
title: "如何从邮件事件中提取 IOC 并用 STIX/TAXII 共享？"
source: "https://ztpop.net/kb/stix-taxii-email-indicator-sharing.html"
license: CC-BY 4.0
---

# 如何从邮件事件中提取 IOC 并用 STIX/TAXII 共享？

1
如何从邮件事件中提取 IOC 并用 STIX/TAXII 共享？
▼

**为什么要标准化共享**

NIST SP 800-150 发布于 2016 年 10 月，是 SP 800-61 的补充文件，专门讨论网络威胁信息共享。其立场是：组织通过与同行交换威胁信息，可以获得超出自身可见范围的态势感知，提升检测与响应能力；但共享必须建立在明确的信任关系、数据处理规则与访问控制之上，并充分考虑其中可能包含的敏感信息与隐私影响。这决定了邮件 IOC 共享的两条基本纪律：**格式要机器可读**（否则消费方无法自动化），**内容要经脱敏与分级**（否则会外泄受害者身份与业务信息）。

**从邮件事件中提取哪些 IOC**

* **网络层**：发信 IP、C2 域名与 IP、URL 与其完整跳转链、DNS 解析记录。
* **邮件层**：信封发件人与 RFC5322.From 地址、Reply-To 地址、Message-ID 生成模式、主题模板、HELO 名、发信基础设施的 ASN。
* **文件层**：附件的 SHA-256（首选）、文件名模式、文档元数据（作者、模板路径）、宏或脚本中的特征字符串。
* **行为层**：落地页表单的提交端点、伪装的品牌与登录页指纹、投递时间规律。

提取时须**区分「可共享的攻击者资产」与「不可共享的受害者信息」**：攻击者控制的域名、哈希、C2 可共享；本方收件人邮箱、内部主机名、内部 IP、员工姓名、业务金额则必须移除或泛化。

**STIX 2.1：用什么对象建模邮件 IOC**

STIX 2.1 于 2021 年 6 月 10 日成为 OASIS 标准，定义了 STIX 领域对象（SDO）、STIX 关系对象（SRO）与 STIX 网络可观察对象（SCO）三类构件。与邮件直接相关的 SCO 包括：

* **email-addr**：表示一个邮件地址，核心属性为 value，另可带 display\_name 与 belongs\_to\_ref（指向所属用户账号）。
* **email-message**：表示一封邮件，必需属性为 is\_multipart，可选属性涵盖 date、content\_type、from\_ref、sender\_ref、to\_refs、cc\_refs、bcc\_refs、message\_id、subject、received\_lines、additional\_header\_fields、body、body\_multipart、raw\_email\_ref 等——其中 received\_lines 与 additional\_header\_fields 使信头链路与自定义头也能进入结构化共享。
* **domain-name / ipv4-addr / ipv6-addr / url / file / autonomous-system**：承载域名、地址、链接、附件与发信基础设施。

在 SDO 层面，用 **Indicator** 表达「可用于检测的模式」（必需属性含 pattern、pattern\_type 与 valid\_from），用 **Observed Data** 表达「实际观察到的事实」，用 **Malware**、**Attack Pattern**、**Campaign**、**Intrusion Set**、**Threat Actor** 表达归因与上下文，用 **Sighting** 表达「我也见到了」，用 **Relationship** 把它们连接成图。Attack Pattern 对象可通过 external\_references 关联到 MITRE ATT&CK 技术编号，使邮件 IOC 与 T1566 等技术直接挂钩。

**TAXII 2.1：怎么把数据交换出去**

TAXII 2.1 同于 2021 年 6 月 10 日成为 OASIS 标准，是一个基于 HTTPS 的应用层协议，专为交换以 STIX 表达的网络威胁情报而设计，但其本身与内容格式解耦。要点：

* **Collection 模式**：TAXII 2.1 定义的交换机制是 Collection——一个由 TAXII 服务器托管的对象集合，消费方通过请求—响应方式获取或推送对象。TAXII 2.0 中曾定义的 Channel（发布—订阅）在 2.1 版本中被保留待未来版本定义。
* **资源层级**：Discovery 端点用于发现服务器提供的 API Root；每个 API Root 下有 Collections；每个 Collection 下有 Objects、Manifest 等资源；写操作通过 Status 资源跟踪处理结果。
* **内容协商**：使用带版本参数的媒体类型（形如 `application/taxii+json;version=2.1`）声明协议版本。
* **访问控制**：TAXII 依赖 HTTPS 与其上的认证机制，并允许对不同 Collection 设置不同的读写权限，从而支持分层共享圈。

美国 CISA 运营的自动化指标共享（Automated Indicator Sharing, AIS）即采用 STIX/TAXII 作为技术底座，实现机器速度的指标双向交换。

**共享治理：标记、脱敏与反馈回路**

* **处理标记**：STIX 2.1 支持通过 object\_marking\_refs 与 granular\_markings 附加数据标记，可承载 TLP 等分发限制；共享前必须显式设定，不可依赖对方默认。
* **置信度与时效**：为 Indicator 设置 valid\_from / valid\_until，并使用 confidence 属性表达把握程度。钓鱼基础设施存活期以小时计，长期不撤销的指标会制造大量误报。
* **可撤回**：STIX 对象具备版本与 revoked 属性，误报或失效指标应显式撤销而非静默停发。
* **与既有邮件反馈机制衔接**：RFC 5965 定义的滥用反馈报告格式（ARF）用于在运营方之间反馈滥用事件，与 STIX/TAXII 面向的情报共享互补——前者偏向逐事件的运营投诉，后者偏向结构化的指标与上下文。
* **闭环**：SP 800-150 强调共享是双向的。消费方应回传 Sighting，使生产方了解指标的实际命中情况；只订阅不回馈的参与方，长期会被降低共享层级。

参考：OASIS《STIX Version 2.1》，OASIS Standard，2021 年 6 月 10 日，https://docs.oasis-open.org/cti/stix/v2.1/stix-v2.1.html ；OASIS《TAXII Version 2.1》，OASIS Standard，2021 年 6 月 10 日，https://docs.oasis-open.org/cti/taxii/v2.1/taxii-v2.1.html ；NIST SP 800-150《Guide to Cyber Threat Information Sharing》，Johnson、Badger、Waltermire、Snyder、Skorupka，2016 年 10 月，DOI 10.6028/NIST.SP.800-150，https://csrc.nist.gov/pubs/sp/800/150/final ；CISA Automated Indicator Sharing（AIS），https://www.cisa.gov/topics/cyber-threat-intelligence/automated-indicator-sharing-ais ；RFC 5965《An Extensible Format for Email Feedback Reports》，https://www.rfc-editor.org/rfc/rfc5965.html

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/stix-taxii-email-indicator-sharing.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
