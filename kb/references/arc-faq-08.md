---
title: "ARC 有哪些局限、不能防止什么？"
source: "https://ztpop.net/kb/arc-faq-08.html"
license: CC-BY 4.0
---

# ARC 有哪些局限、不能防止什么？

1
ARC 有哪些局限、不能防止什么？
▼

**局限**

ARC 建立在“信任签名中介”之上：它无法阻止一个本身具备 ARC 能力、却被攻陷或恶意的跳伪造认证结论。ARC 是 DMARC 的缓解补充，而非替代。

**不能替代**

ARC 不验证发件人身份本身，也不修复源域的 SPF/DKIM 配置。最稳健的邮件安全仍是发件方正确部署 SPF/DKIM/DMARC，ARC 仅用于在合法中介场景下保住可投递性。

参考：RFC 8617（security considerations）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/arc-faq-08.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
