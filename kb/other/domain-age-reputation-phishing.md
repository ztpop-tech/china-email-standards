---
title: "域名年龄与信誉如何用于钓鱼邮件判定？"
source: "https://ztpop.net/kb/domain-age-reputation-phishing.html"
license: CC-BY 4.0
---

# 域名年龄与信誉如何用于钓鱼邮件判定？

1
域名年龄与信誉如何用于钓鱼邮件判定？
▼

**域名年龄作为强信号**

统计上**新注册域名（aged < 30 天）**用于钓鱼的比例远高于老域名。将「注册天数」纳入风险评分：刚注册即大量发信、且主题涉账号验证/账单的域名应显著加权。WHOIS 注册时间、注册局是判断年龄的权威来源。

**信誉与黑名单**

结合 **信誉服务与黑名单**：Spamhaus、SpamCop、URIBL、abuse.ch 等提供的域名/URL 信誉；命中即高危。同时查询 Passive DNS 看该域名历史解析是否密集指向已知恶意 IP，以及是否有大量「兄弟域名」批量注册特征。

**证书透明度与关联分析**

通过 CT 日志发现某攻击者**批量申请仿冒证书**的关联域名群，结合注册时间聚类识别活动集群。对使用 Let's Encrypt 等免费证书、且 SAN 中塞入多个品牌词的域名提高警觉。

**评分落地建议**

在邮件网关中构建评分：新域名（0–30 天）加分、黑名单命中大幅加分、与品牌域编辑距离近加分。对**总分超阈值**的邮件隔离并人工复核，避免直接拦截误伤正常新业务域名；对临界值做附加验证（如回调验证发件域）。

参考：Spamhaus 与 URIBL 信誉列表、abuse.ch 威胁情报、证书透明度日志（RFC 9162）、APWG 钓鱼趋势报告（新域滥用数据）、以及 Passive DNS 服务（如 SecurityTrails/Farsight）实践。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/domain-age-reputation-phishing.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
