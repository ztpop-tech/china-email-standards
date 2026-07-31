---
title: "什么是“反馈回路（FBL，Feedback Loop）”？它如何帮发件人发现“被投诉的垃圾”？"
source: "https://ztpop.net/kb/email-feedback-loop-fbl.html"
license: CC-BY 4.0
---

# 什么是“反馈回路（FBL，Feedback Loop）”？它如何帮发件人发现“被投诉的垃圾”？

1
什么是“反馈回路（FBL，Feedback Loop）”？它如何帮发件人发现“被投诉的垃圾”？
▼

**定义**

FBL 是接收方/邮箱服务商把“用户标记垃圾”的邮件样本回传给发件人（或他的 ESP）的机制，让发件人知道“哪批信被投诉了”。

**格式**

回传通常用 ARF（RFC 5965 滥用报告格式）：包含原始信头与投诉元数据；大厂（如 Yahoo/Microsoft）提供 FBL 供可信发件人订阅。

**价值**

发件人据投诉率（complaint rate）及时关停滥用账号、清理列表、优化内容；投诉率过高会严重损害 IP/域信誉，乃至被拦。

**实践**

批量发信须订阅目标服务商的 FBL、监控投诉率并设阈值告警；结合 List-Unsubscribe（RFC 8058）降低误投诉，合规退订优于“被标记垃圾”。

参考：RFC 5965（ARF 滥用报告格式，FBL 载体）；RFC 8058（一键退订）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-feedback-loop-fbl.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
