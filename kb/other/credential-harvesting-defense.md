---
title: "凭据窃取（Credential Harvesting）邮件如何防御？"
source: "https://ztpop.net/kb/credential-harvesting-defense.html"
license: CC-BY 4.0
---

# 凭据窃取（Credential Harvesting）邮件如何防御？

1
凭据窃取（Credential Harvesting）邮件如何防御？
▼

**凭据窃取如何发生**

凭据窃取（Credential Harvesting）邮件诱导受害者点击链接，进入与正品高度相似的伪造登录页，输入账号密码后被实时回传攻击者。随后攻击者用这批凭据直接登录真实服务，常结合 MFA 疲劳攻击或会话令牌窃取绕过第二步验证。

真实攻击手法：邮件伪装成「邮箱存储空间已满」「账户异常登录」「发票待查」，登录页托管在仿冒域名或合法但被入侵的网站子路径；部分 kit 还能中继实时 MFA 推送。

**检测指标**

* **URL 特征**：域名与品牌仅差字符、使用罕见 TLD、经缩短服务隐藏。
* **页面指纹**：伪造登录页的表单 action 指向陌生后端，或复用已知 kit 模板。
* **行为信号**：同一账号短时间内多地登录、MFA 被反复触发、出现非常用设备会话。
* **举报**：用户通过「举报 phishing」按钮提交的可疑样本。

**防御措施**

* **抗钓鱼 MFA**：优先采用 FIDO2/WebAuthn 等钓鱼抗性多因子，避免可被中继的纯推送/OTP。
* **网关拦截**：URL 重写与实时信誉查询，对未知登录页沙箱预检。
* **品牌防护**：监测并下仿冒域名，DMARC 拒绝伪造发件。
* **身份加固**：条件访问绑定受管设备、异常登录即要求重新认证并吊销会话。

参考：CISA《防钓鱼与 MFA》指南、FIDO Alliance 抗钓鱼认证白皮书、MITRE ATT&CK T1566（Phishing）。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/credential-harvesting-defense.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
