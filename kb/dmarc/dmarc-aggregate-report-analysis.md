---
title: "如何分析 DMARC 聚合报告（RUA）？"
source: "https://ztpop.net/kb/dmarc-aggregate-report-analysis.html"
license: CC-BY 4.0
---

# 如何分析 DMARC 聚合报告（RUA）？

1
如何分析 DMARC 聚合报告（RUA）？
▼

**报告结构与获取**

接收方按 DMARC 的 RUA 地址周期（通常每日）发送 XML 报告。

* 根元素 `<feedback>` 含 `<report_metadata>`（谁发的、起止时间）与 `<policy_published>`（你的策略）。
* 每条 `<record>` 描述一个源 IP 的汇总：`<source_ip>`、`<count>`、`<policy_evaluated>`（dkim/sp 通过与否、处置）。
* 报告常经压缩（.zip/.gz）投递，需先解压再解析；建议落库后批量分析。

**关键指标解读**

聚焦对齐结果，而非单看 DKIM/SPF 自身是否签名。

* `policy_evaluated dkim=pass spf=pass` 表示该流量与 From 域对齐通过——合法。
* `dkim=fail spf=fail` 且你的策略为 reject 时，应已被接收方拒收。
* 若某源 IP 量大但通过率低，且非你已知发送平台，即为未授权发送源（可能是伪造或遗漏的合法网关）。

**实战分析流程**

用脚本或平台把多份报告聚合成可行动视图。

* 按 `source_ip` 聚合 count，按域名/选择器（若有）识别归属平台。
* 对照已知发信基础设施白名单：云邮件、营销平台、事务邮件服务的 IP 段。
* 对未对齐的大流量源：若是自己的遗漏源，补 SPF include / 补 DKIM 选择器；若是外部伪造，确认 reject 已生效。

**策略校准**

用数据驱动地把策略从监测推向强制。

* `p=none` 阶段确认所有合法源对齐通过后，再升 `p=quarantine`。
* quarantine 阶段观察误判率，无误伤再升 `p=reject`。
* 对子域用 `sp=` 独立设置，必要时先用 `pct=` 灰度生效比例。

参考：RFC 7489（DMARC）附录报告 schema、RFC 6591 反馈报告。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/dmarc-aggregate-report-analysis.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
