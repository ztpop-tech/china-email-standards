---
title: "Microsoft Defender for Office 365 反钓鱼：冒充保护与欺骗智能"
source: "https://ztpop.net/kb/microsoft-defender-anti-phishing.html"
license: CC-BY 4.0
---

# Microsoft Defender for Office 365 反钓鱼：冒充保护与欺骗智能

## 概述

Microsoft Defender for Office 365（原 ATP）的反钓鱼引擎是业界最成熟的商业实现之一，其能力维度可作为自建或信创邮件安全网关的能力对标。它在 SPF/DKIM/DMARC 之上，增加了"语义级"的钓鱼识别：不只看域名是否伪造，还看"是否冒充了某人/某域"。

## 核心能力

* **冒充用户保护（User impersonation）**：基于高管/VIP 列表，识别显示名或相似域冒充"老板"的邮件（BEC 主战场）。
* **冒充域名保护（Domain impersonation）**：识别 look-alike 域（如 micros0ft.com）、子域伪造。
* **欺骗智能（Spoof intelligence）**：区分"合法代发"（如邮件服务商代发）与"非法欺骗"，自动学习组织内的合法信封/信头映射。
* **邮箱情报（Mailbox intelligence）**：基于用户历史通信模式判断异常（从不联系的人突然发来紧急付款）。
* **安全收件箱（Safe inbox）**：可疑邮件隔离而非直接投递，附警示横幅。

## 与 DMARC 的分工

DMARC 解决"域名是否伪造"（基础设施层）；Defender 的冒充保护解决"身份是否冒充"（语义层）。两者互补：DMARC reject 拦掉硬伪造，冒充保护拦掉"域不同但像老板"的软钓鱼。这正是纵深防御的体现。

## 攻击模拟演练

Defender 提供攻击模拟训练（Attack Simulation Training），向员工发模拟钓鱼并给即时教学。这与 M3AAWG/ENISA 强调的"用户意识是最后一道闸"完全一致，是技术防线之外的必要补充。

## 对信创邮件与网关的启示

信创邮件安全网关的能力规划应覆盖上述维度：VIP 冒充库、look-alike 域识别、基于通信图的异常检测、隔离与警示、以及配套的员工钓鱼演练。以 Defender 为对标，可系统化补齐 BEC 防护短板。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/microsoft-defender-anti-phishing.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
