---
title: "都说要上 MFA，但短信验证码、普通推送也能被钓鱼绕过，到底哪种 MFA 真抗钓鱼？"
source: "https://ztpop.net/kb/phishing-resistant-mfa-deployment.html"
license: CC-BY 4.0
---

# 都说要上 MFA，但短信验证码、普通推送也能被钓鱼绕过，到底哪种 MFA 真抗钓鱼？

1
都说要上 MFA，但短信验证码、普通推送也能被钓鱼绕过，到底哪种 MFA 真抗钓鱼？
▼

**不是所有 MFA 都等价**

CISA《Implementing Phishing-Resistant MFA》开宗明义：并非所有形式的 MFA 都同样安全；有些易受钓鱼、「推送轰炸（push bombing，也称 push fatigue）」、中间人（MITM）攻击，攻陷后威胁行为者可能获取 MFA 认证凭据或绕过 MFA 访问受保护系统。CISA 强烈敦促各组织把抗钓鱼 MFA 作为践行零信任（Zero Trust）原则的一部分来实施。

**由强到弱：表 1**

CISA 表 1（MFA Forms, Strongest to Weakest）自上而下：①**抗钓鱼 MFA（FIDO/WebAuthn 认证、基于 PKI 的 MFA）**——金标准，抗钓鱼；推送轰炸、SS7、SIM swap 对其均不适用。②**应用认证（OTP、带 number matching 的推送、基于令牌 OTP）**——抗钓鱼性弱于前者，但优于短信；number matching 可抗推送轰炸，是中小组织暂不能上抗钓鱼 MFA 时的最佳选项。③**不带 number matching 的纯推送**——易受推送轰炸与用户误点。④**SMS/语音**——仅作最后手段，易受钓鱼、SS7、SIM swap。

**为什么 FIDO/WebAuthn 抗钓鱼**

CISA 说明：目前唯一广泛可用的抗钓鱼认证是 FIDO/WebAuthn——由 FIDO 联盟最初作为 FIDO2 标准的一部分开发，现由 W3C 发布；主流浏览器、操作系统与手机均内置支持。WebAuthn 认证器可以是独立的物理令牌（roaming，经 USB/NFC 连接），也可嵌入笔记本或手机作为平台（platform）认证器；除「你拥有的东西」外还可结合生物识别或 PIN。基于 PKI 的 MFA 是另一种可用性较低的抗钓鱼形式，绑定企业 PKI。

**迁移建议**

CISA 建议：识别不支持 MFA 的系统并制定升级或迁移计划（常可通过企业身份与单点登录 SSO 集成补上 MFA）；对暂时无法上抗钓鱼 MFA 的既有系统，采用 number matching 等额外预防与检测控制；把不支持 MFA 系统的风险上报组织高层。OMB 已要求美国联邦机构采用抗钓鱼 MFA 方法。

参考：https://www.cisa.gov/sites/default/files/2023-09/Implementing-Phishing-Resistant-MFA-508.pdf

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/phishing-resistant-mfa-deployment.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
