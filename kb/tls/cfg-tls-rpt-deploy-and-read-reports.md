---
title: "TLS-RPT 要怎么配置？收到的 JSON 报告里哪些字段能定位问题？"
source: "https://ztpop.net/kb/cfg-tls-rpt-deploy-and-read-reports.html"
license: CC-BY 4.0
---

# TLS-RPT 要怎么配置？收到的 JSON 报告里哪些字段能定位问题？

**TLS-RPT 的定位**

RFC 8460 定义的 SMTP TLS Reporting 是 MTA-STS 与 DANE 的配套观测机制。MTA-STS 负责声明策略，TLS-RPT 负责让收件域知道「别人按这个策略投递时到底成功了没有」。没有 TLS-RPT，testing 模式基本失去意义——因为你既不拦截、也看不到失败。

**配置 DNS TXT 记录**

在 `_smtp._tls.<域名>` 发布 TXT 记录，格式为 `v=TLSRPTv1; rua=mailto:tls-report@example.com`。rua 也可以是 HTTPS 端点（`rua=https://…`），多个地址用逗号分隔。注意接收报告的邮箱本身要能收大附件，聚合报告通常是压缩后的 JSON。

**报告的粒度与周期**

报告是按天聚合的，覆盖一个 date-range（含 start-datetime 与 end-datetime）。顶层字段包括 organization-name（发送报告方）、contact-info、report-id，以及一个 policies 数组——每个元素对应一条被应用的策略。

**policies 数组：先看 policy-type**

policy-type 取值说明了对方投递时依据的是哪套策略：`sts` 表示走的 MTA-STS 策略，`tlsa` 表示走的 DANE，`no-policy-found` 表示没找到任何策略。如果你已经发布了 MTA-STS 但报告里大量出现 no-policy-found，那说明策略没被正确取到——优先排查 TXT 记录拼写、mta-sts 子域的 HTTPS 证书、以及策略文件路径是否可匿名访问。

**summary 与 failure-details：定位具体故障**

summary 给出 total-successful-session-count 与 total-failure-session-count 两个计数，用于看整体成功率趋势。真正用于定位的是 failure-details，其中 result-type 指明失败原因，常见的有证书相关（如证书过期、名字不匹配、证书链不可信）、STARTTLS 协商失败、以及策略获取或校验失败等类别。配合 sending-mta-ip、receiving-mx-hostname 与 failed-session-count，可以把问题收敛到具体是哪一台 MX、被哪一批发送方看到失败。

**典型排查路径**

先按 receiving-mx-hostname 分组：若失败集中在单台 MX，多半是该节点证书或 TLS 配置问题；若所有 MX 均失败且集中在同一时间段，优先怀疑证书轮换或策略文件变更；若失败分散在少数 sending-mta-ip，则更可能是对端实现或中间网络设备的问题，此时贸然切 enforce 会把这部分邮件全部拒之门外。

参考：[RFC 8460 SMTP TLS Reporting](https://www.rfc-editor.org/rfc/rfc8460.html) ｜ [RFC 8461 SMTP MTA Strict Transport Security](https://www.rfc-editor.org/rfc/rfc8461.html)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/cfg-tls-rpt-deploy-and-read-reports.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
