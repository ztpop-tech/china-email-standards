---
title: "疑似 AI 钓鱼或深伪冒充事件，应急响应该怎么做？"
source: "https://ztpop.net/kb/ai-incident-response-deepfake.html"
license: CC-BY 4.0
---

# 疑似 AI 钓鱼或深伪冒充事件，应急响应该怎么做？

**先判断处于哪个阶段，决定先止损还是先取证**

接报后第一个决策不是「怎么查」，而是**「资金是否已经划出、凭据是否已经提交」**：

* **资金已划出**：时间是唯一变量，立即联系本方银行与收款行发起止付，同时按属地要求向执法机关报案。取证与之并行，不排队。
* **凭据已提交**：立即吊销该账号全部活动会话并重置凭据，检查邮箱规则、委托权限、应用授权。**只重置口令而不吊销会话，攻击者仍然在线**。
* **尚未造成后果**：以取证与扩散排查为主，避免打草惊蛇式的粗糙动作（例如立刻全域封禁发件域，可能让攻击者察觉并切换基础设施）。

整体流程可沿用 NIST SP 800-61 Rev.3 Incident Response Recommendations and Considerations 给出的事件响应组织方式，不必为 AI 相关事件另建体系。

**邮件证据的正确保全方式**

取证最常见的失误发生在第一分钟：**用「转发」把可疑邮件发给安全团队**。转发会丢失或改写原始头部，使后续鉴别结果、投递路径、Message-ID 全部失真。

**正确做法：**

* 以**附件形式转发**原始邮件，或直接从邮箱存储中导出原文件。
* 从网关日志中按 RFC 5322 Internet Message Format 的 Message-ID 提取该邮件的完整处理记录：接收时间、源 IP、TLS 情况、RFC 8601 Message Header Field for Indicating Message Authentication Status 鉴别结果、判定与动作。
* 保存 URL 的完整跳转链与最终落地页快照；**在隔离环境中访问，不要用办公终端点击**。
* 附件保持原样保存并计算散列值，不要在办公终端打开。

**语音与视频证据**

这类证据容易因「当时觉得没什么」而丢失，应在第一时间固定：

* 通话记录：时间、主叫号码、时长、接听人、对方提出的具体要求与措辞。**要求接听人尽快书面回忆并签署时间**，记忆随时间衰减很快。
* 语音留言、会议录音、会议平台的参会记录（加入时间、显示名、账号身份、IP 信息）原样保存，**不要转码**。
* 会议邀请的来源：链接从哪封邮件、哪个渠道送达。

注意：**不要在事件处置中投入大量精力去「鉴定这段音视频是不是合成的」。**该结论既难以快速得出，也不改变处置动作——无论真假，未经带外核验的资金与权限请求都不应执行。

**扩散排查：这类攻击极少只打一个目标**

单点处置完成后，必须做面上排查，检索维度：

* 同一发件域、同一发送 IP、同一 Reply-To、同一收款账号。
* 同一 URL 落地域名、同一附件散列。
* 相似主题模板、相似正文结构（用于发现改写变体）。
* 同一时间窗内投递给关键岗位的邮件。

**同时反查内部侧：**是否有其他账号出现异常登录、是否有新增的自动转发规则、是否有异常的大批量外发。若已存在失陷账号，攻击往往已经进入横向阶段。

**处置动作清单**

1. 吊销受影响账号的全部会话，重置凭据，检查并清除异常邮箱规则与委托权限。
2. 回收已投递的同源邮件（如平台支持），或至少在客户端标注告知。
3. 阻断相关发件域、IP、URL，并**记录阻断时间以便评估攻击者切换速度**。
4. 通知潜在受影响的内部人员与外部对手方；若对方账号疑似失陷，通过带外通道通知。
5. 对涉及资金的事项，同步财务与法务，保留完整决策与沟通链条。
6. 按属地要求完成对外报送，CISA Recognize and Report Phishing 说明了相应的报送渠道形式。

**复盘要产出可执行的改动，而不是一份报告**

复盘应回答四个问题，每个都要落到具体改动：

* **哪一层防线本应拦住但没有拦住？**（协议鉴别 / 网关判分 / 流程核验 / 身份认证）
* **流程在哪一环被绕过？为什么当事人没有执行熔断？**——如果原因是「不敢质疑高管」，那么要改的是管理层背书，不是再培训一次。
* **发现渠道是什么？**如果是对方或银行告知而非自身监控发现，说明可观测性有缺口。
* **哪些证据当时没有采到？**把缺失字段补进日志采集要求。

若事件涉及组织自有的 AI 组件（助手被注入、判分被绕过），复盘结论应同时回流到 NIST AI 100-1 Artificial Intelligence Risk Management Framework (AI RMF 1.0) 的 MANAGE 环节，更新台账、指标与处置机制。

参考：[NIST SP 800-61 Rev.3 Incident Response Recommendations and Considerations](https://csrc.nist.gov/pubs/sp/800/61/r3/final) ｜ [CISA Recognize and Report Phishing](https://www.cisa.gov/secure-our-world/recognize-and-report-phishing) ｜ [RFC 8601 Message Header Field for Indicating Message Authentication Status](https://www.rfc-editor.org/rfc/rfc8601.html) ｜ [NIST AI 100-1 Artificial Intelligence Risk Management Framework (AI RMF 1.0)](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/ai-incident-response-deepfake.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
