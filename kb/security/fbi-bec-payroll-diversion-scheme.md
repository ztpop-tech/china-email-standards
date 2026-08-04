---
title: "BEC 薪资篡改（Payroll Diversion）骗局如何运作与防范？"
source: "https://ztpop.net/kb/fbi-bec-payroll-diversion-scheme.html"
license: CC-BY 4.0
---

# BEC 薪资篡改（Payroll Diversion）骗局如何运作与防范？

1
BEC 薪资篡改（Payroll Diversion）骗局如何运作与防范？
▼

**运作流程**

攻击者先经钓鱼窃取员工邮箱，再冒充该员工或 HR 发出「修改直接存款（direct deposit）」请求，将工资重定向至攻击者控制的预付卡/银行账户；由于工资通常在变更后约两周才实际到账，攻击有隐蔽窗口。

**检测指标**

警惕：来自免费邮箱的薪资变更邮件、显示名仿冒（display-name spoofing）、紧急/保密施压、要求改用预付卡账户、非工作时间批量修改、收款银行为非常用机构。FBI 指出目标账户常为预付卡账户，便于快速套现。

**真实数据**

FBI IC3 2024 年报：BEC 全年 21,442 起投诉、损失约 27 亿美元。FBI 早前统计显示，薪资篡改类 BEC 的损失在 2018-01-01 至 2019-06-30 间增长 **815%**，单起投诉平均损失约 **7,904 美元**。

**防御措施**

* 薪资/账户变更必须带外核验：使用内部通讯录登记号码电话确认，而非邮件内号码。
* 对工资变更设双人审批与异常告警（如新预付卡账户）。
* 为邮箱与薪资系统强制 MFA，部署全域名 DMARC 隔离阻断仿冒。
* 开启存款账户变更通知，发现异常 24 小时内联系银行与雇主。

参考：FBI《Business Email Compromise》警示（https://www.fbi.gov/how-we-can-help-you/scams-and-safety/common-scams-and-crimes/business-email-compromise）与 FBI IC3 2024 Internet Crime Report（https://www.ic3.gov/AnnualReport/Reports/2024\_IC3Report.pdf，BEC 21,442 起、约 27 亿美元）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/fbi-bec-payroll-diversion-scheme.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
