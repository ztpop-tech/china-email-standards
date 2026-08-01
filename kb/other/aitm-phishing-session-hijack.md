---
title: "什么是“中间人钓鱼（AiTM）”？它如何窃取会话、该如何阻断？"
source: "https://ztpop.net/kb/aitm-phishing-session-hijack.html"
license: CC-BY 4.0
---

# 什么是“中间人钓鱼（AiTM）”？它如何窃取会话、该如何阻断？

1
什么是“中间人钓鱼（AiTM）”？它如何窃取会话、该如何阻断？
▼

**机理**

攻击者搭建反向代理站点（钓鱼页）夹在用户与真实登录页之间；用户输入凭据与一次性 MFA 码，代理实时转发给真站，从而拿到“已认证的会话 Cookie/令牌”。

**危害**

传统 MFA（OTP/推送）被实时中继绕过——用户确实完成了认证，但攻击者已窃得会话；之后用 Cookie 直接进邮箱，无需再次认证，邮件被长期窃取。

**检测**

关注异常登录（新设备/新 IP/异常 ASN）、不可能旅行、登录后立刻导出或建转发规则；用 UEBA/风险登录评分，并检查 Authentication-Results 与登录日志。

**阻断**

采用防钓鱼 MFA（通行密钥/FIDO2，具源绑定抗中继）；叠加设备合规与条件访问；会话短时效加风控重认证；发现可疑会话及时吊销（参见 CISA 指南）。

参考：CISA 账户保护指南（防钓鱼 MFA）；Microsoft 安全博客（AiTM 钓鱼）；RFC 9325（HTTPS 安全配置）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/aitm-phishing-session-hijack.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
