---
title: "Microsoft 365 的“增强过滤（Enhanced Filtering for Connectors）”与跳列（skip listing）有何用？"
source: "https://ztpop.net/kb/m365-enhanced-filtering-connectors-skiplisting.html"
license: CC-BY 4.0
---

# Microsoft 365 的“增强过滤（Enhanced Filtering for Connectors）”与跳列（skip listing）有何用？

1
Microsoft 365 的“增强过滤（Enhanced Filtering for Connectors）”与跳列（skip listing）有何用？
▼

**为何需要**

当邮件先经本地网关/第三方过滤再到 EOP（Exchange Online Protection）时，EOP 看到的是网关 IP 而非真实发送方 IP，导致 SPF/DKIM/DMARC 与威胁情报基于错误来源，过滤与策略失真。

**增强过滤**

在连接器（connector）上启用 Enhanced Filtering for Connectors，告诉 EOP 穿越（traverse）列出的跳板，从 Received 头链中还原真实发送方 IP、域与信任链，使过滤与策略基于真实来源生效。

**跳列 / IP 异常**

通过"IP 异常（skip listing）"把已知可信的中继（如你的网关、CTP 设备）加入跳过列表，避免它们被误判。但需仅列入确实受控的中继，否则会放大伪造风险。

**注意**

启用后应在威胁资源管理器中验证真实来源识别是否正确，避免把不可信来源误判为内部，导致绕过过滤。

参考：Microsoft Learn · Enhanced Filtering for Connectors（IP 异常 / skip listing）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/m365-enhanced-filtering-connectors-skiplisting.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
