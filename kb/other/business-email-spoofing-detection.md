---
title: "商业邮件冒充（BEC）如何检测？"
source: "https://ztpop.net/kb/business-email-spoofing-detection.html"
license: CC-BY 4.0
---

# 商业邮件冒充（BEC）如何检测？

1
商业邮件冒充（BEC）如何检测？
▼

**BEC 的常见手法**

商业邮件冒充（Business Email Compromise，BEC）不直接投毒附件，而是伪装成高管、供应商或合作伙伴：用显示名伪装（display-name spoofing）、品牌仿冒域名，或直接攻陷真实员工账号（账户接管，ATO）后从内部发信。

真实攻击链：攻击者先侦察组织结构与付款流程，再以「紧急付款」「变更收款账户」「机密数据请发到此邮箱」为由诱导财务或 HR 操作，常避开恶意链接以降低被网关拦截的概率。

**检测指标**

* **身份异常**：发件显示名与历史一致但域名细微不同；或 SPF/DKIM/DMARC 校验失败却被放行。
* **行为偏离**：该发件人首次联系财务、首次要求变更银行信息、发送时间/语言习惯不符。
* **内容信号**：措辞制造紧迫感、要求保密、绕开正常审批、附「请扫码/请登录查看发票」。
* **账号接管迹象**：登录地突变为陌生国家、可疑转发规则被自动添加、异常的邮件规则。

**防御与响应**

* **技术**：落实 DMARC 拒绝策略；对外部来信加「外部邮件」横幅；对 VIP/财务启用基于关系的异常检测。
* **流程**：任何付款账户或收款信息变更，必须走电话等体外渠道二次确认，禁止仅靠邮件批准。
* **人员**：针对财务、高管助理开展专项演练，建立「可疑即停」文化。

参考：FBI IC3《BEC 警示》年度报告、CISA BEC 防御建议、MITRE ATT&CK T1566.002（Phishing: Spearphishing Link）。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/business-email-spoofing-detection.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
