---
title: "Zscaler ThreatLabz 2026 钓鱼与初始访问报告揭示了哪些邮件攻击趋势？"
source: "https://ztpop.net/kb/zscaler-email-attack-trends-2026.html"
license: CC-BY 4.0
---

# Zscaler ThreatLabz 2026 钓鱼与初始访问报告揭示了哪些邮件攻击趋势？

1
Zscaler ThreatLabz 2026 钓鱼与初始访问报告揭示了哪些邮件攻击趋势？
▼

**量与质反转**

基于 Zscaler Zero Trust Exchange 的全球遥测，钓鱼总量连续第二年同比下降约 20%，但攻击效力与复杂度激增。攻击者以生成式 AI 消除“语法差”与通用诱饵等传统痕迹，转向高保真、AI 加速的精准诱饵，并越来越多地超越收件箱——探查暴露的攻击面、验证被盗凭据、在加密流量内执行账户接管。

**AI 文本到站点**

ThreatLabz 识别出 413,524 个 AI 生成的站点实例（近 10% 被明确标记为恶意）。Manus AI、Blackbox AI、Lovable AI 等工具被武器化，能在数分钟内生成品牌一致、高保真的钓鱼门户，此前需数天手工开发。服务业（Services）受击同比激增 65.5%，攻击者利用账单、入职、支持续费等信任型工作流；制造业与政府仍是邮件钓鱼主要目标，政府受击增 50%。

**加密盲点与会话劫持**

95.2% 的钓鱼尝试隐藏于加密流量（87% 恶意活动经 HTTPS 投递），绕过缺乏深度 TLS 检测的旧式安全栈；Microsoft 与 Google 是最常被仿冒的品牌。BlackForce 等复杂工具包被部署以劫持活动会话、实时绕过 MFA。欺骗（deception）遥测在六个月内记录来自 137 万个独立攻击 IP 的 8990 万次敌对交互，显示在初始入侵前攻击者已大规模扫描与验证凭据。

**防御建议**

超越静态域名封锁，实施行为检测以对指向自动化平台的异常流量模式告警；将终端与这些服务的通信限制在组织已授权的工作流内；以 AI 驱动的邮件安全分析消息语义意图，并与威胁情报社区共享 webhook 结构等 IOC。Zscaler 主张以零信任架构（隐藏应用、完整 TLS/SSL 检测）打破从发现到外泄的攻击链。

参考：Zscaler ThreatLabz《2026 Phishing and Initial Access Report》官方博客：https://www.zscaler.com/blogs/security-research/one-click-compromise-threatlabz-2026-phishing-and-initial-access-report

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/zscaler-email-attack-trends-2026.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
