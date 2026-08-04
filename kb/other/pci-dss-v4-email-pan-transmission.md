---
title: "PCI DSS v4.0.1 对通过邮件传输持卡人数据有什么要求？"
source: "https://ztpop.net/kb/pci-dss-v4-email-pan-transmission.html"
license: CC-BY 4.0
---

# PCI DSS v4.0.1 对通过邮件传输持卡人数据有什么要求？

1
PCI DSS v4.0.1 对通过邮件传输持卡人数据有什么要求？
▼

**官方结论：不允许**

PCI SSC 官方 FAQ 1085 的回答是明确的「No」：PCI DSS 要求 4.2.2 禁止通过终端用户消息技术发送未受保护的主账号（PAN），无论是内部发送还是经由公共网络发送。电子邮件、即时通讯、短信与聊天均被视为终端用户消息技术，因而都必须满足要求 4.2.2。同时，依据要求 4.2.1，当持卡人数据经由开放的公共网络发送时，必须使用强加密与安全协议。

**请求接收持卡人数据的情形**

PCI SSC 官方 FAQ 1310 补充：PCI DSS 并不禁止使用终端用户技术（如电子邮件、短信、聊天）来请求或接收持卡人数据；但若使用终端用户消息技术接收或发送 PAN，该实体的通道必须按所有适用的 PCI DSS 要求加以保护，包括但不限于要求 4.2.1 与 4.2.2。此外，该实体与终端用户技术相关的系统（例如电子邮件服务器）将纳入 PCI DSS 范围。这意味着一旦允许邮件承载 PAN，整套邮件基础设施即进入 CDE 审计范围。

**为什么邮件特别危险**

邮件在投递过程中会经过多跳 MTA，并在收发双方服务器、备份与归档系统中长期留存；跳间 TLS 是机会性的，可被降级。误发、自动转发规则、移动端缓存与工单系统抄送都会让 PAN 扩散到不受控位置。相比之下，把持卡人数据引导到经认证的支付页面或安全上传门户，可将邮件系统整体排除在 CDE 之外，是成本最低的合规路径。

**落地控制**

* 在邮件网关与 DLP 上配置 PAN 正则与 Luhn 校验，命中即阻断外发并告警。
* 在可接受使用策略（对应要求 12.2.1）中明文禁止用邮件收发 PAN，并纳入员工培训。
* 对客服等易收到非预期持卡人数据的邮箱，建立发现即安全删除的处置流程。
* 确有业务需要时，仅在 PAN 已用强加密渲染为不可读后再经消息通道传输。

参考：PCI Security Standards Council 官方 FAQ 1085《Can unencrypted PANs be sent over e-mail, instant messaging, SMS, or chat?》，https://www.pcisecuritystandards.org/faqs/1085/ ；PCI SSC 官方 FAQ 1310《Are entities allowed to request that cardholder data be provided over end-user messaging technologies?》；PCI DSS v4.0.1 要求 4.2.1、4.2.2、12.2.1

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/pci-dss-v4-email-pan-transmission.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
