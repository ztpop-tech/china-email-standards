---
title: "Google Workspace 入站网关（Inbound Gateway）如何配置才能正确处理 SPF？"
source: "https://ztpop.net/kb/google-workspace-inbound-gateway-spf-handling.html"
license: CC-BY 4.0
---

# Google Workspace 入站网关（Inbound Gateway）如何配置才能正确处理 SPF？

1
Google Workspace 入站网关（Inbound Gateway）如何配置才能正确处理 SPF？
▼

**问题背景**

当邮件先经自有旧服务器或第三方网关再到 Gmail 时，Gmail 默认会对"连接来源 IP"做 SPF 校验，而那通常是你自己的网关而非真实发送方，导致 SPF 误判。Google 提供"入站网关"设置把这类跳板主机声明为可信中继。

**配置位置**

在 Admin console 的 Apps › Google Workspace › Gmail › Routing（或 Compliance）中配置 Inbound gateway，把"识别入站网关的方式"指向这些服务器的 IP 或主机名——可基于连接 IP，也可基于邮件头中的 X-Originating-IP / Received 头。

**效果与注意**

启用后，Gmail 会把 SPF 校验"前移"到原始发送方（即网关所声明的真实来源），按真实来源评估 SPF，显著提升准确性。但声明为入站网关的服务器发来的邮件会被当作"内部消息"处理，须谨慎只把可信基础设施列入，避免被滥用。

参考：Google Workspace Help · support.google.com/a/answer/60730

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/google-workspace-inbound-gateway-spf-handling.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
