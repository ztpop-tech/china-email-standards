---
title: "深度伪造（Deepfake）CEO 冒充邮件如何防范？"
source: "https://ztpop.net/kb/email-impersonation-ceo-deepfake.html"
license: CC-BY 4.0
---

# 深度伪造（Deepfake）CEO 冒充邮件如何防范？

1
深度伪造（Deepfake）CEO 冒充邮件如何防范？
▼

**检测指标**

留意异常请求：邮件发件人显示名仿高管但域名细微拼写差异（typosquat）、措辞紧急且要求「保密/绕过流程」、附带合成语音留言或视频链接、收款账户为新增大额或境外账户。可结合 DMARC 失败率、发件 IP 信誉、发件显示名与通讯录匹配度做风险评分。

**防御措施**

* 建立「敏感操作必须带外核验」制度：大额付款、凭证变更须通过电话或线下当面确认，且使用已登记号码而非邮件内号码。
* 强制全域名 DMARC 隔离（p=quarantine/reject）与 SPF/DKIM 对齐，阻断伪装内部域名。
* 对财务、HR 等高价值岗位做针对化反钓鱼演练与深度伪造识别培训。

**真实攻击手法**

攻击者先入侵或观察高管公开视频与演讲素材，用开源工具合成「CEO 语音」拨打财务电话，再以高管邮箱或仿冒域名发邮件要求紧急付款。邮件常声称「在开会、勿电话」以阻止带外核验。部分案例先发钓鱼骗取秘书通讯录，再精准冒充上级。

**基准控制项**

以 CIS Controls v8 控制项 9（员工培训）、14（安全意识与技能培训）固化识别能力；RFC 7489 DMARC 提供发件人认证基线；结合 NIST SP 800-53 的 AC-2（账户管理）、SI-4（系统监控）对高价值岗位做持续监控。

参考：FBI IC3 商务邮件入侵警示、CISA 深度伪造风险指引、RFC 7489 DMARC、MITRE ATT&CK T1566.002（Spearphishing Link）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-impersonation-ceo-deepfake.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
