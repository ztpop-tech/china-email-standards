---
title: "如何用 Received 链做“高级邮件取证”？怎样还原完整传输路径并识别篡改？"
source: "https://ztpop.net/kb/received-highlevel-forensics.html"
license: CC-BY 4.0
---

# 如何用 Received 链做“高级邮件取证”？怎样还原完整传输路径并识别篡改？

1
如何用 Received 链做“高级邮件取证”？怎样还原完整传输路径并识别篡改？
▼

**还原路径**

从下（最早发送方）往上（收件方）逐跳读 Received 头，每跳含 from/by/with/ID/时间；按时间戳差算每跳延迟，按主机名/IP 确认经手方，拼出完整路由图。

**识别伪造**

① 收件方最近一跳（最顶）必真；② 比对“信封 Received”（MAIL FROM 会话日志）与“信头 Received”——发送方可在信头塞伪造 Received，但无法伪造信封层；③ 异常跳：时间倒流、时区矛盾、公网不可达 IP、重复主机→高概率伪造。

**关联认证**

将 Received 链与 Authentication-Results（SPF/DKIM/DMARC）结合——伪造 Received 常伴随认证失败；DKIM 通过的信说明签名后信头未被改，可佐证 Received 真实性。

**工具链**

用 received-parser / 取证工具或自写脚本解析；取证报告需固化原始信头（含所有 Received）作为证据。

参考：RFC 5321 §4.4（Received 头）；与 RFC 8601 / DKIM 联合取证

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/received-highlevel-forensics.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
