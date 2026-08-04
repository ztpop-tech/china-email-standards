---
title: "M3AAWG 地址验证最佳实践：减少退信与列表污染的运营基线"
source: "https://ztpop.net/kb/m3aawg-address-validation-bcp.html"
license: CC-BY 4.0
---

# M3AAWG 地址验证最佳实践：减少退信与列表污染的运营基线

## 概述

向不存在或不可接受的地址发信，会产生硬退信（5xx），拉高失败率、污染 IP 声誉，甚至触发黑名单。M3AAWG 地址验证 BCP 给出"发信前该做哪些校验"的运营基线：在用户注册时验证、在群发前清洗，从源头降低退信与列表污染。

## 验证层次

* **语法校验**：符合 RFC 5322 地址格式（本地部分@域，无非法字符）。
* **域与 MX 校验**：域有有效 DNS、存在 MX（或 A）记录可收信。
* **可接受性校验（Acceptability）**：通过 SMTP `RCPT TO` 试探（不实际发信）判断邮箱是否被接受；注意频率与礼貌，避免被当成探测/滥用。
* **确认式 opt-in**：发送确认邮件，用户点击才入列表，杜绝伪造/ typo 地址。

## 退信分类与处置

| 类型 | 示例 | 处置 |
| --- | --- | --- |
| 硬退信 | 无此用户（5.1.1） | 立即从列表移除 |
| 软退信 | 邮箱满/临时不可达 | 重试计数，超限移除 |
| 阻塞 | IP 被限流 | 降速、查声誉 |

## 隐私与合规边界

地址验证不得变成"账号枚举"或向第三方泄露列表；试探性 RCPT TO 应限速、标注来源，遵守接收方政策。这与 RRVS（RFC 8689）的"收件人有效性"视角互补：一个从发件方验证、一个从接收方声明。

## 对信创邮件与政企的启示

政企信创邮件系统做会员/客户群发前，应建"地址验证+退信处理"流水线：注册确认式 opt-in、群发前 MX/可接受性清洗、硬退信自动剔除以保护 IP 声誉。这与域名声誉管理、投递率工程构成完整闭环。

### 相关主题

* [M3AAWG 域名声誉管理](/kb/m3aawg-domain-reputation-bcp.html)：退信对声誉的影响
* [退信诊断完全手册](/kb/smtp-bounce-diagnosis-complete.html)：5xx/4xx 分类
* [RFC 7293 RRVS](/kb/rfc7293-rrvs-require-recipient-valid-since.html)：接收方有效性声明
* [邮件送达率工程](/kb/email-deliverability-engineering.html)：列表卫生
* [M3AAWG 垃圾陷阱指南](/kb/m3aawg-spam-trap-guide.html)：避免踩中陷阱

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/m3aawg-address-validation-bcp.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
