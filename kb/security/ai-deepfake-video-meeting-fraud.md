---
title: "视频会议里「本人出镜」要求紧急付款，怎么判断是不是深伪？"
source: "https://ztpop.net/kb/ai-deepfake-video-meeting-fraud.html"
license: CC-BY 4.0
---

# 视频会议里「本人出镜」要求紧急付款，怎么判断是不是深伪？

**不要把希望寄托在「看出破绽」上**

网络上流传的深伪识别技巧——眨眼频率、面部边缘、光影不一致、侧脸失真——存在两个致命问题：**其一，这些破绽会随技术改进而消失；其二，它们要求人在高压场景下做精细视觉判断，而这恰恰是人类最不可靠的时候。**

更根本的是，这类识别是**被动防守**：即使你这次看出来了，也只是侥幸。防守方需要的是不依赖识别准确率的结构性方法。ENISA Artificial Intelligence and Cybersecurity Research 对 AI 相关安全研究方向的梳理中，也强调技术检测手段与流程性控制需要配合使用，而非相互替代。

**第一判据：会议入口从哪来**

结构性研判的第一问不是「画面真不真」，而是**「这个会议是怎么发起的」**：

* **低风险：**会议链接来自组织内部的日程系统，与会者是通过内部账号登录进入的，参会名单在内部目录中可核对。
* **高风险：**会议链接来自一封邮件、一条外部消息，或使用了组织平时不用的会议平台；参会者以访客身份加入、显示名可任意设置。

**判定条件：**凡是「链接由邮件送达 + 平台非常用 + 无内部身份登录」三者同时成立的会议，无论画面中出现谁，都不得作为付款或权限变更的授权依据。

**第二判据：交互是否真正可控**

合成内容在**实时、非预期的双向交互**下最容易失稳。可用的做法不是要求对方做某个特定动作（这类技巧一旦流传就会被针对性适配），而是把交互引向**攻击者无法预演的内容**：

* 提出一个只有双方知道、且未在任何书面渠道出现过的具体事实性问题。
* 切换话题到与本次「紧急事项」完全无关的日常工作细节，观察对方是否只能围绕既定剧本回应。
* 请对方当场在内部系统里完成一个可验证的操作（例如在内部工单中留言），而不是口头承诺。

**注意边界：**以上只是提高攻击成本，**不能作为最终授权依据**。真正的授权依据只有带外核验加既定审批流程。

**第三判据：请求本身是否绕过了流程**

和语音场景同理，最稳定的信号不在媒介层而在流程层。会议中出现以下情形，应直接按高风险处置：

* 要求跳过审批、要求保密、要求当场决定。
* 要求向新账号付款，或要求变更既有收款信息。
* 要求授予账号权限、重置口令、关闭某项安全控制。
* 拒绝把要求落到书面工单或内部系统中，坚持只在会议中口头交办。

**最后一条尤其值得重视：**合法的业务要求几乎总是愿意留痕，因为留痕对发起方也是保护。强烈抗拒留痕本身就是异常。

**组织侧应当固化的会议纪律**

1. **资金与权限类决策不得在视频会议中终结**：会议可以讨论，但生效必须落到既定审批系统，由系统内的身份完成。
2. **外部发起的会议默认不具授权效力**，需要授权时改由内部渠道重新发起。
3. **关键岗位的会议参与需要内部账号登录**，禁用匿名访客身份参加涉及资金与权限的会议。
4. **把「会议中被要求紧急付款」纳入演练场景**，检验员工是否会真的执行熔断。

这些纪律的共同点是：**把身份确认从「感官判断」转移到「系统中的可验证账号与流程」**。只要这个转移完成，合成内容做得多逼真都不再改变结果。

**与邮件通道的联动排查**

视频侧的欺骗通常伴随邮件侧的铺垫或收尾。事件研判时应回到邮件通道做联动排查：

* 会议邀请邮件的 SPF / DKIM / DMARC 判定结果与对齐情况，参见 RFC 7489 Domain-based Message Authentication, Reporting, and Conformance (DMARC)。
* 该发件域与本组织的历史通信记录、首次出现时间。
* 是否存在邮箱规则被篡改（自动转发、自动归档到冷门文件夹）——这是账号已被控制的典型痕迹。
* 同一时间窗内是否有其他员工收到同源邮件。

参考：[ENISA Artificial Intelligence and Cybersecurity Research](https://www.enisa.europa.eu/publications/artificial-intelligence-and-cybersecurity-research) ｜ [NIST AI 100-2e2025 Adversarial Machine Learning: A Taxonomy and Terminology](https://csrc.nist.gov/pubs/ai/100/2/e2025/final) ｜ [RFC 7489 Domain-based Message Authentication, Reporting, and Conformance (DMARC)](https://www.rfc-editor.org/rfc/rfc7489.html) ｜ [CISA Phishing Guidance: Stopping the Attack Cycle at Phase One](https://www.cisa.gov/resources-tools/resources/phishing-guidance-stopping-attack-cycle-phase-one)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/ai-deepfake-video-meeting-fraud.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
