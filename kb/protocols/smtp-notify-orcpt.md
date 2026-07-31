---
title: "SMTP 的 NOTIFY 与 ORCPT 参数（RFC 3461）如何精细控制退信与原始收件人追踪？"
source: "https://ztpop.net/kb/smtp-notify-orcpt.html"
license: CC-BY 4.0
---

# SMTP 的 NOTIFY 与 ORCPT 参数（RFC 3461）如何精细控制退信与原始收件人追踪？

1
SMTP 的 NOTIFY 与 ORCPT 参数（RFC 3461）如何精细控制退信与原始收件人追踪？
▼

**NOTIFY**

MAIL FROM 的 NOTIFY 参数控制“何时发 DSN”：NOTIFY=SUCCESS（成功才通知）、FAILURE（失败才通知）、DELAY（延迟才通知）、NEVER（绝不通知）。默认通常 FAILURE,DELAY；批量发信用 NEVER 可减少退回噪声。

**ORCPT**

Original-Recipient，记录“原始信封收件人”，即便经别名/转发改写后仍保留原地址，便于 DSN 回执对应到正确用户（RFC 3461 §4.3）。

**RET**

RET=HDRS/FULL 控制退信里附带原始信的“头”还是“全信”，影响退信体积与取证信息量。

**实践**

大批量/通知类发信用 NOTIFY=NEVER 或 FAILURE 减噪；网关与归档系统用 ORCPT 保证溯源准确；需在 MTA 配置或发信库显式设置。

参考：RFC 3461（SMTP DSN，NOTIFY/ORCPT/RET）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/smtp-notify-orcpt.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
