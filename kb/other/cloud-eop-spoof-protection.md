---
title: "EOP 判定「未经身份验证的发件人」依据什么？复合身份验证该怎么读？"
source: "https://ztpop.net/kb/cloud-eop-spoof-protection.html"
license: CC-BY 4.0
---

# EOP 判定「未经身份验证的发件人」依据什么？复合身份验证该怎么读？

**为什么不能只看 SPF/DKIM/DMARC**

真实世界里大量域根本没有发布 DMARC 策略，还有大量合法邮件因转发而 SPF 失败。如果只按三项原始结果二分，要么放过一大批伪造，要么误杀一大批正常邮件。

因此 EOP 在原始认证结果之上再做一层**复合身份验证**，结论写在 Authentication-Results 头部的 `compauth=` 字段，并附带 `reason=` 说明依据。

**显式判定与隐式判定**

* **显式判定：**发件域发布了 DMARC 策略，直接依据 DMARC 结果得出结论。责任清晰，争议最小。
* **隐式判定：**发件域未发布 DMARC，平台结合 SPF/DKIM 结果、发送基础结构的历史信誉、该域以往的发送模式等信号推断这封信是否可信。

**运维含义：**隐式判定天然带不确定性。遇到某个合作方的邮件时好时坏，先查对方是否发布了 DMARC——推动对方发布策略，比在你这边不断加例外更能根治。

**读懂 compauth 的取值**

取值大致分四类：通过、失败、不适用、不确定。真正需要动作的是**失败**类，此时必须结合 `reason=` 判断原因属于哪一种：

* 发件域明确发布了策略且校验失败 ⇒ 大概率是真伪造，按策略处置即可。
* 隐式判定失败 ⇒ 需要人工确认，常见于对方认证配置不全的中小企业。

不看 reason 只看 fail 就加例外，是把真伪造和配置不全一起放行。

**内部冒充是最高优先级**

「发件域就是本组织的域，但未通过认证」这一类必须单独对待——不存在任何合法理由让外部 IP 用你的域发信却无法通过你自己配置的认证。

**处置：**这类邮件应设为隔离或直接拒绝，且**不应存在例外**。若某内部系统确实触发了此判定，正确做法是把它纳入 SPF/DKIM，而不是为它开口子。

**外部发件人标识与首次联系提示**

两项低成本高收益的配置：

* **外部发件人标识：**对所有来自组织外的邮件加可视标记。它直接瓦解了「显示名写成同事姓名」这类攻击的伪装效果。
* **首次联系安全提示：**对收件人从未通信过的发件人给出提示，与业务邮件欺诈的典型特征（陌生地址 + 紧急资金请求）高度吻合。

两者都不拦截邮件，只提供上下文，因此几乎没有误伤成本，应作为默认开启项。

**把结论沉淀到可检索的日志**

NIST SP 800-177 Rev.1 在可信邮件的整体框架中强调认证结果需要可被记录与审计。落地到运维，最低要求是把 `compauth` 结论、原始 SPF/DKIM/DMARC 结果、发件域与源 IP 一并留存，且**分字段存储而不是只存一个总评分**——事后复盘时，总评分无法告诉你当初是哪一层判错了。

参考：[Microsoft Learn：Anti-spoofing protection in Microsoft 365](https://learn.microsoft.com/en-us/defender-office-365/anti-phishing-protection-spoofing-about)、[NIST SP 800-177 Rev. 1：Trustworthy Email](https://csrc.nist.gov/pubs/sp/800/177/r1/final)、[RFC 8601：Message Header Field for Indicating Message Authentication Status](https://www.rfc-editor.org/rfc/rfc8601.html)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/cloud-eop-spoof-protection.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
