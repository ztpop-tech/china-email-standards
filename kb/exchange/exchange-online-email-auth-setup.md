---
title: "Exchange Online / Microsoft 365 如何配置邮件认证与防冒名？"
source: "https://ztpop.net/kb/exchange-online-email-auth-setup.html"
license: CC-BY 4.0
---

# Exchange Online / Microsoft 365 如何配置邮件认证与防冒名？

1
Exchange Online / Microsoft 365 如何配置邮件认证与防冒名？
▼

**SPF/DKIM**

M365 提供专属 SPF include(include:spf.protection.outlook.com) 与 DKIM 选择器(selector1/2.\_domainkey CNAME 指向 Microsoft)；租户密钥由 MS 托管。

**DMARC**

发布 \_dmarc TXT，结合 M365 的“防欺骗”与情报；对未对齐邮件启用隔离/拒绝，并开启“欺骗智能”识别仿冒。

**防冒名进阶**

启用反钓鱼策略（模拟用户/域名、首要执行展现名保护）、防接管(MFI)、以及 Defender for Office 365 的反钓鱼/安全附件/安全链接。

**混合注意**

混合环境需保证本地Exchange 出站也经 EOP 或正确 include，否则 SPF 断裂；迁移期用过渡 SPF 与中继信任。

参考：Microsoft Learn（连接电子邮件的 SPF/DKIM/DMARC；反钓鱼策略）；RFC 7489

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/exchange-online-email-auth-setup.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
