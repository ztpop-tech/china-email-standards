---
title: "Microsoft Defender for Office 365 的反钓鱼保护包含哪些能力？"
source: "https://ztpop.net/kb/defender-office365-antiphishing-policy.html"
license: CC-BY 4.0
---

# Microsoft Defender for Office 365 的反钓鱼保护包含哪些能力？

1
Microsoft Defender for Office 365 的反钓鱼保护包含哪些能力？
▼

**威胁分类**

微软官方文档把钓鱼细分为几类并分别说明其特征：鱼叉式钓鱼（针对特定收件人做过侦察后定制内容）、鲸钓（针对高管等高价值目标以求效果最大化）、商务邮件入侵 BEC（伪造受信任发件人如财务主管、客户、合作伙伴，诱使收件人批准付款、转账或泄露客户数据），以及勒索软件——文档明确指出勒索几乎总是从钓鱼邮件开始，反钓鱼能力虽不能解密文件，但能拦截关联的初始钓鱼消息。

**所有云邮箱的基础能力**

基础层面向所有云邮箱提供四项能力：一是欺骗智能（spoof intelligence），用于审阅来自外部与内部域的被检出仿冒发件人并手工放行或阻断；二是反钓鱼策略，可开关欺骗智能、开关 Outlook 中的未验证发件人标识、并指定对被阻断仿冒发件人的处置动作，其中包含「当邮件被判定为仿冒时遵从发件方 DMARC 策略」的开关，用于控制显式 DMARC 校验失败且策略为 quarantine 或 reject 时的行为；三是租户允许/阻止列表中的仿冒发件人条目；四是隐式邮件身份验证——在 SPF、DKIM、DMARC 之外叠加发件人信誉、发件历史、收件历史与行为分析等信号来识别伪造发件人。

**Defender for Office 365 追加能力**

在基础层之上，Defender for Office 365 的反钓鱼策略可配置：针对特定发件人与发件域的冒充防护（impersonation protection）、邮箱智能（mailbox intelligence，基于收件人历史通信图谱识别异常）、以及可调节的钓鱼判定阈值；被检出的冒充尝试可在冒充洞察（impersonation insight）中查看明细。此外还提供 Campaign Views——用机器学习与启发式识别针对整个服务与本组织的协同钓鱼活动，以及攻击模拟训练，供管理员向内部用户投放仿真钓鱼邮件做教育。

**配置建议**

从文档结构可以读出清晰的分层：先把基础层的欺骗智能与遵从发件方 DMARC 策略打开，作为对抗直接伪造的第一道线；再对高管、财务、HR 等高价值账号与常被仿冒的合作方域名逐一配置冒充防护，因为冒充类攻击往往并不伪造域名而是使用近似域或仅改显示名，基础层的认证校验对此无能为力；最后用 Campaign Views 做面上的活动级研判，用攻击模拟训练闭环人员侧短板。需注意冒充防护与邮箱智能属于 Defender for Office 365 层能力，仅有内置基础防护的租户不具备。

参考：Microsoft Learn 官方文档《Anti-phishing protection in cloud organizations》（Microsoft Defender for Office 365），https://learn.microsoft.com/en-us/defender-office-365/anti-phishing-protection-about

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/defender-office365-antiphishing-policy.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
