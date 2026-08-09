---
title: "DMARC 报告怎么接入 SOC？告警规则应该怎么设计？"
source: "https://ztpop.net/kb/gw-dmarc-reports-to-soc.html"
license: CC-BY 4.0
---

# DMARC 报告怎么接入 SOC？告警规则应该怎么设计？

**两类报告的用途完全不同**

RFC 7489 第 7 节定义了两类反馈：聚合报告（rua）是周期性的统计 XML，按源 IP 汇总消息量与 SPF/DKIM/DMARC 结果，用于看趋势与发现未知发送源；失败报告（ruf）是单封邮件级别的样本，用于定位具体一封邮件为什么失败。

SOC 接入应以聚合报告为主线做持续监控，失败报告只在排障期按需开启——后者包含收件人等敏感信息，长期全量收取会带来隐私与合规负担。

**采集与解析**

在 DMARC 记录中用 `rua=mailto:` 指向专用收件地址（建议独立邮箱，避免与人工邮箱混用）。报告以 zip 或 gzip 附件形式送达，需解压后解析 XML。

入库时至少保留这些维度：报告方组织、报告时间窗、发送源 IP、header From 域、SPF 结果与对齐、DKIM 结果与对齐、DMARC 处置动作、消息计数。跨报告方的时间窗不一致，入库后应按 UTC 日归一，否则趋势图会出现锯齿。

若目标域不在你控制的组织域下，RFC 7489 第 7.1 节要求接收报告的域必须发布 `_report._dmarc` 授权记录，否则报告方会拒发。跨组织托管报告地址时这一步经常被漏配，表现为「配了 rua 但收不到报告」。

**先建基线，再设告警**

刚接入时不要立刻配告警——前两到四周用于枚举全部合法发送源（含营销平台、工单系统、监控系统、分支机构出口）并逐一登记。把这些登记为已知源，剩下的才是告警对象。

跳过基线期直接告警，SOC 会被自家未登记的系统淹没，最终把规则关掉。

**四条值得配的告警规则**

一，出现未登记源且其消息量超过阈值、DMARC 结果为 fail —— 可能是域名被冒用，也可能是新上线的业务系统未报备，需人工定性。

二，已登记源的通过率骤降 —— 通常是密钥轮换、SPF 记录超出查询次数上限、或第三方平台变更出口，属于自身配置故障。

三，整体 fail 量在短时间内跃升 —— 结合源分布判断是集中式冒用还是全局配置问题。

四，策略推进过程中的回归 —— 从 none 走向 quarantine/reject 的每一步之后，观察被处置量是否包含已登记源；有则立即回退。CISA BOD 18-01 对联邦机构提出了推进 DMARC 至 reject 的要求，但推进节奏同样依赖报告驱动的验证。

**顺带把 TLS 报告一起接**

RFC 8460 定义的 TLS-RPT 与 DMARC 报告的接入方式相似（DNS 中 `_smtp._tls` 记录声明 rua），报告内容是传输层的握手与策略校验失败统计。两类报告合并到同一条采集管线，可以同时覆盖「身份被冒用」与「传输被降级」两个面，边际成本很低。

参考：[RFC 7489 Domain-based Message Authentication, Reporting, and Conformance (DMARC)](https://www.rfc-editor.org/rfc/rfc7489.html) ｜ [RFC 8460 SMTP TLS Reporting](https://www.rfc-editor.org/rfc/rfc8460.html) ｜ [CISA BOD 18-01 Enhance Email and Web Security](https://www.cisa.gov/news-events/directives/bod-18-01-enhance-email-and-web-security)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/gw-dmarc-reports-to-soc.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
