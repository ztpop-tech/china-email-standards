---
title: "CISA 多因素认证实施指引：抗钓鱼 MFA 与高风险账号保护"
source: "https://ztpop.net/kb/cisa-mfa-implementation-guide.html"
license: CC-BY 4.0
---

# CISA 多因素认证实施指引：抗钓鱼 MFA 与高风险账号保护

## 概述

CISA 反复强调"MFA 是性价比最高的单点安全控制"，并将其列为 Shields Up 等告警的核心动作。其实施指引进一步区分 MFA 的强弱：基于 SMS/语音的 OTP 可被 SIM 交换、拦截绕过，而基于公钥密码的 FIDO2/WebAuthn、PIV 智能卡属于**抗钓鱼（phishing-resistant）MFA**，应作为高价值系统的首选。

## MFA 类型分级

| 类型 | 示例 | 抗钓鱼 | 评价 |
| --- | --- | --- | --- |
| 知晓+持有（弱） | SMS/语音 OTP | 否 | 可被拦截，逐步淘汰 |
| 持有（中） | TOTP App（Google Authenticator） | 部分 | 防密码泄露，但可被实时钓鱼 |
| 持有（强） | FIDO2/WebAuthn 密钥、PIV 卡 | 是 | 首选，绑定-origin 防钓鱼 |

## 强制范围

CISA 要求对一切暴露面强制 MFA：邮件 Web 登录、VPN/远程访问、管理员后台、以及财务等高价值账号。这与 NIST SP 800-63B 的 MFA 要求同频，也是阻断 BEC（凭据窃取型）的第一道闸。

## 部署实践

* 优先给管理员与高管发 FIDO2 硬件密钥；普通用户可用平台内置通行密钥（passkey）。
* 对无法升级的旧系统，至少启用 TOTP App，禁用 SMS/语音。
* 结合条件访问：异常登录地/设备触发 step-up MFA 或阻断。

## 对信创邮件与政企的启示

信创邮件系统替换 Exchange 时，身份模块应默认开启 MFA、优先 FIDO2/国密 USBKey，并将"管理员+财务+高管"列为强制范围。这与邮件账号防盗体系、等保身份鉴别要求叠加，构成 BEC 防护的基石。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/cisa-mfa-implementation-guide.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
