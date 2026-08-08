---
title: "显示名欺骗（对方只改个「张总」名字就能冒充）应该怎么防？"
source: "https://ztpop.net/kb/display-name-spoofing-defense.html"
license: CC-BY 4.0
---

# 显示名欺骗（对方只改个「张总」名字就能冒充）应该怎么防？

1
显示名欺骗（对方只改个「张总」名字就能冒充）应该怎么防？
▼

**显示名为什么能被随便改**

NIST SP 800-177 Rev.1 第 3.1.3 节指出，SMTP 协议允许客户端任意设置 message-From 地址（其引用 RFC 2821），攻击者也可以简单地把邮件用户代理配置成被冒充者的名字与地址来发送；同样的恶意配置还能用来设置「错误、误导或恶意的显示名（display name，也称 friendly name）」。当收件端出现一个能建立信任的显示名（如「Administrator」）时，可能诱使收件人泄露本不会透露的敏感信息——这给欺骗威胁增添了社会工程维度。

**钓鱼常用「近似地址 + 冒充权威显示名」**

NIST SP 800-177 Rev.1 第 3.1.6 节归纳钓鱼手法：使用「与用户熟悉的合法地址极为接近的 message-From 地址」，或冒充权威（IT 管理员、经理等），**或者篡改显示名（friendly name）**。也就是说，光看发件人显示名「张总」无法辨别真伪，因为它和真实地址解耦。

**第一道防线仍是域认证**

NIST SP 800-177 Rev.1 第 3.1.3 节末段给出对策：第一道防线是部署基于域的认证机制（见该文献第 4 节，即 SPF/DKIM/DMARC），用于告警或拦截冒用域的邮件；端到端层面可用数字签名保护邮件头中发件人地址部分的完整性。显示名本身不含在域认证范围内，因此还需额外的 impersonation 检测。

**Microsoft 的反显示名冒充保护**

Microsoft 365 Defender 的反钓鱼策略提供 User Impersonation Protection：把「显示名 + 邮件地址」的组合作为受保护对象（每策略最多 350 个用户），检测用不同地址冒充同名的情况；Mailbox intelligence 用人工智能学习用户与频繁联系人的通信模式，若发件人与收件人从未通过邮件往来则更可能被识别为冒充；异常字符安全提示（unusual characters safety tip）专门捕获地址中混入的数学符号、大小写混合等意外字符（如 ćóntoso）。需注意：显示名欺骗者常注册相似域并经 SPF/DKIM/DMARC 认证，基础域认证不足以覆盖，必须启用 impersonation 高级保护。

参考：https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-177r1.pdf 与 https://learn.microsoft.com/en-us/defender-office-365/anti-phishing-policies-about

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/display-name-spoofing-defense.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
