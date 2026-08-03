---
title: "Microsoft 365 高级反钓鱼策略如何配置？"
source: "https://ztpop.net/kb/microsoft-365-advanced-anti-phishing.html"
license: CC-BY 4.0
---

# Microsoft 365 高级反钓鱼策略如何配置？

1
Microsoft 365 高级反钓鱼策略如何配置？
▼

**反钓鱼策略入口**

在 Microsoft Defender for Office 365 的「威胁策略 → 反钓鱼」中创建/编辑策略，作用于 Exchange Online Protection（EOP）与 Defender 的保护层；建议为高管与重点部门设专用高优先级策略，确保优先匹配。

**冒充保护**

启用用户冒充保护（列出受保护邮箱/显示名，如 CEO、财务）与域名冒充保护（保护本域及相似域名/已注册品牌域名），对匹配邮件隔离或告警。开启「邮箱智能（Mailbox Intelligence）」基于用户历史通信模式识别异常冒充。

**欺骗与认证**

开启欺骗智能以处理未通过 SPF/DKIM 且声称来自本域的欺骗；结合租户内强制 DMARC 隔离（对 DMARC=fail 入站隔离）。确保入站域已正确发布并校验 SPF/DKIM/DMARC 记录，降低伪造成功率。

**高级投递与附件链接**

配置「高级投递」对安全通报/钓鱼模拟（如第三方培训）免过滤；启用安全附件（Safe Attachments）动态沙箱与「重新设置定向检测」、安全链接（Safe Links）对 URL 做点击时改写与实时检测，覆盖邮件正文与附件内链接。

参考：Microsoft 365 Defender 文档《反钓鱼策略（Defender for Office 365）》、Exchange Online Protection 与 Safe Attachments/Safe Links 说明。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/microsoft-365-advanced-anti-phishing.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
