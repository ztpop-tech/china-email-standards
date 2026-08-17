---
title: "CISA《钓鱼防护指南：在第一阶段阻断攻击链》中文摘译"
source: "https://ztpop.net/kb/vnd-cisa-phishing-guidance.html"
license: CC-BY 4.0
---

# CISA《钓鱼防护指南：在第一阶段阻断攻击链》中文摘译

**翻译／摘录披露：**本页为对 CISA / NSA / FBI / MS-ISAC Phishing Guidance: Stopping the Attack Cycle at Phase One 的中文翻译与摘录，原文著作权归该机构所有，内容以人类官方原文为准。
  
原文机构：CISA / NSA / FBI / MS-ISAC；原文名称：Phishing Guidance: Stopping the Attack Cycle at Phase One（《钓鱼防护指南：在第一阶段阻断攻击链》）；原文发布：2023-10；授权状态：美国联邦政府作品，TLP:CLEAR（原文声明「可无限制分发」）。
  
本页由 AI 承担翻译、摘录与排版工作，**不含任何 AI 原创的技术结论**；每一节均标注其对应的人类原文章节，如与原文有出入，以原文为准。

# CISA《钓鱼防护指南：在第一阶段阻断攻击链》中文摘译

⁣​‌​‌‌​‌​​‌​‌​‌​​​‌​‌​​​​​‌​​‌‌‌‌​‌​‌​​​​​‌‌‌‌‌​​​​‌‌​​‌​​​‌‌​​​​​​‌‌​​‌​​​‌‌​‌‌​​​‌​‌‌​‌​​‌‌​​​​​​‌‌‌​​​​‌‌‌‌‌​​​‌‌‌​‌‌​​​‌‌​​​‌​‌‌‌‌‌​​​‌​​​‌‌​​‌​​​‌​‌​‌​​​‌​​​‌​​​‌​‌⁤

⁣​‌​‌‌​‌​​‌​‌​‌​​​‌​‌​​​​​‌​​‌‌‌‌​‌​‌​​​​​‌‌‌‌‌​​​​‌‌​​‌​​​‌‌​​​​​​‌‌​​‌​​​‌‌​‌‌​​​‌​‌‌​‌​​‌‌​​​​​​‌‌‌​​​​‌‌‌‌‌​​​‌‌‌​‌‌​​​‌‌​​​‌​‌‌‌‌‌​​​‌​​​‌‌​​‌​​​‌​‌​‌​​​‌​​​‌​​​‌​‌⁤来源机构：CISA / NSA / FBI / MS-ISAC　|　原文：Phishing Guidance: Stopping the Attack Cycle at Phase One　|　原文发布：2023-10　|　页面性质：中文翻译与摘录（非原创综述）

本页对 CISA、NSA、FBI 与 MS-ISAC 联合发布的钓鱼防护指南做中文翻译与摘录。该文件为美国联邦政府作品并标记 TLP:CLEAR，原文首页声明：披露不受限制（“Disclosure is not limited”）。以下每一节均标注其在原文 PDF 中的章节位置，技术判断以原文为准。

## 文件概况（原文封面页 / TABLE OF CONTENTS）

人类原文来源章节：封面页 + 目录页

* **原文标题：**Phishing Guidance: Stopping the Attack Cycle at Phase One
* **发布时间：**Publication: October 2023
* **联合发布机构：**Cybersecurity and Infrastructure Security Agency (CISA)、National Security Agency (NSA)、Federal Bureau of Investigation (FBI)、Multi-State Information Sharing and Analysis Center (MS-ISAC)
* **流通标记：**TLP:CLEAR
* **原文目录：**OVERVIEW / PHISHING TO OBTAIN LOGIN CREDENTIALS / MALWARE-BASED PHISHING / MITIGATIONS / INCIDENT RESPONSE / REPORTING / CISA SERVICES / RESOURCES / ACKNOWLEDGEMENTS / DISCLAIMER / REFERENCES

## 一、概述：钓鱼的两大目的（原文 OVERVIEW 节）

人类原文来源章节：OVERVIEW（PDF 第 3 页）

原文将社会工程定义为「诱骗他人泄露信息（例如口令）或采取某种可用于攻陷系统或网络的行动」，并把钓鱼归入社会工程的一种形式——攻击者通常经由电子邮件引诱受害者访问恶意站点或骗取登录凭据。

原文指出攻击者实施钓鱼主要用于两个目的：

* **获取登录凭据（Obtaining login credentials）。**攻击者发动钓鱼行动窃取登录凭据，以取得网络的初始访问权。
* **投放恶意软件（Malware deployment）。**攻击者常借钓鱼投放恶意软件以开展后续活动，例如中断或破坏系统、提升用户权限、在已失陷系统上维持驻留。

原文同时说明适用范围：面向网络防御者的建议适用于所有组织，但对资源有限的组织未必可行，因此指南另设中小企业专章；面向软件制造商的部分聚焦「安全设计（secure-by-design）与安全默认（secure-by-default）」。

## 二、凭据窃取型钓鱼：定义与常见技术（原文 PHISHING TO OBTAIN LOGIN CREDENTIALS 节）

人类原文来源章节：PHISHING TO OBTAIN LOGIN CREDENTIALS — DEFINITION / EXAMPLE TECHNIQUES（PDF 第 4–5 页）

**原文定义：**攻击者伪装成可信来源（如同事、熟人或机构），引诱受害者交出登录凭据；随后利用这些被窃凭据（用户名与口令）访问企业网络或受保护资源（例如邮箱账户）。

**原文列举的常见手法：**

* 冒充主管、可信同事或 IT 人员，向员工发送定向邮件骗取登录凭据。
* 借助智能手机或平板，通过短信（SMS）以及 Slack、Teams、Signal、WhatsApp、Facebook Messenger 等平台的聊天消息诱骗用户泄露凭据。
  + 原文注记：混合办公环境中面对面交流减少、虚拟交互频繁，用户更易被针对其常用平台设计的社会工程手法欺骗。
* 利用 VoIP 轻易伪造主叫号码（caller ID），利用公众对电话服务（尤其固话）安全性的信任。

**关于 MFA 的原文表述：**多因素认证可降低攻击者利用被窃凭据取得初始访问的能力；但若启用的是弱形式的 MFA，攻击者仍可能通过钓鱼等技术获得访问权。原文将「未使用 FIDO 或 PKI 类抗钓鱼 MFA 的账户」列为弱 MFA 实现的情形之一，并指向 CISA 的两份事实清单：*Implementing Phishing Resistant MFA* 与 *Implementing Number Matching in MFA Applications*。

## 三、恶意软件型钓鱼：定义与常见技术（原文 MALWARE-BASED PHISHING 节）

人类原文来源章节：MALWARE-BASED PHISHING — DEFINITION / EXAMPLE TECHNIQUES（PDF 第 5 页）

**原文定义：**攻击者伪装成可信来源，引诱受害者点击恶意超链接或打开邮件附件，从而在主机系统上执行恶意软件。

* 发送恶意超链接或附件促使用户下载恶意软件，用于取得初始访问、窃取信息、破坏或中断系统与服务、提升账户权限。
  + 原文点名攻击者可能使用免费公开工具（如 GoPhish、Zphisher）开展鱼叉式钓鱼，对特定个人使用高度定制且具说服力的诱饵。
  + 原文指出攻击者可能发送带宏脚本的恶意附件，或投送看似无害／经混淆的链接以下载恶意可执行文件。
* 借助手机／平板 App 与短信，在 Slack、Teams、Signal、WhatsApp、iMessage、Facebook Messenger 等协作平台发送消息，诱使用户交互从而执行恶意软件。
  + 原文注记：这类平台界面受限（constrained UI），用户很难辨别恶意 URL。

## 四、面向所有组织的缓解措施（原文 MITIGATIONS — ALL ORGANIZATIONS 节）

人类原文来源章节：MITIGATIONS / ALL ORGANIZATIONS（PDF 第 5–8 页）；括号内 CPG 编号为原文标注

原文说明：以下缓解措施与 CISA 和 NIST 制定的跨部门网络安全绩效目标（Cross-Sector Cybersecurity Performance Goals, CPGs）对齐。

### 4.1 人员与邮件认证

* **开展社会工程与钓鱼的用户培训 [CPG 2.I]。**原文要求定期教育用户识别可疑邮件与链接、不与可疑对象交互，并强调上报「已打开可疑邮件／链接／附件或其他诱饵」的重要性。
* **对收到的邮件启用 DMARC。**原文表述：DMARC 与 SPF、DKIM 一同按已发布的规则校验来信的发送服务器；若校验失败，即判定为伪造发件地址，邮件系统将其隔离并报告为恶意。原文补充：可定义多个 DMARC 报告接收人；当 DMARC 策略为 reject 时，这些机制会拒收被伪造域的来信。
* **对发出的邮件将 DMARC 设为 “reject” [CPG 2.M]。**原文称此举可强力防止他人收到冒充本域的邮件：
  + 伪造邮件在投递前即在邮件服务器被拒绝；
  + DMARC 报告为被伪造域的所有者提供通知机制，包含疑似伪造来源等其原本无从获知的信息；
  + 启用 DMARC 策略可降低威胁行为者伪造本组织域名发信的可能性。原文在此处指向 CISA Insights《Enhance Email and Web Security》、CIS 的 DMARC 页面以及 Microsoft 的 Anti-Spoofing 指南。
* **实施内部邮件与消息监控。**原文要求监控内部邮件与消息流量以识别异常活动。

### 4.2 身份与认证强度

* **优先部署抗钓鱼 MFA。**原文注记：基于 PKI 的 MFA 需要高度成熟的身份与访问管理体系，且未被常用服务广泛支持；应优先为管理员和特权账户（例如可访问电子取证工具、或可广泛访问客户与财务数据的账户）部署抗钓鱼 MFA。
* **围绕单点登录（SSO）实施集中式登录。**原文称 SSO 属用户生命周期管理机制，可降低用户被社会工程骗取凭据的概率（与 MFA 或抗钓鱼 MFA 配合时尤为明显），并为 IT 人员提供可在疑似或确认入侵后主动／回溯审查的审计轨迹。
* **检查 MFA 锁定与告警设置，跟踪被拒绝（或尝试中）的 MFA 登录 [CPG 2.G]。**原文要求在出现异常活动或持续恶意登录尝试时执行账户锁定，以防攻击者绕过 MFA；同时尽量减少不必要的业务中断，并强调应优先保障组织与消费者数据的健康度，而非单个员工的短期生产力。
* 识别并处置成功的钓鱼事件；及时上报钓鱼事件；制定成文的事件响应计划（原文指向 CISA 的 *Incident Response Plan Basics* 事实清单）。

### 4.3 阻断恶意软件执行（原文 PREVENTING MALWARE EXECUTION 子节）

* 使用防护型钓鱼过滤与恶意域名阻断（原文指向 CIS 的 Malicious Domain Blocking and Reporting/MDBR，以及 Microsoft、macOS、Google 各自的钓鱼与恶意软件防护指南）；原文建议联系厂商或服务商了解可用的钓鱼过滤与恶意软件防护能力。
* **限制 macOS 与 Windows 用户拥有管理员权限 [CPG 2.E]。**
* **在管理用户账户时实施最小权限原则（PoLP）**，仅允许指定的管理员账户用于管理用途。
* **实施应用允许列表 [CPG 2.Q]。**原文定义其为「基于既定基线，枚举网络内被授权存在的应用组件」的安全控制，并指向 NIST 的 Application Allowlisting。
* **默认阻断宏 [CPG 2.N]。**
* **部署远程浏览器隔离（RBI）。**原文说明 RBI 在用户与恶意链接或二进制文件交互时将恶意样本隔离，阻止其在环境中扩散；应在远程工作站上配置 RBI，使恶意软件被限制在隔离边界内、无法访问组织资源。
* 使用 Quad9、Google Safe Browsing 等免费安全工具，在用户执行时识别并阻断恶意软件（原文指向 CISA 的 Free Cybersecurity Services and Tools 页面）。
* 建立自助式应用商店，客户仅可安装经批准的应用，并阻断其他来源的应用与可执行文件。

## 五、面向中小企业（SMB）的专项建议（原文 SMB 专章）

人类原文来源章节：MITIGATIONS — 中小企业专章（PDF 第 9 页）

* **培训与认证闭环。**原文要求培训项目演进时加入「培训检查」，以确认员工确已掌握培训所列全部内容。
* **可用的免费／官方培训资源（原文列举）：**NIST 在 *Small Business Cybersecurity Corner: Phishing* 页面为小企业提供免费反钓鱼培训资源；美国司法部（DOJ）向联邦机构提供 Anti-Phishing Training Program Support；联邦贸易委员会（FTC）在 *Cybersecurity for Small Businesses: Phishing* 页面提供小企业防钓鱼指导。原文亦鼓励中小企业采用商业化钓鱼意识培训项目。
* **识别网络钓鱼脆弱性。**原文鼓励联邦组织参加 CISA 的 Phishing Vulnerability Scanning 评估服务。
* **启用 MFA。**原文称启用强 MFA 是小企业保护其面向互联网业务账户免受钓鱼相关威胁的最佳方式，并指向 CISA 的 *More than a Password* MFA 页面（该页含一份 MFA 强度层级表，帮助用户按运营需求选择最强形式的 MFA）。
* **实施强口令策略。**原文要求口令符合强度策略：最小字符长度、数字、特殊字符、区分大小写，并禁止用户复用曾用口令。
* **实施 DNS 过滤。**

## 常见问题（答案均取自上述人类原文章节）

### CISA 这份指南对 DMARC 的具体要求是什么？

原文 MITIGATIONS 节要求双向配置：对收到的邮件启用 DMARC（与 SPF、DKIM 配合校验发送服务器，失败即判为伪造并隔离上报）；对发出的邮件将 DMARC 策略设为 reject [CPG 2.M]，使伪造本域的邮件在投递前于邮件服务器被拒绝，并通过 DMARC 报告获知伪造来源。

### 这份指南由哪些机构联合发布，版权状态如何？

由 CISA、NSA、FBI 与 MS-ISAC 联合发布，发布时间为 2023 年 10 月，文件标记 TLP:CLEAR，原文首页声明披露不受限制。本页为该文件的中文翻译与摘录，内容以人类官方原文为准。

## 人类官方原文来源（source）

* CISA / NSA / FBI / MS-ISAC — CISA 资源页：<https://www.cisa.gov/resources-tools/resources/phishing-guidance-stopping-attack-cycle-phase-one>
* CISA / NSA / FBI / MS-ISAC — 指南 PDF 全文（508 版）：<https://www.cisa.gov/sites/default/files/2025-03/Phishing%20Guidance%20-%20Stopping%20the%20Attack%20Cycle%20at%20Phase%20One%20508.pdf>

本页为对 CISA / NSA / FBI / MS-ISAC Phishing Guidance: Stopping the Attack Cycle at Phase One 的中文翻译与摘录，原文著作权归该机构所有，内容以人类官方原文为准。本页仅作中文可达性辅助，任何技术决策请以上述官方原文为准。

ztpop.net 邮件技术知识库 · 官方文献中译摘录系列

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/vnd-cisa-phishing-guidance.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
