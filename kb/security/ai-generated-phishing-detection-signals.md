---
title: "AI 生成的钓鱼邮件有哪些可检测特征？传统的「语法错误」判据还成立吗？"
source: "https://ztpop.net/kb/ai-generated-phishing-detection-signals.html"
license: CC-BY 4.0
---

# AI 生成的钓鱼邮件有哪些可检测特征？传统的「语法错误」判据还成立吗？

1
AI 生成的钓鱼邮件有哪些可检测特征？传统的「语法错误」判据还成立吗？
▼

**官方结论：文本层面的传统判据正在失效**

FBI IC3 在 2024 年 12 月 3 日发布的公共服务公告 PSA241203 中明确警告：犯罪分子利用生成式 AI 以更大规模实施欺诈，并提高其骗局的可信度；生成式 AI 降低了犯罪分子欺骗目标所需的时间与精力，这些工具协助内容创作，并能**修正那些原本可作为欺诈警示信号的人为错误**。公告在「AI 生成文本」一节进一步列出：犯罪分子借助生成式 AI 工具完成语言翻译，以减少针对美国受害者的境外犯罪分子所产生的语法或拼写错误。这意味着以「中文夹生、语法别扭、拼写错误」为核心的人工识别培训要点，其有效性已被官方文献直接否定。

**IC3 记录的 AI 文本滥用形态**

依据同一份公告，AI 生成文本被用于社会工程、鱼叉式钓鱼以及包括交友、投资在内的金融欺诈骗局，或用于克服欺诈骗局的常见识别指标。公告列举的具体形态包括：批量生成虚构社交媒体账号以诱骗受害者汇款；更快地撰写发给受害者的消息，从而以可信内容触达更广受众；为加密货币投资欺诈等骗局的虚假网站生成内容；以及在欺诈网站中嵌入 AI 驱动的聊天机器人，诱导受害者点击恶意链接。对邮件防护而言，这意味着单封邮件的「文本质量」已不再具备区分度，且攻击的**规模与个性化程度可同时提升**。

**仍然可靠的检测面：基础设施与身份**

* **发信域与认证结果**：SPF、DKIM、DMARC 的对齐结果由密钥与 DNS 决定，不受文本生成质量影响；DMARC 强制策略对仿冒本域的拦截效果不因 AI 而衰减。
* **域名与基础设施年龄**：新注册域、近似域（lookalike）、一次性托管与短命 IP 仍需人工与自动化基础设施投入，是较难被文本模型抹平的成本项。
* **链接与附件的落地行为**：凭据收割页、OAuth 同意页、二跳跳转的动态分析结果与正文措辞无关。
* **会话与关系图异常**：首次通信、回复链劫持、Reply-To 与 From 不一致、异常收款账户变更，属于关系层信号而非语言层信号。
* **行为侧信号**：发送时间、批量指纹、模板复用度、收件人集合的选择模式。

**对「AI 文本检测器」应保持的克制**

需要特别注意：把「判定正文是否由 AI 生成」直接等同于「判定是否为钓鱼」在方法论上并不成立——合法的营销、客服与外贸沟通同样大量使用生成式工具，误判成本极高。NIST AI 100-2 E2025 在其对抗性机器学习分类法中系统描述了规避（evasion）类攻击，即攻击者构造输入以使 ML 模型产生错误判定；任何以文本风格为唯一输入的分类器都直接暴露在这一攻击面下。Google Threat Intelligence Group 在 2025 年 1 月 29 日发布的《Adversarial Misuse of Generative AI》中给出的观察是：其所分析的威胁行为者主要将生成式 AI 用作提升效率的生产力与研究工具，而非获得了突破性的新型攻击能力。因此正确的工程结论是：**维持并强化认证、基础设施与行为三层检测，把文本特征降级为辅助权重，而不是围绕「AI 味」重建检测体系**。

参考：FBI Internet Crime Complaint Center（IC3）《Criminals Use Generative Artificial Intelligence to Facilitate Financial Fraud》，Public Service Announcement，2024 年 12 月 3 日，https://www.ic3.gov/PSA/2024/PSA241203 ；Google Threat Intelligence Group《Adversarial Misuse of Generative AI》，2025 年 1 月 29 日，https://cloud.google.com/blog/topics/threat-intelligence/adversarial-misuse-generative-ai ；NIST AI 100-2 E2025《Adversarial Machine Learning: A Taxonomy and Terminology of Attacks and Mitigations》，2025 年 3 月，DOI 10.6028/NIST.AI.100-2e2025

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/ai-generated-phishing-detection-signals.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
