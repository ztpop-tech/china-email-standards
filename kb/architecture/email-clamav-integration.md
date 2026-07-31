---
title: "ClamAV 如何为邮件“扫描病毒/恶意附件”？它与邮件系统怎么集成？"
source: "https://ztpop.net/kb/email-clamav-integration.html"
license: CC-BY 4.0
---

# ClamAV 如何为邮件“扫描病毒/恶意附件”？它与邮件系统怎么集成？

1
ClamAV 如何为邮件“扫描病毒/恶意附件”？它与邮件系统怎么集成？
▼

**引擎**

ClamAV 是开源反病毒引擎，用特征库（CVD）识别病毒/木马/宏恶意文档；clamd 守护进程提供扫描服务，避免每信起进程。

**集成**

邮件侧常用 ① clamav-milter 挂 MTA 直接扫；② 经 amavis 调用 clamd；③ 网关 appliance 内置。扫到恶意附件可“删除/隔离/标记”并通知。

**库更新**

freshclam 定时拉最新病毒库；库新鲜度直接决定检出率，离线/老旧库会漏。

**实践**

邮件网关务必对附件做病毒扫描（尤其 Office/PDF/压缩包）；扫描失败应“fail-safe 拒或隔离”而非放行；注意大附件扫描的超时与资源。

参考：ClamAV 文档（clamd / clamav-milter / freshclam）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-clamav-integration.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
