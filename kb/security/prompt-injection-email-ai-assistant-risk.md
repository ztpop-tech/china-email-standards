---
title: "提示词注入（prompt injection）会给邮件 AI 助手带来什么风险？如何防护？"
source: "https://ztpop.net/kb/prompt-injection-email-ai-assistant-risk.html"
license: CC-BY 4.0
---

# 提示词注入（prompt injection）会给邮件 AI 助手带来什么风险？如何防护？

1
提示词注入（prompt injection）会给邮件 AI 助手带来什么风险？如何防护？
▼

**官方定义：直接注入与间接注入**

OWASP Top 10 for LLM Applications 2025 的 LLM01:2025 条目定义：当用户提示以非预期方式改变 LLM 的行为或输出时，即出现提示词注入漏洞；这些输入即使对人不可见也能影响模型，因此提示词注入**不需要对人类可见或可读，只要内容能被模型解析即可**。条目区分两类：**直接提示词注入**指用户的提示输入直接以非预期方式改变模型行为，可能是故意的，也可能是无意的；**间接提示词注入**指 LLM 接受来自外部来源（如网站或文件）的输入，该外部来源的内容在被模型解读时改变了模型行为。OWASP 同时说明，提示词注入与越狱（jailbreaking）是相关概念且常被混用，越狱是提示词注入的一种形式，即攻击者提供的输入使模型完全无视其安全协议。

**为什么邮件是间接注入的高危载体**

Google 在 2025 年 6 月 13 日发布于官方安全博客的《Mitigating prompt injection attacks with a layered defense strategy》中把这一点讲得很直接：与攻击者直接把恶意命令输入提示的直接注入不同，间接提示词注入涉及隐藏在外部数据源中的恶意指令，**这些数据源可能包括电子邮件、文档或日历邀请**，用以指示 AI 外泄用户数据或执行其他越权动作。邮件的特殊性在于：任何人都可以向企业邮箱投递内容，无需任何前置权限；而 AI 邮件助手的核心用途恰恰是读取这些不受信内容并据以行动。OWASP LLM01 列出的攻击场景中亦包含针对 LLM 驱动的邮件助手的注入案例（对应 CVE-2024-5184），以及攻击者修改 RAG 检索库文档、载荷分割、多模态图片藏指令、对抗性后缀、多语言与编码混淆等手法。

**可能造成的后果**

* **邮箱数据外泄**：诱导助手把收件箱中的敏感邮件摘要或原文，经由渲染外链图片、生成含数据的 URL 等隐蔽通道回传攻击者。
* **代为发信与转发**：若助手持有发送权限，注入指令可让其自动转发邮件或向内部同事发出以真实身份签发的欺诈请求。
* **系统提示词泄露**：暴露安全规则、内部术语与集成拓扑，为后续攻击提供情报。
* **摘要污染**：篡改助手对邮件线程的总结，使用户基于错误结论作出付款或授权决定。
* **横向进入连接系统**：若助手可调用工单、CRM、文件存储扩展，注入即可延伸为跨系统操作。

**厂商公开的分层缓解与自建方案**

OWASP 在 LLM01 中首先给出一个诚实的前提：鉴于模型工作方式中固有的随机性影响，尚不清楚是否存在万无一失的提示词注入防范方法；其建议的缓解方向为约束模型行为、定义并校验预期输出格式、实施输入输出过滤、强制最小权限、**对高风险动作要求人工审批**、**隔离并标识外部内容**、开展对抗测试与攻击模拟。

Google 公布的分层策略包含五项内建于 Gemini 的防御：提示词注入内容分类器（在邮件与文件等格式中检测恶意指令并在 Workspace 数据查询时过滤）、安全思维强化（在提示内容周围加入定向安全指令，提醒模型执行用户指定任务并忽略对抗性指令）、Markdown 净化与可疑 URL 遮蔽（其 Markdown 净化器识别外部图片 URL 且不予渲染，并基于 Google Safe Browsing 遮蔽可疑链接）、用户确认框架（对删除日历事件等风险操作要求显式确认，即 Human-In-The-Loop）、以及面向终端用户的安全缓解通知。Microsoft 在 Azure AI Content Safety 中提供 Prompt Shields 统一 API，将对抗性输入分为 **User Prompt attacks**（原「Jailbreak risk detection」，涵盖试图更改系统规则、嵌入对话模拟、角色扮演、编码攻击等子类）与 **Document attacks（Indirect attack）**（防护来自外部文档等非用户直接提供信息的攻击，攻击者可能在这些材料中嵌入隐藏指令以获取对 LLM 会话的越权控制），并在内容生成前完成检测与拦截。

自建邮件 AI 助手时的最小可行护栏：邮箱凭据仅授予只读范围；外部邮件内容在拼入提示前用明确定界符包裹并标注为不可信数据；禁止模型输出直接触发发信、转发规则创建与外链渲染；对所有工具调用在下游系统侧做独立授权校验；完整记录提示词与工具调用日志以备取证。

参考：OWASP Top 10 for LLM Applications 2025，LLM01:2025 Prompt Injection，OWASP GenAI Security Project，https://genai.owasp.org/llm-top-10/ 及 OWASP 官方仓库 https://github.com/OWASP/www-project-top-10-for-large-language-model-applications ；Google Security Blog《Mitigating prompt injection attacks with a layered defense strategy》，2025 年 6 月 13 日，https://security.googleblog.com/2025/06/mitigating-prompt-injection-attacks.html ；Microsoft Learn《Prompt Shields in Azure AI Content Safety》，https://learn.microsoft.com/azure/ai-services/content-safety/concepts/jailbreak-detection ；MITRE ATLAS AML.T0051.000 / AML.T0051.001

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/prompt-injection-email-ai-assistant-risk.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
