---
title: "如何识别伪造的 Received 头（邮件溯源造假）？"
source: "https://ztpop.net/kb/received-forgery.html"
license: CC-BY 4.0
---

# 如何识别伪造的 Received 头（邮件溯源造假）？

1
如何识别伪造的 Received 头（邮件溯源造假）？
▼

**原理**

Received 头由“经手服务器”自己添加，发送方无法伪造“收件方服务器”添加的 Received（除非攻破该服务器）；但发送方可在自己发出的信里预先塞入伪造 Received 头，企图误导溯源。

**识别**

① 最顶（收件方最近一跳）必为真实（由你的服务器写）；② 伪造的往往是“下方靠近发送方的额外 Received”，其 by/from 主机与真实路径不符、时间顺序错乱、时区矛盾；③ 比对信封 Received 与信头 Received 是否一致。

**工具**

用邮件客户端“查看原始信头（View Source）”，从下往上逐跳核对主机名、IP、时间连续性；异常跳的时间倒流或公网不可达 IP 是强信号。

**价值**

溯源与取证（钓鱼/欺诈调查）的核心技能；配合 Authentication-Results（SPF/DKIM/DMARC）一起看，伪造 Received 往往与认证失败并存。

参考：RFC 5321 §4.4（Received 头）；与SPF/DKIM/DMARC 联合取证

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/received-forgery.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
