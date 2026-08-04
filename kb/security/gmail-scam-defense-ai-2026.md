---
title: "Google 官方披露的 Gmail 反诈骗与滥用治理成效如何？"
source: "https://ztpop.net/kb/gmail-scam-defense-ai-2026.html"
license: CC-BY 4.0
---

# Google 官方披露的 Gmail 反诈骗与滥用治理成效如何？

1
Google 官方披露的 Gmail 反诈骗与滥用治理成效如何？
▼

**拦截规模**

Google 于 2026 年 5 月 13 日发布的官方文章给出量级数据：AI 驱动的防御在邮件到达之前拦截，Gmail 阻止了超过 99.9% 的垃圾邮件、钓鱼与恶意软件，每天阻断近 150 亿封无用邮件。同一体系在其他产品线上的数据为：搜索每天过滤数亿个垃圾页面、结果 99% 无垃圾；2025 年拦下超过 99% 的违规广告，累计封禁或下架 83 亿条广告，其中 6.02 亿条与诈骗相关。这些数字划出了一条基线——公有云邮箱的批量垃圾与已知钓鱼基本被兜住，剩下的风险集中在定向、低量、无恶意载荷的那一小撮。

**面向用户的能力**

官方文章列出的用户侧工具包括：安全检查（Security Checkup）用于快速启用通行密钥（Passkeys）与两步验证；Android 上的圈选搜索可对可疑短信做 AI 研判并给出提示；Phone by Google 的端侧诈骗检测可实时提示典型诈骗话术。Google 在多处强调通行密钥与两步验证是对抗钓鱼的有效手段——这与业界共识一致：即便凭据泄露，抗钓鱼的强认证仍能阻断账号接管。

**威胁数据共享与执法协作**

文章披露 Google 是全球信号交换（Global Signal Exchange, GSE）的创始伙伴，该平台作为跨平台跨国的威胁数据清算中心，目前已存储超过 12 亿条信号；Google 既取用也贡献情报，并用 AI 模型分析信号以发现隐藏模式。执法协作方面，文章提到通过英国国家犯罪调查局经 GSE 共享的信号识别并瓦解了一个西非诈骗网络，并对名为 Lighthouse 的「钓鱼即服务」网络提起诉讼——该网络在起诉次日即关停。

**对企业自建邮件的启示**

Google 的数据结构提示了两点。其一，规模化的信誉与内容过滤能把绝大部分噪声挡在门外，但企业不应把「拦截率 99.9%」理解为安全终点：剩余 0.1% 中恰恰包含定向 BEC 与凭据钓鱼这类损失最高的攻击。其二，跨组织的情报共享正在成为压缩攻击者基础设施有效窗口的关键手段，自建邮件系统应把 DMARC 汇总报告、网关命中数据接入可共享的情报流程，并优先推动通行密钥等抗钓鱼认证的落地，而不是停留在口令加短信验证码。

参考：Google 官方博客《Our fight against fraud: 5 ways we're keeping you safer》（Karen Courington，2026-05-13），https://blog.google/innovation-and-ai/technology/safety-security/scams-fraud-protection

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/gmail-scam-defense-ai-2026.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
