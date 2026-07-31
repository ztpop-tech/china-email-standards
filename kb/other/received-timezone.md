---
title: "邮件头里的 Received 时间戳与时区（RFC 5321 §4.4）如何解读？为何能还原传输路径？"
source: "https://ztpop.net/kb/received-timezone.html"
license: CC-BY 4.0
---

# 邮件头里的 Received 时间戳与时区（RFC 5321 §4.4）如何解读？为何能还原传输路径？

1
邮件头里的 Received 时间戳与时区（RFC 5321 §4.4）如何解读？为何能还原传输路径？
▼

**格式**

每个 Received 头形如：Received: from A (host.a) by B (host.b) with ESMTPS id xxx; Wed, 31 Jul 2026 09:12:33 +0000 (UTC)。末尾是“事件发生的本地时间 + 时区偏移”。

**时区意义**

末尾 (UTC)/+0800 标明该跳发生地的时区；跨时区的多跳链路里，凭偏移可判断各跳所在地理时区，辅助反推路径与延迟。

**倒序**

Received 头是“倒着加”的——最上面的是最后经手的服务器（收件方最近一跳），最下面是最早的发送方；顺时间读要从下往上。

**运维**

时间跳跃过大（如负数间隔、未来时间）可能暗示伪造或时钟不同步；结合 Received 链可定位邮件在哪一跳被延迟或篡改。

参考：RFC 5321 §4.4（Received 头格式与语义）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/received-timezone.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
