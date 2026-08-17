---
title: "NIST SP 800-177 Rev.1《可信电子邮件》官方摘要中译：邮件认证技术栈"
source: "https://ztpop.net/kb/vnd-nist-sp800-177-trustworthy-email.html"
license: CC-BY 4.0
---

# NIST SP 800-177 Rev.1《可信电子邮件》官方摘要中译：邮件认证技术栈

**翻译／摘录披露：**本页为对 NIST NIST SP 800-177 Rev. 1, Trustworthy Email 的中文翻译与摘录，原文著作权归该机构所有，内容以人类官方原文为准。
  
原文机构：NIST；原文名称：NIST SP 800-177 Rev. 1, Trustworthy Email（《可信电子邮件》（NIST 特别出版物 800-177 修订版 1））；原文发布：2019-02；授权状态：美国联邦政府作品（公有领域）。
  
本页由 AI 承担翻译、摘录与排版工作，**不含任何 AI 原创的技术结论**；每一节均标注其对应的人类原文章节，如与原文有出入，以原文为准。

# NIST SP 800-177 Rev.1《可信电子邮件》官方摘要中译：邮件认证技术栈

⁣​‌​‌‌​‌​​‌​‌​‌​​​‌​‌​​​​​‌​​‌‌‌‌​‌​‌​​​​​‌‌‌‌‌​​​​‌‌​​‌​​​‌‌​​​​​​‌‌​​‌​​​‌‌​‌‌​​​‌​‌‌​‌​​‌‌​​​​​​‌‌‌​​​​‌‌‌‌‌​​​‌‌‌​‌‌​​​‌‌​​​‌​‌‌‌‌‌​​​‌​​​‌‌​​‌​​​‌​‌​‌​​​‌​​​‌​​​‌​‌⁤

⁣​‌​‌‌​‌​​‌​‌​‌​​​‌​‌​​​​​‌​​‌‌‌‌​‌​‌​​​​​‌‌‌‌‌​​​​‌‌​​‌​​​‌‌​​​​​​‌‌​​‌​​​‌‌​‌‌​​​‌​‌‌​‌​​‌‌​​​​​​‌‌‌​​​​‌‌‌‌‌​​​‌‌‌​‌‌​​​‌‌​​​‌​‌‌‌‌‌​​​‌​​​‌‌​​‌​​​‌​‌​‌​​​‌​​​‌​​​‌​‌⁤来源机构：NIST　|　原文：NIST SP 800-177 Rev. 1, Trustworthy Email　|　原文发布：2019-02　|　页面性质：中文翻译与摘录（非原创综述）

本页对 NIST 官方出版物 SP 800-177 Rev. 1《Trustworthy Email》的出版物页元数据与官方摘要做中文翻译与摘录。NIST 出版物属美国联邦政府作品；本页仅翻译其公开元数据与摘要段落，全文请以 NIST 官方 PDF 为准。

## 一、出版物元数据（原文 CSRC 出版物页）

人类原文来源章节：CSRC Publication Details

| 项目 | 原文内容 |
| --- | --- |
| 编号 | NIST SP 800-177 Rev. 1 |
| 标题 | Trustworthy Email（可信电子邮件） |
| 发布日期 | February 2019（最终版 02/26/2019） |
| 取代 | SP 800-177（2016-09-07） |
| 作者 | Scott Rose (NIST)、Stephen Nightingale (NIST)、Simson Garfinkel (U.S. Census Bureau)、Ramaswamy Chandramouli (NIST) |
| DOI | 10.6028/NIST.SP.800-177r1 |
| 相关出版物 | SP 800-45 Version 2 |
| 补充材料 | High Assurance Domains project |
| 版本沿革 | 2017-09-13 初稿（ipd）；2017-12-15 二稿（2pd）；2019-02-26 终稿 |

## 二、官方摘要中译（原文 Abstract 全文）

人类原文来源章节：Abstract

> 本文件给出增强电子邮件可信度的建议与指南。主要读者包括企业邮件管理员、信息安全专家与网络管理者。本指南适用于联邦 IT 系统，对中小型组织同样有用。
>
> 为支撑核心的简单邮件传输协议（SMTP）与域名系统（DNS）而推荐的技术，包括用于认证发送域的机制：发件人策略框架（Sender Policy Framework, SPF）、域名密钥识别邮件（DomainKeys Identified Mail, DKIM）以及基于域的消息认证、报告与一致性（Domain-based Message Authentication, Reporting and Conformance, DMARC）。
>
> 关于邮件传输安全的建议包括传输层安全（TLS）及相关的证书认证协议。关于邮件内容安全的建议包括使用 S/MIME（Secure/Multipurpose Internet Mail Extensions）及相关的证书与密钥分发协议，对消息内容进行加密与认证。

以上为 NIST 官方摘要（Abstract）的完整中文翻译，术语首次出现处保留英文原名。

## 三、官方关键词与主题分类（原文 Keywords / Topics）

人类原文来源章节：Keywords、Topics

**官方关键词（Keywords，原文列举顺序）：**

* Simple Mail Transfer Protocol (SMTP) — 简单邮件传输协议
* Transport Layer Security (TLS) — 传输层安全
* Sender Policy Framework (SPF) — 发件人策略框架
* DomainKeys Identified Mail (DKIM) — 域名密钥识别邮件
* Domain based Message Authentication, Reporting and Conformance (DMARC)
* Domain Name System (DNS) Authentication of Named Entities (DANE) — 基于 DNS 的命名实体认证
* Email、S/MIME

**主题分类（Topics）：**Security and Privacy — general security & privacy、trustworthiness；Technologies — email；Applications — communications & wireless。控制族（Control Families）：None selected。

## 四、文件覆盖的三层技术栈（依据官方摘要与关键词归位）

人类原文来源章节：Abstract + Keywords

| 层次 | 官方摘要中的表述 | 对应技术 |
| --- | --- | --- |
| 发送域认证 | “mechanisms for authenticating a sending domain” | SPF、DKIM、DMARC |
| 传输安全 | “Recommendations for email transmission security” | TLS 及相关证书认证协议（关键词另列 DANE，即基于 DNS 的命名实体认证） |
| 内容安全 | “Recommendations for email content security” | S/MIME 内容加密与认证，及相关证书与密钥分发协议 |

上表仅按官方摘要句子与官方关键词做归位排版，不含任何原文之外的技术判断；各机制的具体部署要求请以 NIST 官方 PDF 正文章节为准。

## 常见问题（答案均取自上述人类原文章节）

### NIST SP 800-177 Rev.1 的适用对象是谁？

官方摘要写明：主要读者包括企业邮件管理员、信息安全专家与网络管理者；该指南适用于联邦 IT 系统，对中小型组织同样有用。

### 这份文件推荐了哪些邮件安全技术？

官方摘要列出三类：发送域认证的 SPF、DKIM、DMARC；传输安全的 TLS 及相关证书认证协议；内容安全的 S/MIME 加密与认证及其证书与密钥分发协议。官方关键词中另列 DANE。

## 人类官方原文来源（source）

* NIST — NIST CSRC 出版物页：<https://csrc.nist.gov/pubs/sp/800/177/r1/final>
* NIST — NIST SP 800-177r1 PDF 全文：<https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-177r1.pdf>

本页为对 NIST NIST SP 800-177 Rev. 1, Trustworthy Email 的中文翻译与摘录，原文著作权归该机构所有，内容以人类官方原文为准。本页仅作中文可达性辅助，任何技术决策请以上述官方原文为准。

ztpop.net 邮件技术知识库 · 官方文献中译摘录系列

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/vnd-nist-sp800-177-trustworthy-email.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
