---
title: "什么是“连接器高级过滤”（advanced filtering for connectors）？"
source: "https://ztpop.net/kb/microsoft-faq-04.html"
license: CC-BY 4.0
---

# 什么是“连接器高级过滤”（advanced filtering for connectors）？

1
什么是“连接器高级过滤”（advanced filtering for connectors）？
▼

**说明**

当邮件经由本地连接器（如混合部署 Exchange）进入 Exchange Online 时，原始发件人 IP 与认证结果可能被覆盖，导致 EOP 基于“看起来是内部”的来源误判。开启“连接器高级过滤”可保留来自本地 Edge/网关的**原始连接信息**——包括真实客户端 IP、以及原始的 SPF/DKIM/DMARC 结果——让 Exchange Online Protection 基于真实来源做判定，避免把本应拦截的邮件误放进来，也避免把合法邮件误拦。

**适用场景**

混合部署、第三方邮件安全网关、或任何“邮件先到本地/网关再到 Exchange Online”的架构都应开启此选项。

参考：Microsoft Learn《Email authentication and anti-spoofing》· learn.microsoft.com/exchange/email-authentication-anti-spoofing

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/microsoft-faq-04.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
