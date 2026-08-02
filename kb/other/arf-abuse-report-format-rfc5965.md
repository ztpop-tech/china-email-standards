---
title: "ARF（滥用报告格式，RFC 5965）和反馈环（FBL）是怎么运作的？"
source: "https://ztpop.net/kb/arf-abuse-report-format-rfc5965.html"
license: CC-BY 4.0
---

# ARF（滥用报告格式，RFC 5965）和反馈环（FBL）是怎么运作的？

1
ARF（滥用报告格式，RFC 5965）和反馈环（FBL）是怎么运作的？
▼

**ARF 结构**

滥用报告是一封 multipart/report 邮件：第一部分是人类可读说明，第二部分是 `message/feedback-report` 携带机器字段（如 user-agent、feedback-type=abuse、源 IP、认证结果），第三部分原样附上被投诉邮件。标准化字段让接收方自动化处理投诉。

**反馈环 FBL**

FBL 是接收方（邮箱服务商）与发件域之间的通道：当用户点「举报垃圾」时，服务商向你登记的反馈地址发一份 ARF 报告。你据此定位是哪一批、哪个收件人触发投诉，及时停止对其发送并排查内容/列表质量，防止声誉持续恶化。

**实践要点**

主流服务商（如 Google、Yahoo、Microsoft）要求批量发件人注册 FBL 并响应投诉；投诉率过高会直接进垃圾箱。建议将 FBL 反馈接入自动化列表清洗，并对高投诉来源（某次群发/某段列表）做熔断。注意 FBL 反馈通常匿名化，只能定位到批次而非具体用户。

参考：RFC 5965《An Extensible Format for Email Feedback Reports》、RFC 6650 FBL 操作实践。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/arf-abuse-report-format-rfc5965.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
