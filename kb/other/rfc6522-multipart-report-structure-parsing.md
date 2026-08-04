---
title: "退信和投诉报告的 multipart/report 结构是怎样的？如何正确解析？"
source: "https://ztpop.net/kb/rfc6522-multipart-report-structure-parsing.html"
license: CC-BY 4.0
---

# 退信和投诉报告的 multipart/report 结构是怎样的？如何正确解析？

1
退信和投诉报告的 multipart/report 结构是怎样的？如何正确解析？
▼

**为什么要有一个统一的报告容器**

邮件系统会产生多种「关于另一封邮件」的管理性报告：投递失败通知、垃圾投诉、阅读处置通知。这些报告如果各用各的格式，接收方就需要为每一种单独写解析逻辑，而且无法可靠地把报告与被报告的原始邮件关联起来。

RFC 6522 为此定义了 **multipart/report** 媒体类型，作为承载各类邮件系统管理报告的**统一容器**。具体的报告内容格式由各自的规范定义——投递状态通知由 RFC 3464 定义，反馈报告由 RFC 5965 定义，报文处置通知由 RFC 8098 定义——而容器结构由 RFC 6522 统一规定。

理解这个分层很重要：**解析报告时先按 RFC 6522 拆容器，再按 report-type 决定用哪份规范去解析机器可读的那一段。**把两层混在一起写解析器，是这类实现最常见的结构性问题。

**容器结构：两段或三段**

RFC 6522 §3 规定 multipart/report 的**必需参数为 boundary 与 report-type**。其中 **report-type 参数标识报告的类型，其取值为第二个 body part 的 MIME 子类型**。

容器包含**两个或三个子部分**：

* **第一部分（必需）：人类可读的说明。**供人阅读，说明发生了什么。规范指出这一段的存在是为了让不具备解读第二段能力的接收方仍能理解报告内容。
* **第二部分（必需）：机器可读的报告。**其 MIME 子类型即 report-type 参数的取值。投递状态通知为 `message/delivery-status`，反馈报告为 `message/feedback-report`，处置通知为 `message/disposition-notification`。
* **第三部分（可选）：原始报文或其信头。**用于把报告与被报告的邮件关联起来。

一个典型的退信结构如下：

```
Content-Type: multipart/report;
  report-type=delivery-status;
  boundary="----=_Part_0"

------=_Part_0
Content-Type: text/plain; charset=utf-8

（人类可读说明：投递失败的原因描述）

------=_Part_0
Content-Type: message/delivery-status

（机器可读字段：Reporting-MTA、Final-Recipient、Action、Status …）

------=_Part_0
Content-Type: message/rfc822

（原始报文，或其信头）

------=_Part_0--
```

**第三部分的两种形态与 text/rfc822-headers**

第三部分可以是完整的原始报文（`message/rfc822`），也可以只是其信头。RFC 6522 §4 为后者专门定义了 **text/rfc822-headers** 媒体类型，用于标注与承载一段邮件信头。

规范说明该类型**应当包含被报告报文的全部邮件信头字段**。它的存在解决了一个实际问题：完整回附原始报文会显著增大报告体积，在处理大附件邮件的退信时尤其明显；而只回附信头则足以完成关联与诊断，因为定位所需的 Message-ID、发件人、收件人、时间与路径信息都在信头里。

规范还提到，若报文无法被轻易地重新编码为合法的 7 位 MIME 报文，可以使用 text/rfc822-headers 这一路径。

**解析器必须同时支持这两种形态。**只处理 `message/rfc822` 而遇到 `text/rfc822-headers` 就放弃关联，是退信分析系统里很常见的缺陷——现象是「某些退信始终无法归因到原始邮件」。

**解析实现要点**

1. **先读 report-type，再选解析路径。**不要依据人类可读段的文字内容来猜测报告类型。**report-type 是权威依据**，且其值必须与第二段的实际子类型一致；若不一致，应当记录为异常而不是强行按其一处理。
2. **不要假设一定有三段。**规范明确是两段或三段。缺少第三段时，关联只能依靠第二段中的字段（如投递状态通知中的原始收件人与报文标识信息）。
3. **不要假设第一段可解析出结构化信息。**第一段是给人看的自由文本，其措辞完全由生成方决定。**从人类可读段用正则提取状态码或收件人，是退信分析系统里最脆弱的做法**，任何一方改动措辞都会让它失效。结构化信息一律从第二段取。
4. **正确处理 boundary。**multipart 的解析规则由 RFC 2046 定义。boundary 处理不当会导致段落切分错误，进而把机器可读段的内容当成正文文本。
5. **状态码按 RFC 3463 解读。**投递状态通知中的 Status 字段采用增强邮件系统状态码，其三段式结构区分了永久失败与临时失败以及具体原因类别。**按首位区分永久与临时，是决定「是否重试」与「是否清理地址」的基本依据。**
6. **对格式不合规的报告要能降级处理。**现实中存在大量不完全遵循规范的退信。解析器应当在无法按结构解析时保留原文并标记，而不是直接丢弃——**丢弃会让投递问题失去可观测性**。

**运维层面的用法**

* **把退信解析结果结构化入库。**至少记录：报告类型、最终收件人、动作、增强状态码、报告方 MTA、关联到的原始报文标识。**这六项齐备，绝大多数投递质量问题可以在一次查询内定位。**
* **区分永久与临时后再决定动作。**永久失败应触发地址清理流程，临时失败应进入重试观察。**把两者混为一谈，要么误删有效地址，要么长期向无效地址投递**，后者会直接损害发信信誉。
* **反馈报告与退信分开治理。**RFC 5965 定义的反馈报告表达的是「收件人投诉」，其处置动作（通常是立即停止向该地址发送）与退信不同。二者虽共用容器，但业务含义不可混用。
* **确保接收报告的地址真的能收信。**报告类邮件本身也是邮件。如果配置报告接收地址时把它放在了一个不接收邮件的域上，报告会被拒，问题随之失去可观测性。
* **注意处置通知的隐私含义。**RFC 8098 定义的报文处置通知会向发送方披露收件人的处置行为。是否生成、在什么条件下生成，应当由收件方策略与用户意愿决定，不应默认全开。

参考：RFC 6522《The Multipart/Report Media Type for the Reporting of Mail System Administrative Messages》§3、§4 The text/rfc822-headers Media Type，M. Kucherawy 编，2012 年 1 月，STD 73，DOI 10.17487/RFC6522，https://www.rfc-editor.org/rfc/rfc6522.html ；RFC 3464《An Extensible Message Format for Delivery Status Notifications》，K. Moore、G. Vaudreuil，2003 年 1 月，https://www.rfc-editor.org/rfc/rfc3464.html ；RFC 3461《Simple Mail Transfer Protocol (SMTP) Service Extension for Delivery Status Notifications (DSNs)》，K. Moore，2003 年 1 月，https://www.rfc-editor.org/rfc/rfc3461.html ；RFC 3463《Enhanced Mail System Status Codes》，G. Vaudreuil，2003 年 1 月，https://www.rfc-editor.org/rfc/rfc3463.html ；RFC 5965《An Extensible Format for Email Feedback Reports》，Y. Shafranovich、J. Levine、M. Kucherawy，2010 年 8 月，https://www.rfc-editor.org/rfc/rfc5965.html ；RFC 8098《Message Disposition Notification》，T. Hansen、A. Melnikov 编，2017 年 2 月，STD 85，https://www.rfc-editor.org/rfc/rfc8098.html ；RFC 2046《Multipurpose Internet Mail Extensions (MIME) Part Two: Media Types》，N. Freed、N. Borenstein，1996 年 11 月，https://www.rfc-editor.org/rfc/rfc2046.html

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/rfc6522-multipart-report-structure-parsing.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
