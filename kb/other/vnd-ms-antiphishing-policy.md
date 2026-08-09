---
title: "Microsoft 365 反钓鱼策略官方文档中文摘录：Spoof、冒充保护与钓鱼阈值"
source: "https://ztpop.net/kb/vnd-ms-antiphishing-policy.html"
license: CC-BY 4.0
---

# Microsoft 365 反钓鱼策略官方文档中文摘录：Spoof、冒充保护与钓鱼阈值

**翻译／摘录披露：**本页为对 Microsoft Anti-phishing policies in Microsoft 365 (Microsoft Learn) 的中文翻译与摘录，原文著作权归该机构所有，内容以人类官方原文为准。
  
原文机构：Microsoft；原文名称：Anti-phishing policies in Microsoft 365 (Microsoft Learn)（《Microsoft 365 中的反钓鱼策略》）；原文发布：持续更新；授权状态：© Microsoft。原文受版权保护，本页仅做配置事实的结构化中译与要点摘录，不复刻原文全文。
  
本页由 AI 承担翻译、摘录与排版工作，**不含任何 AI 原创的技术结论**；每一节均标注其对应的人类原文章节，如与原文有出入，以原文为准。

# Microsoft 365 反钓鱼策略官方文档中文摘录：Spoof、冒充保护与钓鱼阈值

来源机构：Microsoft　|　原文：Anti-phishing policies in Microsoft 365 (Microsoft Learn)　|　原文发布：持续更新　|　页面性质：中文翻译与摘录（非原创综述）

本页对 Microsoft Learn 官方文档《Anti-phishing policies in Microsoft 365》做中文摘录与结构化整理。原文著作权归 Microsoft 所有；本页只转述配置项名称、默认值与适用范围等事实性内容，并逐节标注其在原文中的章节位置，配置行为一律以官方原文为准。

## 一、原文章节结构（便于对照定位）

人类原文来源章节：全文目录

1. Anti-phishing policies in cloud organizations（概述与适用产品）
2. Configure anti-phishing policies（配置指引）
3. Comparison of anti-phishing policies for all cloud mailboxes and in Defender for Office 365（能力对比）
4. Common policy settings（通用策略设置）
5. Spoof settings（含 Spoof protection and sender DMARC policies、Unauthenticated sender indicators）
6. First contact safety tip（首次联系安全提示）
7. Exclusive settings in anti-phishing policies in Microsoft Defender for Office 365（含 Impersonation settings、Phishing email thresholds、Spoofing vs. impersonation）

## 二、Spoof 设置（原文 “Spoof settings” 节）

人类原文来源章节：Spoof settings / Unauthenticated sender indicators

* **Enable spoof intelligence（启用伪造智能）：**对所有云邮箱的反钓鱼策略以及 Defender for Office 365 均可用。原文建议保持开启；默认策略与新建的自定义策略中默认启用，Standard／Strict 预设安全策略中同样启用。
* **未认证发件人标识（Unauthenticated sender indicators，位于 Safety tips & indicators，仅在 spoof intelligence 开启时可用）：**
  + *Show (?) for unauthenticated senders for spoof*：当邮件未通过 SPF／DKIM 且未通过 DMARC／复合认证时，在发件人头像位置显示问号。
  + *Show "via" tag*：当 From 域与 DKIM 签名域或 MAIL FROM 域不一致时显示 “via” 标签。
* **对被阻断的伪造发件人邮件的处置动作（Actions）：**
  + *Move messages to the recipients' Junk Email folders*（移入收件人垃圾邮件文件夹）——**原文标注为默认值**；
  + *Quarantine the message*（隔离邮件）——可选，并可指定隔离策略。
* **Honor DMARC record policy when the message is detected as spoof：**开启后可分别为发件域策略 `p=quarantine` 与 `p=reject` 指定动作（前者可选隔离或移入垃圾邮件，后者可选隔离或拒绝）。

## 三、冒充保护设置（原文 “Impersonation settings”，仅 Defender for Office 365）

人类原文来源章节：Exclusive settings … / Impersonation settings（User / Domain / Mailbox intelligence / Trusted senders and domains）

### 3.1 用户冒充保护（User impersonation protection）

* **Enable users to protect：**指定受保护的内部或外部发件人地址，原文标注上限为每策略 350 个；默认策略与自定义策略中**均未预置任何地址**。
* **检测到冒充时的动作：**Don't apply any action（**默认**）、Redirect、Move to Junk、Quarantine、Add Bcc、Delete before delivery。

### 3.2 域冒充保护（Domain impersonation protection）

* **Enable domains to protect：**指定受保护的发件域，原文标注上限为每策略 50 个；默认**未配置任何域**。
* **动作：**取值同用户冒充，默认为 **Don't apply any action**。

### 3.3 邮箱智能冒充保护（Mailbox intelligence）

* **Enable mailbox intelligence：**原文标注**默认开启**。
* **Enable intelligence for impersonation protection：**原文标注**默认关闭**；需与上一项同时开启才会执行动作。
* **动作：**默认 **Don't apply any action**。

### 3.4 受信任发件人与域（Trusted senders and domains）

* 作为冒充保护的例外项，原文标注上限 1,024 条；**子域需单独添加**；默认为空列表。
* 原文提示可将 Microsoft 365 系统发件人（例如 `noreply@email.teams.microsoft.com`）加入例外以避免误判。

## 四、高级钓鱼阈值四级（原文 “Phishing email thresholds”）

人类原文来源章节：Exclusive settings … / Phishing email thresholds

该设置仅存在于 Defender for Office 365 的反钓鱼策略中，用于控制机器学习判定钓鱼的敏感度：

| 级别 | 原文名称 | 行为（原文表述） |
| --- | --- | --- |
| 1 | Standard（**默认值**） | 按置信度（低／中／高／极高）施加相应严重程度的动作。 |
| 2 | Aggressive | 高置信度的判定按极高置信度处理。 |
| 3 | More aggressive | 中或高置信度的判定按极高置信度处理。 |
| 4 | Most aggressive | 低／中／高置信度的判定均按极高置信度处理（原文提示误报风险随级别递增）。 |

## 五、默认策略取值速查（依据原文事实整理）

人类原文来源章节：Common policy settings / Spoof settings / Impersonation settings / Phishing email thresholds

| 设置项 | 适用范围 | 默认值（原文标注） |
| --- | --- | --- |
| Default anti-phishing policy（自动创建） | 全体收件人 | 始终存在；名称与描述不可改，不可指定收件人 |
| Enable spoof intelligence | 所有云邮箱 & Defender | 开启 |
| 被阻断伪造发件人的动作 | 所有云邮箱 & Defender | Move messages to the recipients' Junk Email folders |
| 用户冒充 / 域冒充保护 | 仅 Defender | 保护列表为空，动作 Don't apply any action |
| Mailbox intelligence | 仅 Defender | 开启；但 intelligence for impersonation protection 关闭 |
| Phishing email thresholds | 仅 Defender | 1 - Standard |
| Trusted senders and domains | 仅 Defender | 空（上限 1,024） |

原文说明：默认反钓鱼策略为全体收件人提供 spoof protection 与 mailbox intelligence，但其余冒充保护与阈值项并未配置；需修改默认策略或新建自定义策略才能启用全部能力。

## 常见问题（答案均取自上述人类原文章节）

### Microsoft 365 默认反钓鱼策略是否已开启冒充保护？

按 Microsoft Learn 原文，默认反钓鱼策略为全体收件人提供 spoof protection 与 mailbox intelligence，但用户冒充与域冒充的保护列表为空、动作为 Don't apply any action，且 intelligence for impersonation protection 默认关闭；需修改默认策略或新建自定义策略才会生效。

### 高级钓鱼阈值默认是哪一级？

原文 Phishing email thresholds 一节标注默认值为「1 - Standard」，按低／中／高／极高置信度施加相应严重程度的动作；级别 2–4 逐步把较低置信度判定按极高置信度处理，原文提示误报风险随之上升。

## 人类官方原文来源（source）

* Microsoft — Microsoft Learn 原文：<https://learn.microsoft.com/en-us/defender-office-365/anti-phishing-policies-about>

本页为对 Microsoft Anti-phishing policies in Microsoft 365 (Microsoft Learn) 的中文翻译与摘录，原文著作权归该机构所有，内容以人类官方原文为准。本页仅作中文可达性辅助，任何技术决策请以上述官方原文为准。

ztpop.net 邮件技术知识库 · 官方文献中译摘录系列

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/vnd-ms-antiphishing-policy.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
