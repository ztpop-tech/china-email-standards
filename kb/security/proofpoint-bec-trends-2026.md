---
title: "Proofpoint 最新 BEC（商业邮件入侵）趋势有哪些关键发现？"
source: "https://ztpop.net/kb/proofpoint-bec-trends-2026.html"
license: CC-BY 4.0
---

# Proofpoint 最新 BEC（商业邮件入侵）趋势有哪些关键发现？

1
Proofpoint 最新 BEC（商业邮件入侵）趋势有哪些关键发现？
▼

**攻击规模与经济动机**

根据 FBI 互联网犯罪报告，BEC 造成的年度损失超过 27 亿美元，约为勒索软件损失的 80 倍。BEC 攻击通常冒充可信发件人，诱导收件人相信正在与信任对象交互，进而完成欺诈性银行转账或付款；由于不依赖恶意载荷即可生效，传统防病毒难以发现，防御尤为困难。

**Proofpoint 检测能力**

Proofpoint 的 Advanced BEC Defense 由名为 Supernova 的 AI 检测引擎驱动，使识别出的威胁数量提升 17 倍，检测范围扩展到多种邮件欺诈。该引擎对消息头数据、发件人 IP、收发关系、发件信誉做深度分析，并用大语言模型（LLM）语义分析正文情感与语言以判断是否为 BEC 威胁；行为机器学习引擎追踪异常发信量、异常 IP、收件人是否曾见过该发件人等信号，实时检测异常。据 Proofpoint 披露，其每月平均拦截约 6600 万次 BEC 攻击。

**典型攻击手法**

常见手法包括：显示名仿冒（display-name spoofing）、相似域名（lookalike domains）、以及利用被攻陷的供应商账号发起发票欺诈（supplier invoicing fraud）。Proofpoint 观察到攻击者会动态分析消息以识别供应商发票欺诈战术，并标记最常被利用的主题如礼品卡诈骗（gift carding）、供应商发票欺诈与工资单篡改（payroll diversion）。

**防御要点**

有效防御需要技术+教育的整体方法：在邮件到达收件箱前检测并阻断冒名威胁；对最易被攻击的用户以及存在潜在账户风险的第三方供应商做可见性管理，并在供应商域名及其仿冒域名出现威胁时主动通知；以自动化加速响应；同时通过培训让用户识别并上报邮件欺诈。对敏感付款务必执行带外核验。

参考：Proofpoint《Five Steps to Combat Business Email Compromise》官方方案简报：https://proofpoint.com/uk/resources/solution-briefs/five-steps-to-combat-bec （另据 Proofpoint《State of the Phish》，其每月平均拦截约 6600 万次 BEC 攻击）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/proofpoint-bec-trends-2026.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
