---
title: "Agari（Fortra）的身份欺骗防御与 DMARC Protection 如何运作？"
source: "https://ztpop.net/kb/agari-dmarc-identity-deception-2026.html"
license: CC-BY 4.0
---

# Agari（Fortra）的身份欺骗防御与 DMARC Protection 如何运作？

1
Agari（Fortra）的身份欺骗防御与 DMARC Protection 如何运作？
▼

**产品谱系与定位**

Agari 共同创立了 DMARC 标准，现为 Fortra Email Security 的组成部分。其产品线分工明确：**Cloud Email Protection** 以数据科学与机器学习模型拦截绕过传统控制的高级邮件威胁，防御 BEC、鱼叉钓鱼与冒充攻击；**Agari DMARC Protection（DMP）** 自动化 DMARC 认证与强制，阻止品牌域被冒用去钓客户；**Agari Phishing Defense（APD）** 拦截钓鱼、BEC 与其他身份欺骗攻击；**Agari Phishing Response（APR）** 面向 Microsoft 365 自动化钓鱼事件响应、修复与失陷遏制；此外还有 Suspicious Email Analysis 与 Threat Intel Service。Fortra 公开数据称，APR 可将员工上报事件的安全运营中心响应时间**最多缩短 95%**，把原本需要数月才能发现的失陷压缩到分钟级。

**核心方法论：给「好邮件」建模而非匹配攻击签名**

这是 Agari 与传统安全邮件网关（SEG）最本质的区别。官方表述为：与识别攻击「数字签名」的传统控制**相反**，Agari 对**正常邮件与发件人行为建模——这种模型无法被伪造或欺骗**；通过理解消息背后的**身份与信任关系**、把握发件人与收件人之间长期形成的关系，在上下文中识别异常迹象。这一思路使其能够处理三类 SEG 难以覆盖的场景：一是零日攻击（无已知签名可匹配）；二是显示名欺骗与近似域名（认证全部通过）；三是账号接管——当员工在伪造的登录页或业务应用上被骗输入凭据，或误以为是必要更新而下载恶意软件之后，其行为会偏离长期建模出的「良好身份与行为」而被识别。

**DMARC 报告与 DMARC 的能力边界**

Fortra 官方文档区分两类 DMARC 报告：**聚合报告（RUA）**记录以你的域名义发送的消息的认证状态，包含发送域、发件 IP、日期以及 DKIM/SPF 检查结果，可用于识别欺骗尝试并规划未来的 reject 策略；**取证报告（RUF）**在邮件未通过 DMARC/SPF/DKIM 校验时生成，含主题、完整 From 地址与 URL，便于排障与定位攻击者发件 IP。建议做法是先 `none`、再 `quarantine`、最后 `reject`，并**设立专用邮箱**接收报告（企业级组织每天可能收到数百份）。同时必须清楚 DMARC 的边界——官方明确列出 DMARC **不能**做的事：不能扫描邮件恶意内容、**不能阻止使用近似域名（look-alike / cousin domain）的钓鱼**、不能检测和移除邮件内的恶意链接、不能监控出入站消息内容。这正是必须叠加身份欺骗防护的原因。

**落地能力与合规映射**

DMARC Protection 的工程能力包括：自动生成并托管 DMARC、SPF、DKIM 记录以降低管理负担；**第三方发件人管理**——持续识别、跟踪并管理代你发信的第三方，发现新发件人时告警，即便已知发件人与自定义发件人重叠也能处理；**入站 DMARC 可见性**——填补 M365 与 Exchange 基础设施不向发件方回报 DMARC 数据造成的盲区，并就域名被劫持用于针对员工的鱼叉钓鱼提供取证数据；与 Splunk、Azure Sentinel、Palo Alto Networks 等 SOAR/SIEM 的预配置集成及原生 API；结合 Fortra Takedown Services，用失败样本数据挖掘并下架钓鱼站点。合规侧可映射到美国国土安全部 **BOD 18-01**（联邦机构强制 DMARC）、英国 NCSC 的 **Mail Check** 要求，以及 FISMA；对 Google、Yahoo 等收件方提出的批量发件人认证要求，未达成 reject 策略将直接影响送达。

参考：Fortra 官方产品页《Fortra's Agari, part of Fortra Email Security》：<https://www.fortra.com/agari>；Fortra Email Security《Agari DMARC Protection》：<https://emailsecurity.fortra.com/solutions/email-security/dmarc>

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/agari-dmarc-identity-deception-2026.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
