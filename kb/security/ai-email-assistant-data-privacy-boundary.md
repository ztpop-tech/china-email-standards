---
title: "部署 AI 邮件助手时，数据隐私与合规的边界应该怎么划？"
source: "https://ztpop.net/kb/ai-email-assistant-data-privacy-boundary.html"
license: CC-BY 4.0
---

# 部署 AI 邮件助手时，数据隐私与合规的边界应该怎么划？

1
部署 AI 邮件助手时，数据隐私与合规的边界应该怎么划？
▼

**第一问：数据会不会被用于训练**

这是最应当写进合同的一条。Microsoft 在 Microsoft 365 Copilot 的官方隐私文档中给出的表述是明确的：提示词、响应，以及通过 Microsoft Graph 访问的数据，不用于训练基础大语言模型，包括 Microsoft 365 Copilot 所使用的模型；文档同时说明这些交互数据在存储时被加密，并按照与组织之间的合同承诺、与 Microsoft 365 中的其他内容一并处理与存储。对于可选的客户反馈，文档说明其可能用于改进 Copilot，但不用于训练 Microsoft 365 Copilot 所使用的基础模型；文档还说明 Azure OpenAI 中可用的人工审核滥用监控在该服务中已选择退出。评估任何 AI 邮件助手时，都应要求供应商就「训练用途」「人工审阅」「日志留存期」三项分别给出书面承诺，而不接受笼统的「我们重视隐私」。

**第二问：权限边界是否被继承**

AI 助手的最大隐私风险之一，是它以一个高权限身份读取全部邮箱，从而绕过原有的最小权限设计——这与 OWASP LLM06:2025 所描述的「过度权限」根因完全一致（该条目举出的反例即为：本应在个人用户上下文中操作的扩展，却以通用高权限身份访问下游系统）。Microsoft 官方文档对此的表述是：Copilot 仅呈现每位用户使用与其他 Microsoft 365 服务相同的底层数据访问控制所能访问的数据，语义索引遵循基于用户身份的访问边界；对于经 Microsoft Purview 信息保护加密的数据（敏感度标签或 IRM），Copilot 会遵循授予该用户的使用权限；租户之间通过 Microsoft Entra 授权与基于角色的访问控制实现逻辑隔离。选型提问应当是：**助手是以「当前用户身份」还是以「服务账号身份」访问邮箱？共享邮箱与委派邮箱如何处理？敏感度标签与加密邮件是否被尊重？**

**第三问：数据去了哪里、留了多久**

Microsoft 文档说明：自 2024 年 3 月 1 日起，Copilot 被纳入 Microsoft 产品条款与数据保护附录中的数据驻留承诺，成为覆盖的工作负载，Advanced Data Residency 与 Multi-Geo 同步包含该承诺；针对欧盟用户设有额外保障以符合 EU Data Boundary，欧盟流量保留在 EU Data Boundary 内，而全球流量可被发送至欧盟及其他国家或地区进行 LLM 处理（文档亦注明由 Anthropic 作为子处理器提供的模型当前排除在 EU Data Boundary 之外）。文档另说明用户可通过 My Account 门户删除自己的 Copilot 活动历史（含提示词与响应），管理员可使用内容搜索与 Microsoft Purview 查看和管理数据并设置保留策略。跨境传输、子处理者名单与保留策略这三项，是邮件 AI 助手合规评估中最容易被忽略、却最可能触发监管问题的部分。

**第四问：法律义务如何落地**

NIST AI RMF 1.0 把「增强隐私（Privacy-Enhanced）」列为可信 AI 的七项特征之一，但框架本身为自愿采用，不替代任何法定义务。在欧盟 GDPR 语境下，邮件 AI 助手的部署至少需要回答：处理的**合法性基础**是什么（第 6 条）；是否满足**目的限制与数据最小化**（第 5 条）——「让助手读取全部历史邮件以便更好地回答」往往与最小化原则直接冲突；是否需要开展**数据保护影响评估**（第 35 条）——对全员邮箱内容进行系统化分析，通常落入「可能对自然人权利与自由造成高风险」的情形；以及是否落实了第 32 条要求的适当技术与组织措施。Microsoft 官方文档中亦声明 Copilot 符合其对 Microsoft 365 商业客户既有的隐私、安全与合规承诺，包括 GDPR 与 EU Data Boundary，并列出 ISO/IEC 27001、ISO/IEC 42001（AI 管理体系）等认证。

最后是一项常被漏掉的边界：**邮件中的个人数据并不都属于本组织**。收件箱里包含客户、供应商与第三方发来的内容，这些数据主体并未就「其邮件被送入 AI 模型分析」作出任何选择。因此在划定边界时，除了内部员工告知与培训，还应评估对外部数据主体的透明度义务，并在技术上对特定邮箱、特定标签或特定发件域的邮件设置排除范围，避免把「全量接入」当作默认配置。

参考：Microsoft Learn《Data, Privacy, and Security for Microsoft 365 Copilot》，https://learn.microsoft.com/copilot/microsoft-365/microsoft-365-copilot-privacy ；NIST AI 100-1《Artificial Intelligence Risk Management Framework (AI RMF 1.0)》第 3.6 节 Privacy-Enhanced，2023 年 1 月 26 日，DOI 10.6028/NIST.AI.100-1 ；Regulation (EU) 2016/679（GDPR）第 5、32、35 条，Official Journal of the European Union L 119/1，https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32016R0679 ；OWASP Top 10 for LLM Applications 2025，LLM02:2025 Sensitive Information Disclosure

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/ai-email-assistant-data-privacy-boundary.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
