---
title: "商业邮件诈骗（BEC）在 2026 年出现了哪些演进？"
source: "https://ztpop.net/kb/bec-threat-evolution-2026.html"
license: CC-BY 4.0
---

# 商业邮件诈骗（BEC）在 2026 年出现了哪些演进？

1
商业邮件诈骗（BEC）在 2026 年出现了哪些演进？
▼

**规模基线**

FBI IC3《2025 年互联网犯罪报告》记录 BEC 投诉 **24,768** 起、损失 **3,046,598,558 美元**，按损失排名仅次于投资诈骗，位居第二；折算平均单起损失约 12.3 万美元，远高于普通钓鱼。APWG 各季报中 Fortra 供稿章节则给出攻击侧口径：电汇 BEC 的**请求金额均值**在 2025 年内剧烈波动——Q1 为 `42,236` 美元（较 2024 Q4 的 128,980 美元下降 67%），Q2 反弹至 `83,099` 美元（+97%），Q3 回落至 `48,115` 美元（−42%），Q4 为 `50,297` 美元（+4.5%）。金额下降而**数量激增**是 2025 年的主线：Q1 环比 +33%、Q2 +27%、Q3 +57%、Q4 **+136%**。

**自动化「小额高频」团伙**

Fortra 把 Q3、Q4 的量增归因于一个被命名为 **Scripted Sparrow** 的团伙（首次观测于 2024 年 6 月），并在 Q4 报告中称其为当时**全球最高产的 BEC 团伙**：估计每月发出多达 **600 万封**高度定向邮件，专门瞄准应付账款（Accounts Payable）团队，投递伪造的「高管培训服务」发票，索要金额通常**刚好低于 5 万美元**——这一门槛设计明显是为规避大额付款的额外审批。成员来自南非、尼日利亚、美国与土耳其。其核心手法是**伪造回复链**（spoofed reply chain）：在邮件中嵌入看似高管与培训机构此前往来的对话历史，诱使收件人相信该支出已获高管批准。Q2 报告还记录该类邮件附带两个 PDF 附件（一份发票、一份填好的 IRS W-9 表），以强化真实感。攻击量之大表明其使用了自动化手段批量生成唯一的 PDF 附件与正文。

**提现方式与基础设施**

Fortra 对提现方式的统计显示礼品卡长期居首但份额波动：Q1 50.9%、Q2 72%、Q4 59%；Q4 电汇请求占比升至 **17%**（Q3 报告中电汇因 Scripted Sparrow 的高量攻击已从 3% 升至 5%），Interac 9%，工资转移（payroll diversion）8%，加密货币 4%。基础设施方面，Q1 数据显示 **72%** 的 BEC 攻击使用免费网页邮箱域名发起（回到 2024 Q3 水平，2024 Q4 曾低至 63%），其中 Gmail 占免费邮箱的 **73.5%**、微软系占 13.8%；剩余 28% 使用非网页邮箱域名，其注册商分布为 Cloudflare 28.6%（居首）、Squarespace 19.2%、NameCheap 17.1%。

**AI 加持与防御建议**

IC3 2025 年报单列了 AI 相关 BEC：135 起投诉、损失 `30,256,592` 美元，并说明聊天生成器可快速产出模仿 CEO 或高管口吻的「官方腔」邮件，语音克隆则用于配合电话催办电汇。Europol IOCTA 2026 与 INTERPOL 2026 评估同样指出，生成式 AI 被用于定制社工话术、让 BEC 与 CEO 欺诈更逼真。据此，防御应从「识别语言破绽」转向流程与认证：**（1）**所有付款账户新增或变更、大额电汇必须走带外核验，使用系统内已登记的联系方式而非邮件正文中的号码；**（2）**对应付账款团队设置金额阈值以下同样需要双人复核，直接对冲「刚好低于 5 万美元」的规避设计；**（3）**全域名 DMARC 强制策略并对外部来信标注横幅，对伪造回复链启用会话链一致性检测（比对 `References/In-Reply-To` 与本地会话存档是否真实存在）；**（4）**对免费网页邮箱发出的「高管指令」类邮件单列风险评分规则。

参考：FBI IC3《2025 Internet Crime Report》：[ic3.gov 原始 PDF](https://www.ic3.gov/AnnualReport/Reports/2025_IC3Report.pdf)；APWG《Phishing Activity Trends Report》2025 Q1—Q4 中 Fortra 供稿的 BEC 章节，[Q4 2025 PDF](https://docs.apwg.org/reports/apwg_trends_report_q4_2025.pdf)；Europol《IOCTA 2026》：[europol.europa.eu](https://www.europol.europa.eu/publication-events/main-reports/iocta-2026-evolving-threat-landscape)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/bec-threat-evolution-2026.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
