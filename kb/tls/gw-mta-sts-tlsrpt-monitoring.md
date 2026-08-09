---
title: "MTA-STS 上线后靠什么观测？TLS 报告里该看哪些字段？"
source: "https://ztpop.net/kb/gw-mta-sts-tlsrpt-monitoring.html"
license: CC-BY 4.0
---

# MTA-STS 上线后靠什么观测？TLS 报告里该看哪些字段？

**先用 testing 模式把观测通道建起来**

RFC 8461 定义了策略的三种模式：`none`、`testing`、`enforce`。testing 模式下发送方会执行校验但不因失败而中断投递，只把失败通过 TLS-RPT 报回。这正是上线的第一步——先拿到数据，再谈强制。

顺序上，TLS-RPT 应当先于 MTA-STS 策略发布：在 `_smtp._tls.<域名>` 发布 `v=TLSRPTv1; rua=mailto:...`，确认能收到报告后，再发布 testing 策略。反过来做会导致 testing 期没有任何数据。

**报告里真正要看的字段**

RFC 8460 的报告是 JSON，按策略与接收方分组。核心是 `policies[].summary` 中的 `total-successful-session-count` 与 `total-failure-session-count`，以及 `failure-details[]` 里的 `result-type`。

常见 result-type 的定性：`starttls-not-supported` 表示对方 MX 未提供 STARTTLS（通常是某台备用 MX 配置遗漏）；`certificate-expired`、`certificate-not-trusted`、`certificate-host-mismatch` 指向证书本身；`validation-failure` 是校验阶段的其他失败；`sts-policy-fetch-error` 与 `sts-policy-invalid` 表示对方取不到或解析不了你的策略文件，属于你这一侧的问题。

配合 `failure-details[].receiving-mx-hostname` 与 `sending-mta-ip` 就能把失败精确定位到具体主机。

**推进到 enforce 的判据**

不要按时间推进，按数据推进。需要同时满足：其一，testing 期覆盖一个完整业务周期且报告来自多个主要报告方；其二，failure 计数在最近连续若干个报告周期内为零或仅剩已定性的可忽略项；其三，策略中列出的每一台 MX 主机都在成功记录中出现过——只被少数发送方触及的备用 MX 最容易漏配证书，等到主 MX 故障切换时才暴露。

第三条尤其重要：MTA-STS 校验的是策略中声明的 mx 模式与实际连接主机的证书，任何一台备用 MX 的证书主体名不匹配，都会在切换时造成全面投递失败。

**max\_age 决定了回滚有多慢**

策略按 `max_age` 被发送方缓存。设得过长（例如数周）时，一旦发布了错误策略，即使立刻修正，已缓存旧策略的发送方仍会按旧策略执行到缓存过期为止。

务实做法：初次上线与每次涉及 MX 或证书变更的时期，把 max\_age 设短（数天量级），稳定运行后再逐步延长。同时必须同步更新 DNS 中 `_mta-sts` 的 `id` 值——发送方靠 id 变化判断需要重新拉取策略，只改策略文件不改 id 等于没改。

**与证书轮换的联动**

证书轮换是 MTA-STS 环境下最高风险的常规操作。流程应固定为：确认新证书主体名覆盖策略中全部 mx 主机名 → 在低峰期分批更换 → 更换后立即检查 TLS 报告是否出现 certificate 类失败 → 全部正常后再更换下一批。

监控上建议对两个信号设告警：TLS 报告中 failure 计数环比跃升，以及策略文件 HTTPS 站点自身的可用性与证书有效期。策略站点的证书过期同样会导致发送方取不到策略，这一点常被遗漏。NIST SP 800-177 Rev.1 也把传输加密的持续验证列为邮件安全的组成部分，而非一次性配置。

参考：[RFC 8461 SMTP MTA Strict Transport Security (MTA-STS)](https://www.rfc-editor.org/rfc/rfc8461.html) ｜ [RFC 8460 SMTP TLS Reporting](https://www.rfc-editor.org/rfc/rfc8460.html) ｜ [NIST SP 800-177 Rev. 1 Trustworthy Email](https://csrc.nist.gov/pubs/sp/800/177/r1/final)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/gw-mta-sts-tlsrpt-monitoring.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
