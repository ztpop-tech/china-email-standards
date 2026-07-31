---
title: "如何检测自己的邮件服务器是否“开放中继”？被当开放中继有何后果？"
source: "https://ztpop.net/kb/email-open-relay-test.html"
license: CC-BY 4.0
---

# 如何检测自己的邮件服务器是否“开放中继”？被当开放中继有何后果？

1
如何检测自己的邮件服务器是否“开放中继”？被当开放中继有何后果？
▼

**检测**

从外部（非内网）用 telnet/swaks 连 25，尝试向“本服务器不负责的外部域”发信（MAIL FROM 外部、RCPT 外部）；若接受并投递，即开放中继。也可用在线 open-relay 测试服务。

**后果**

开放中继会被垃圾发送者疯狂利用，你的 IP 迅速进 RBL/黑名单，所有正常邮件被全球拒收；信誉崩塌恢复极慢。

**防护**

relay 仅限 mynetworks/已认证用户；未知来源一律“本地域才收、外部域要认证”；用 postscreen/限制减少暴露；上线前必测。

**实践**

“对话内拒收 + 严格中继判定”是底线；定期用外部探测复核，配合 RBL 自监控，确保未因配置变更重新开放。

参考：RFC 5321（中继模型）；开放中继检测实践 / Spamhaus 开放中继判定

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-open-relay-test.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
