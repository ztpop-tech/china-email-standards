---
title: "什么是“仿冒域名 / 打字 squatting（Typosquatting）”？如何防御？"
source: "https://ztpop.net/kb/lookalike-domain-typosquatting-defense.html"
license: CC-BY 4.0
---

# 什么是“仿冒域名 / 打字 squatting（Typosquatting）”？如何防御？

1
什么是“仿冒域名 / 打字 squatting（Typosquatting）”？如何防御？
▼

**机理**

注册与贵司极相似的域名（多字母/换形字符/额外后缀/错拼），发送钓鱼冒充贵司，骗取客户与员工信任。

**识别**

比对发件域与官方域的“视觉/拼写/Unicode 同形字（如拉丁 o 与西里尔 о）”；用 DMARC 报表查看“以你域名义失败”的未知来源。

**技术防御**

强制 DMARC p=reject 让仿冒被收方拒绝；SPF/DKIM 覆盖所有发送源；对关键相似域做“防御性注册”与持续监控。

**人的防御**

培训员工与客户核对域名而非仅看显示名；对“似像非像”的发件一律二次确认；公布官方域名清单供比对。

参考：RFC 7489（DMARC）；ICANN 同形字/IDN 安全建议；CISA 域名仿冒防护

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/lookalike-domain-typosquatting-defense.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
