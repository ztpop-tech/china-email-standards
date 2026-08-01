---
title: "什么是“回调钓鱼（Callback Phishing）”？为何难防、如何处置？"
source: "https://ztpop.net/kb/callback-phishing-defense.html"
license: CC-BY 4.0
---

# 什么是“回调钓鱼（Callback Phishing）”？为何难防、如何处置？

1
什么是“回调钓鱼（Callback Phishing）”？为何难防、如何处置？
▼

**机理**

钓鱼信不含恶意链接或附件，只留“客服电话/二维码”，诱骗受害者主动回拨；人工坐席（攻击者）再以“远程协助/订阅取消”为由骗取凭据或诱导安装远控软件。

**难防点**

无 URL、无附件，传统网关（URL 沙箱、附件扫描）几乎命中不了；攻击在电话里靠社会工程完成，绕开技术防线。

**检测**

警惕“无链接无附件却催你打电话”的可疑信；对“订阅/扣费/账号异常”类话术提高警觉；核对所谓“官方电话”是否在官网公布。

**处置**

绝不使用信中给的电话或二维码；经官方渠道核实；企业公布统一客服入口并培训员工“只走官方入口”；配合 DMARC 降低冒名信量。

参考：FBI IC3 商业邮件诈骗报告；CISA 钓鱼防范；Microsoft 安全博客（callback phishing）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/callback-phishing-defense.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
