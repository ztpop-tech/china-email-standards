---
title: "如何用 Received-SPF / Received-DKIM / Received-ARC 辅助判定？"
source: "https://ztpop.net/kb/header-faq-07.html"
license: CC-BY 4.0
---

# 如何用 Received-SPF / Received-DKIM / Received-ARC 辅助判定？

1
如何用 Received-SPF / Received-DKIM / Received-ARC 辅助判定？
▼

**Received-SPF**

部分 MTA 会在邮件里写入 Received-SPF 头，记录对信封域 SPF 检查的结论与使用的域名，便于在不依赖下游 Authentication-Results 时直接查看 SPF 结果。

**Received-DKIM**

类似地，Received-DKIM（或 DKIM-Signature 头的存在与验证备注）记录 DKIM 验证细节：用了哪个选择器、结果 pass/fail、body hash 是否匹配，是核查“签名域是否等于声称域”的直接证据。

**Received-ARC**

当邮件经合法转发（如邮件列表、网关）时，ARC 会把原始 Authentication-Results 封装进 ARC 头链（AAR/AMS/AS）。Received-ARC 或 ARC-Seal 可证明“原始认证结论在转发后仍被完整保留”，从而避免被误判为伪造。

**综合使用**

三者在邮件头里形成“信封 SPF → 内容 DKIM → 转发 ARC”的证据链。排查时优先看 Authentication-Results，缺失或被剥离时再用这些 Received-\* 头补证。

参考：RFC 7208（SPF）；RFC 6376（DKIM）；RFC 8617（ARC）；RFC 7001

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/header-faq-07.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
