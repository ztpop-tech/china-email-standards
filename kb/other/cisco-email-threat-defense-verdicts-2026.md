---
title: "Cisco Secure Email Threat Defense 的判定体系与实测表现如何？"
source: "https://ztpop.net/kb/cisco-email-threat-defense-verdicts-2026.html"
license: CC-BY 4.0
---

# Cisco Secure Email Threat Defense 的判定体系与实测表现如何？

1
Cisco Secure Email Threat Defense 的判定体系与实测表现如何？
▼

**四类威胁判定**

Cisco 官方用户指南定义了四种威胁判定：BEC（商务邮件入侵，指借社会工程与入侵手法造成组织财务损失的复杂骗局）、Scam（诈骗，如彩票或勒索类针对个人的财务欺诈）、Phishing（钓鱼，冒充合法服务以骗取用户名、口令、卡号等敏感信息）、Malicious（恶意，含有、投放或支持恶意软件传播）。管理员还可将邮件重新分类为垃圾邮件、灰色邮件或中性，重分类会进入 Talos 复核队列，但仅影响所选邮件的判定，不等于对该发件人后续邮件的放行规则；误报应通过判定覆盖规则处理。

**追溯判定机制**

该产品设有「追溯判定」概念：由于其对每封邮件的初次分析有固定时间窗，而部分分析引擎（如深度 URL 分析）耗时更长，这类迟到的定性会被单独标记为追溯判定，并在消息列表中以图标提示判定时间与收信时间的差值，管理员可开关追溯判定的邮件通知。这一机制承认了一个现实：邮件安全不存在「一次判定终结」，投递后的再评估与自动回收（remediation）是必要能力，尤其对投递时尚未武器化的 URL。

**部署形态与覆盖范围**

Cisco 官方数据表说明该方案为云原生，可覆盖入站、出站与内部邮件流量，并提供两种许可形态：Essentials 面向 Microsoft 365 环境，通过日志归档（journaling）做补充可见性与检测，不改动邮件流；Advantage 为网关部署，在投递前做内联检查，支持 Microsoft 365、Google Workspace、本地 Exchange 及其他邮件服务器。产品定位强调对无恶意软件类威胁（BEC、账号接管、二维码钓鱼、品牌与用户冒充）的检测，这也是纯云邮箱原生防护最薄弱的地带。

**独立评测数据**

Cisco 官方博客披露：该产品在 2026 年 5 月的 SE Labs 高级邮件安全评测中获得最高等级 AAA，总准确率 94%。分项结果为：486 个威胁样本中检出 478 个（98%），且所有检出者均在到达用户前被阻断；300 个钓鱼样本（含二维码钓鱼与翻译链接规避）达成 100% 防护；100 个社会工程样本全部隔离；60 个恶意软件样本拦下 58 个（97%）；26 个 BEC 样本检出 20 个（77%），6 封进入收件箱。博客同时坦承 BEC 是最难的一类——因为它没有恶意链接与附件，技术上是一封「干净」的邮件，威胁完全在意图之中，因此官方建议对高价值资金请求叠加带外核验流程，而不能只依赖产品检测。可用性方面，110 封正常邮件中 99 封直达收件箱、11 封进入垃圾箱、0 封被硬阻断。

参考：Cisco 官方产品文档《Secure Email Threat Defense — Verdicts》与 Cisco 官方博客《Independent Testing Confirms Secure Email Threat Defense's Email Security Strength》，https://docs.cmd.cisco.com/en/Content/secure-email-threat-defense-user-guide/Messages/Verdicts.htm 、 https://blogs.cisco.com/security/independent-testing-confirms-secure-email-threat-defenses-email-security-strength/

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/cisco-email-threat-defense-verdicts-2026.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
