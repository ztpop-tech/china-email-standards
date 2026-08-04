---
title: "NIST SP 800-177 对可信邮件（SMTP/传输安全）提出了哪些建议？"
source: "https://ztpop.net/kb/nist-sp800-177-smtp-transport-security.html"
license: CC-BY 4.0
---

# NIST SP 800-177 对可信邮件（SMTP/传输安全）提出了哪些建议？

1
NIST SP 800-177 对可信邮件（SMTP/传输安全）提出了哪些建议？
▼

**定位与范围**

SP 800-177 Rev.1 于 2019 年 2 月发布，前身是 2016 年的 SP 800-177；主要受众是企业邮件管理员、信息安全专家与网络管理员，适用于联邦 IT 系统，也可供中小组织参考。其核心目标是「增强对电子邮件的信任」。

**发件域认证：SPF / DKIM / DMARC**

该文件与核心 SMTP、DNS 配合，推荐三类机制做发送域认证：SPF（Sender Policy Framework）声明授权发信 IP、DKIM（DomainKeys Identified Mail）对单封邮件做密码学签名、DMARC（基于域的消息认证、报告与一致性）告诉接收方对未通过认证邮件的处理策略。三者共同弥补 SMTP 协议本身缺乏源认证的弱点，抑制伪造发件域的钓鱼与垃圾邮件。

**传输安全：TLS 与证书认证**

对于邮件传输安全，文件推荐传输层安全（TLS）及相关的证书认证协议，对邮件在传输途中加密。关键词中还列出 DANE（DNS-Based Authentication of Named Entities），即借助 DNSSEC 绑定证书/公钥，缓解 TLS 握手被降级或伪造的风险。落地时可叠加 MTA-STS 与 TLS-RPT 以强制并监控加密传输。

**内容安全：S/MIME**

针对邮件内容安全，文件建议用 S/MIME（Secure/Multipurpose Internet Mail Extensions）及其证书与密钥分发协议，对邮件内容做加密与认证，保护端到端机密性与完整性，作为传输层 TLS 之外的补充控制。

参考：NIST SP 800-177 Rev.1《Trustworthy Email》(https://doi.org/10.6028/NIST.SP.800-177r1；2019-02，作者 Scott Rose 等)，关键词与摘要

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/nist-sp800-177-smtp-transport-security.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
