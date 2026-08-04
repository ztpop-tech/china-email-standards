---
title: "如何用 NIST CSF 2.0 六大功能映射邮件防护？"
source: "https://ztpop.net/kb/nist-csf-2-0-email-protection.html"
license: CC-BY 4.0
---

# 如何用 NIST CSF 2.0 六大功能映射邮件防护？

1
如何用 NIST CSF 2.0 六大功能映射邮件防护？
▼

**CSF 2.0 的六个功能**

NIST 网络安全框架 2.0 由六个并列功能（Functions）组成：**GOVERN（治理）**、**IDENTIFY（识别）**、**PROTECT（防护）**、**DETECT（检测）**、**RESPOND（响应）**、**RECOVER（恢复）**。相比 1.1，2.0 **新增 GOVERN**，强调网络安全风险管理须由治理层驱动，贯穿其余五个功能。

**GOVERN 与 IDENTIFY（治理与识别）**

GOVERN：把邮件安全纳入组织网络安全战略、政策与角色职责，明确责任人与风险容忍度。IDENTIFY：梳理邮件资产（邮件服务器、网关、域名、收发账号）、数据流与依赖关系，并完成风险分类，为后续控制选型提供依据。

**PROTECT（防护）映射**

在防护层落实具体邮件控制：强制 SPF/DKIM/DMARC（建议 p=quarantine/reject）、全域名 TLS 与 MTA-STS、全员 MFA（优先防钓鱼 MFA）、最小权限账号管理、S/MIME 内容加密。这些控制直接对应 DMARC/STARTTLS 等治理要求。

**DETECT / RESPOND / RECOVER（检测·响应·恢复）**

DETECT：监控异常发信、DMARC 失败率、伪造域名与邮箱数据外泄信号。RESPOND：对钓鱼/BEC 事件做隔离账号、撤销会话、取证与通报。RECOVER：从备份或归档恢复被篡改/加密的邮箱，复盘并加固控制。三功能形成邮件事件的闭环运营。

参考：NIST CSF 2.0《Cybersecurity Framework 2.0》(https://doi.org/10.6028/NIST.CSWP.29；NIST CSWP 29)，六大功能定义

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/nist-csf-2-0-email-protection.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
