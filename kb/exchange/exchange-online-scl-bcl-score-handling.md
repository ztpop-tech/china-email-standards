---
title: "Exchange Online / Microsoft 365 里的 SCL 与 BCL 分数分别是什么，如何据此处理邮件？"
source: "https://ztpop.net/kb/exchange-online-scl-bcl-score-handling.html"
license: CC-BY 4.0
---

# Exchange Online / Microsoft 365 里的 SCL 与 BCL 分数分别是什么，如何据此处理邮件？

1
Exchange Online / Microsoft 365 里的 SCL 与 BCL 分数分别是什么，如何据此处理邮件？
▼

**SCL 垃圾邮件置信度**

SCL（Spam Confidence Level）取值 0–9，越高越可能是垃圾邮件；-1 表示被跳过（如连接器跳列/允许列表）。可在反垃圾邮件策略的"垃圾邮件阈值"统一决定高于阈值的邮件去垃圾箱还是隔离。

**BCL 批量投诉等级**

BCL（Bulk Complaint Level）取值 1–9，衡量发信方作为"批量邮件"的投诉倾向；越高越像营销/批量邮件。常用于区分正常批量信与滥发。

**相关标头**

EOP/Defender 会在邮件注入 X-Forefront-Antispam-Report、X-Microsoft-Antispam 等标头，内含 SCL/BCL 数值与判定原因（如 SFV、PCL、蕴含的 DMARC 结果），便于排障与建规则。

**如何据此处理**

在 Exchange 邮件流规则（Transport rule）里可读取 SCL/BCL：当标头出现特定值（如 X-MS-Exchange-Organization-SCL:9）时执行"隔离""设置垃圾邮件置信度""添加 X 标头"等动作，从而把高 SCL/BCL 邮件分流处理。

参考：Microsoft Learn · 反垃圾邮件邮件标头（anti-spam message headers，EOP/MDO）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/exchange-online-scl-bcl-score-handling.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
