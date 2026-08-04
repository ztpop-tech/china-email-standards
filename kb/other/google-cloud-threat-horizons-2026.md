---
title: "Google Cloud Threat Horizons 报告揭示了哪些初始访问与凭据威胁趋势？"
source: "https://ztpop.net/kb/google-cloud-threat-horizons-2026.html"
license: CC-BY 4.0
---

# Google Cloud Threat Horizons 报告揭示了哪些初始访问与凭据威胁趋势？

1
Google Cloud Threat Horizons 报告揭示了哪些初始访问与凭据威胁趋势？
▼

**报告口径与核心结论**

该报告由 Google Cloud 安全团队、Google 威胁情报组（GTIG）与 Mandiant 共同撰写，统计 Google Cloud 环境中被利用的初始访问途径分布。报告指出：2025 上半年威胁行为者仍高度依赖弱口令、缺失凭据与配置错误；进入 2025 下半年，攻击者转向利用未修补的第三方漏洞获取初始访问。Google 明确说明，这些事件针对的是客户侧的外部暴露漏洞，**并不涉及 Google Cloud 核心基础设施被攻破**。Google 评估这一转变可能源于其「默认安全」策略与增强的凭据保护成功封堵了传统的、更易利用的路径，抬高了攻击门槛。

**初始访问途径分布（2025 下半年）**

* 软件类入口合计 **44.5%**（其中软件漏洞 30.9%、远程代码执行 RCE 13.6%），相比 2025 上半年的 2.9% 大幅跃升。
* 弱口令或无凭据：从上半年 **47.1%** 降至 **27.2%**。
* 配置错误：从 **29.4%** 降至 **21.0%**。
* 暴露的敏感 UI 或 API：从 **11.8%** 降至 **4.9%**。
* 其他：2.5%。

其中 RCE 占比从上半年 2.9% 增至下半年 13.6%，接近五倍增长。Google 提示该数据仅反映观察到的部分活动，未必代表全部客户。

**利用窗口坍缩为「天」级**

报告最值得邮件与身份运维关注的一点是时间线：漏洞披露到大规模利用的窗口**缩短了一个数量级，从数周变为数天**。Google 观察到威胁行为者在 React Server Components 严重 RCE 漏洞 CVE-2025-55182（俗称 React2Shell）公开披露后**约 48 小时内**就部署了 XMRig 挖矿程序；2025 年 11 月针对 XWiki 评估注入漏洞 CVE-2025-24893 的挖矿投放也呈现同样节奏。这意味着依赖人工补丁窗口的运维模式已经失效，包括 Webmail、OA 与邮件相关的对外 Web 组件在内，都必须假设补丁来不及。

**对邮件与身份体系的防御启示**

Google 给出的风险管理建议是转向**不可被轻易覆盖的默认安全配置**，并从三方面着手：以身份访问控制收敛权限、用集中可见性工具保护数据、以自动化手段强制安全态势。针对必须暴露在公网的服务，Google Cloud 提供 VPC Service Controls 隔离敏感数据、Identity-Aware Proxy 对每一次访问请求做验证。防御侧应从「手工打补丁」转向「自动化防御」——例如在 Web 应用防火墙（WAF）层下发虚拟补丁，在软件更新到位之前先于网络边缘中和利用。映射到邮件系统，即：Webmail 与管理后台前置 WAF 与身份代理、对外组件纳入自动化漏洞与配置扫描、邮箱账号全面启用强身份控制而非仅靠口令。

参考：Google Cloud《Cloud Threat Horizons Report H1-2026》官方 PDF：<https://services.google.com/fh/files/misc/cloud_threat_horizons_report_h12026.pdf>

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/google-cloud-threat-horizons-2026.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
