---
title: "Mandiant M-Trends 2026 如何刻画邮件与身份相关的 APT 入侵活动？"
source: "https://ztpop.net/kb/mandiant-email-apt-activity-2026.html"
license: CC-BY 4.0
---

# Mandiant M-Trends 2026 如何刻画邮件与身份相关的 APT 入侵活动？

1
Mandiant M-Trends 2026 如何刻画邮件与身份相关的 APT 入侵活动？
▼

**速度崩溃**

基于 2025 年超过 50 万小时事件调查，Mandiant 发现初始访问到转交二级威胁组织的中位时间，从 2022 年的逾 8 小时骤降至 2025 年的 22 秒。初始访问代理（IAB）如同流水线第一道工序，一旦入侵成功便以近乎即时速度将访问凭据转交负责勒索、窃密或破坏的专门团队，几乎不留人工响应空间。

**向量结构转移**

漏洞利用占可识别初始向量的 32%，连续保持首位；语音钓鱼（vishing）跃升为第二大初始感染向量，整体占 11%，在云入侵案例中高达 23%，主要由 ShinyHunters 与 Scattered Spider 等犯罪组织驱动；相比之下，传统邮件钓鱼占比明显下降，反映企业长期倚重的邮件过滤防线已不足以应对新型社会工程。

**身份与 SaaS 导向的邮件活动**

Mandiant 将针对身份提供商与 SaaS 平台的攻击归为多个集群（包括 UNC6661、UNC6671 与 UNC6240/ShinyHunters）。攻击者冒充 IT 人员致电员工，以“更新 MFA 设置”为幌子诱导其访问凭据窃取链接；得手后利用窃取的 SSO 凭据与 MFA 码注册自有 MFA 设备，横向移动并从 SaaS 平台（如 SharePoint、OneDrive）窃取数据；部分行动还利用被控邮箱向联系人发送更多钓鱼邮件以延续攻击链，最终由 UNC6240 实施勒索。攻击者亦升级骚扰式勒索策略。

**防御建议**

对语音钓鱼保持警惕，并对员工做身份核验与反社工培训；监控异常 MFA 设备注册与 OAuth 令牌滥用；强化边缘网络设备（VPN、防火墙）与 Tier-0 虚拟化栈的遥测（此类设备常缺乏标准 EDR 可见性）；以实时可见性与自动化响应对抗秒级访问转交。Mandiant 强调：绝大多数成功入侵仍源于人为疏忽与系统性漏洞，但被利用的速度已彻底改变防御者的响应数学。

参考：Mandiant（Google Cloud）《M-Trends 2026》官方报告：https://www.mandiant.com/products/services/m-trends

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/mandiant-email-apt-activity-2026.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
