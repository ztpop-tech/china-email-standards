---
title: "美国联邦 DMARC 政策（BOD 18-01）规定了哪些强制动作与报送地址？"
source: "https://ztpop.net/kb/bod-18-01-federal-dmarc-reporting.html"
license: CC-BY 4.0
---

# 美国联邦 DMARC 政策（BOD 18-01）规定了哪些强制动作与报送地址？

1
美国联邦 DMARC 政策（BOD 18-01）规定了哪些强制动作与报送地址？
▼

**指令性质与法定授权**

**具有约束力的运营指令（Binding Operational Directive，BOD）**是美国国土安全部（DHS）依据《2014 年联邦信息安全现代化法案》（FISMA 2014）向联邦行政部门与机构发出的**强制性指示**，用于保障联邦信息与信息系统安全，联邦机构必须遵守。DHS 的 BOD **不适用**于法律定义的「国家安全系统」，也不适用于国防部与情报界运营的某些系统。

**BOD 18-01「Enhance Email and Web Security」**于 2017 年 10 月 16 日发布，适用范围为**面向互联网的机构信息系统**，既包括机构直接管理的系统，也包括代表机构运营的系统；其主要焦点是机构的**邮件与 Web 基础设施，且不论域名后缀**。此处「二级域（second-level domain）」指组织直接注册的域名（含顶级域），例如在 www.dhs.gov 中，二级域为 dhs.gov。

指令的政策依据是：联邦机构的「网络卫生」水平极大影响用户安全；通过实施业界已广泛采纳的具体安全标准，机构可确保互联网传输数据的完整性与保密性、减少垃圾邮件，并更好保护那些可能被「看似来自政府系统的钓鱼邮件」欺骗的用户。

**四项邮件安全强制动作与时限**

BOD 18-01 要求所有机构在**指令发布后 30 个自然日内**制定并向 DHS 提交「BOD 18-01 机构行动计划」，随后按以下时限落实（以 2017 年 10 月 16 日发布日起算）：

* **90 天内（至 2018 年 1 月 15 日）**：

+ 将**所有面向互联网的邮件服务器配置为提供 STARTTLS**；
+ 为**所有二级机构域配置有效的 SPF/DMARC 记录**，DMARC 策略**至少为 `p=none`**，且**至少定义一个地址**作为聚合报告和/或失败报告的接收方。

* **120 天内（至 2018 年 2 月 13 日）**：确保邮件服务器上**禁用 SSLv2 与 SSLv3**，并**禁用 3DES 与 RC4 密码套件**。（DHS 承认在邮件环境中禁用 3DES 存在显著约束，已于 2018 年 9 月 20 日就该项要求发布**临时政策豁免**。）
* **集中报送地点建立后 15 天内**：将 NCCIC（国家网络安全与通信整合中心）添加为 DMARC **聚合报告**的接收方。
* **一年内（至 2018 年 10 月 16 日）**：为**所有二级域与所有发信主机**设置 DMARC 策略 `p=reject`。

此外，机构需在指令发布后 60 天（2017 年 12 月 15 日）起、直至完全实施为止**每 30 天**提交一次实施状态报告。Web 侧要求（HTTPS-only 与 HSTS、二级域 HSTS 预加载、Web 服务器禁用 SSLv2/SSLv3 与 3DES/RC4）同样在 120 天内完成，实施依据为 https.cio.gov 上的 M-15-13 合规指南。

**联邦聚合报告接收地址与 SCuBA 基线**

关于「联邦 DMARC 报送」这一常被混淆的细节，需以 CISA 官方安全配置基线为准：**联邦机构应在 DMARC 记录的 `rua` 字段中包含 `reports@dmarc.cyber.dhs.gov`**。CISA 在其 M365 Exchange Online 与 Google Workspace Gmail 的 SCuBA 安全配置基线中给出的典型记录形态为：

`v=DMARC1; p=reject; pct=100; rua=mailto:reports@dmarc.cyber.dhs.gov, mailto:reports@example.com; ruf=mailto:reports@example.com`

该记录表示：所有未通过 SPF/DKIM 检查的邮件均被拒绝；聚合报告同时发往 CISA 与机构自身地址；失败报告发往机构自身地址。CISA 明确标注：**仅联邦行政部门与机构应在其 DMARC 记录中包含该地址**；将其作为报告联系点可让 CISA 洞察针对联邦域名的仿冒尝试，是 BOD 18-01 对 FCEB 部门与机构的要求。

相关基线条款包括：DMARC 策略**应**设为 `reject`；聚合报告的 DMARC 联系点**应**包含 `reports@dmarc.cyber.dhs.gov`；**宜**为聚合报告与失败报告同时设置机构自身的联系点（理由是「邮件仿冒尝试对域名所有者并非天然可见，DMARC 提供了接收仿冒尝试报告的机制」）。CISA 将这些条款映射到 **NIST SP 800-53 Rev.5 / FedRAMP High 基线的 SI-4(5)**，并映射到 MITRE ATT&CK 的 T1566（Phishing）系列与 T1562（Impair Defenses）。同一批基线还包含 **MS.EXO.5.1v1「SMTP AUTH 应被禁用」**等条款——理由是现代连接 Exchange Online 邮箱的客户端（Outlook、Outlook on the web、iOS Mail、Outlook for iOS/Android）发送邮件时都不使用 SMTP AUTH，而**启用 SMTP AUTH 时无法强制 MFA**。

**对非联邦组织的借鉴价值**

BOD 18-01 虽只对美国联邦机构具有强制力，但其技术要求构成一份可直接复用的**邮件安全最小基线**，尤其适合政企与关键行业参照：

1. **先做可见性，再做强制**——指令的设计逻辑是「90 天 p=none 收集报告 → 一年内 p=reject」，用近一年时间通过聚合报告发现并整改合法代发源，避免直接拒绝造成业务中断。这与 RFC 7489 建议的渐进部署路径一致。
2. **覆盖面要到「所有二级域与所有发信主机」**——只保护主域而放任子域与旁路发信域，是伪装邮件最常见的突破口。
3. **传输加密与弱算法治理同步推进**——STARTTLS 只解决「能否加密」，还须同时禁用 SSLv2/SSLv3 与 3DES/RC4 等弱协议与弱套件，否则加密形同虚设。DHS 对 3DES 发布临时豁免这一事实也提示：**弱算法退役需评估邮件生态的兼容性约束**，应做好互通性测试与灰度。
4. **报告必须有人接收与消费**——指令要求至少定义一个报告接收地址，联邦机构额外向 CISA 报送。企业侧对应的做法是：建立 RUA 报告的自动解析与看板，并对新增未对齐发送源设置告警，而不是仅仅把报告投递到一个无人查看的邮箱。
5. **禁用无法强制 MFA 的遗留提交方式**——参照 SCuBA 基线对 SMTP AUTH 的处理，对确需保留的旧设备改用应用专用凭据并限定来源 IP 与配额。

参考：DHS / CISA Binding Operational Directive 18-01《Enhance Email and Web Security》，2017 年 10 月 16 日发布，[cisa.gov/news-events/directives/binding-operational-directive-18-01](https://www.cisa.gov/news-events/directives/binding-operational-directive-18-01)；联邦机构聚合报告接收地址与 SCuBA 安全配置基线要求见 CISA M365 Exchange Online 与 Google Workspace Gmail 基线文档；法定授权为《2014 年联邦信息安全现代化法案》（FISMA 2014）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/bod-18-01-federal-dmarc-reporting.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
