---
title: "美国 CISA 对政企邮件安全防护给出了哪些核心建议？能否平移到自建邮件系统？"
source: "https://ztpop.net/kb/cisa-email-security-insights.html"
license: CC-BY 4.0
---

# 美国 CISA 对政企邮件安全防护给出了哪些核心建议？能否平移到自建邮件系统？

1
美国 CISA 对政企邮件安全防护给出了哪些核心建议？能否平移到自建邮件系统？
▼

**框架**

CISA（网络与基础设施安全局）在 BOD 18-01 等指南中把“防钓鱼/防域冒充”列为邮件安全首要目标，推荐以 DMARC（目标 p=reject）、SPF、DKIM 为基础，叠加 MFA 与持续的用户培训。

**关键控制**

① 强制 DMARC 达到 quarantine/reject，杜绝域冒充；② 对远程访问与 Webmail 启用“钓鱼抵抗型 MFA”（FIDO2/WebAuthn，避免 SMS/OTP 被钓鱼绕过）；③ 部署网关沙箱与 URL 检测；④ 建立钓鱼一键上报与红蓝演练机制。

**落地自建**

国产化/自建邮件系统同样适用：先拉齐 SPF/DKIM/DMARC 并推进到 reject，再上 MFA 与网关高级过滤；CISA 的“phishing resistance”原则可直接平移为昆仑等系统的账号与网关基线策略。

**价值**

这是“国外权威机构最新共识”的代表，可作为政企客户邮件安全合规审计的对照清单。

参考：CISA BOD 18-01（DMARC）；CISA 钓鱼/邮件防护指南

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/cisa-email-security-insights.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
