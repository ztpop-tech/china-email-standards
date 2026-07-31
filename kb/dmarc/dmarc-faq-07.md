---
title: "能否在不影响现有邮件流的情况下逐步部署 DMARC？"
source: "https://ztpop.net/kb/dmarc-faq-07.html"
license: CC-BY 4.0
---

# 能否在不影响现有邮件流的情况下逐步部署 DMARC？

1
能否在不影响现有邮件流的情况下逐步部署 DMARC？
▼

**说明**

完全可以。事实上，支持渐进式部署与逐步加强策略正是该规范的核心设计目标。你可以从子域或主域的一条"监控模式"记录开始，仅请求接收方回送统计，即使尚未部署 SPF/DKIM 也能做；随着引入 SPF/DKIM，报告会显示通过/未通过这些检查的邮件数量与来源。

**建议**

当确认绝大部分合法流量已被 SPF/DKIM 覆盖，先实施 quarantine（放入垃圾箱），并可只对部分流量（pct）应用；排查无误后逐步将 pct 提升到 100%。最后再升级到 reject（直接拒绝），同样可先用小比例试水。若从子域开始，可再到其他子域，最终覆盖顶级域。

参考：DMARC.org FAQ · RFC 7489 §7.1（pct 回退）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/dmarc-faq-07.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
