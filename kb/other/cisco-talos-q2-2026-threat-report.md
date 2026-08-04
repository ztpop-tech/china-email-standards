---
title: "Cisco Talos 2026 年 Q2 事件响应趋势显示哪些邮件攻击变化？"
source: "https://ztpop.net/kb/cisco-talos-q2-2026-threat-report.html"
license: CC-BY 4.0
---

# Cisco Talos 2026 年 Q2 事件响应趋势显示哪些邮件攻击变化？

1
Cisco Talos 2026 年 Q2 事件响应趋势显示哪些邮件攻击变化？
▼

**钓鱼回潮**

本季度钓鱼成为最主要的初始访问手段，出现在超过一半的 Cisco Talos 事件响应（Talos IR）参与事件中（上季度约为三分之一）。攻击者持续创新投递方式以规避防御：部署内嵌 QR 码的 PDF，绕过只解析文本的邮件网关；并将链接托管于 SharePoint 等受害组织信任的云平台上，借声誉过滤并显得更可信。

**认证滥用激增**

认证滥用本季出现在 65% 的参与事件中（上季度为 35%），攻击者频繁通过对抗式中间人（AitM）代理、会话令牌窃取、MFA 疲劳攻击与自注册设备等手段绕过或击败多因素认证（MFA）。

**具体活动与勒索软件**

UAT-11764 是针对澳大利亚组织的持续性 QR 码钓鱼活动，利用被攻陷的 Microsoft 365 账号收割凭据并经内部联系人列表传播，创建收件箱规则以规避检测、借 SharePoint 托管恶意文档并继续发送钓鱼邮件。ARToken 是一个与 EvilTokens 关联的钓鱼即服务（PhaaS）平台，暴露 80+ API 端点，支持设备码钓鱼、PRT 持久化、BEC 操作与 SharePoint 外泄。勒索软件（含首次响应的 Sinobi，以及 Nitrogen、Warlock）占逾 20% 的参与事件，并武器化被篡改的 MeshAgent 二进制与 Zoho Assist 等合法 RMM 工具。

**防御建议**

实施策略以阻断或标记含 PDF 内 QR 码的可疑邮件；对 M365 账号强制防钓鱼 MFA（phishing-resistant MFA）；监控可疑收件箱规则创建与异常 SharePoint 文件暂存作为入侵后指标；监控设备码（device code）认证、强化条件访问策略、防御基于令牌的攻击。因 UAT-11764 武器化 SharePoint/M365 等可信基础设施，传统邮件安全网关易被绕过。

参考：Cisco Talos Intelligence Group《IR Trends Q2 2026》官方博客：https://blog.talosintelligence.com/ir-trends-q2-2026/

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/cisco-talos-q2-2026-threat-report.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
