---
title: "在邮件 TLS 上部署 DANE 有什么价值与局限？"
source: "https://ztpop.net/kb/dane-faq-08.html"
license: CC-BY 4.0
---

# 在邮件 TLS 上部署 DANE 有什么价值与局限？

1
在邮件 TLS 上部署 DANE 有什么价值与局限？
▼

**价值**

DANE 在 DNSSEC 之上同时实现“强制 TLS + 证书认证”，能有效防御 SMTP 降级与中间人攻击，且无需依赖公共 CA——对自签/私有 CA 的基础设施尤为友好。

**局限**

前提是收发双方都部署了 DNSSEC 与 TLSA，且需在证书轮换时同步更新 TLSA（否则会断邮）。在 DNSSEC 覆盖不足的跨域互操作中，仍需 MTA-STS 兜底。DANE 是强补充，而非处处可用的默认。

参考：RFC 7671（运维与安全考量）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/dane-faq-08.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
