---
title: "已经部署 DNSSEC 了，为什么还需要 MTA-STS？"
source: "https://ztpop.net/kb/mtasts-faq-07.html"
license: CC-BY 4.0
---

# 已经部署 DNSSEC 了，为什么还需要 MTA-STS？

1
已经部署 DNSSEC 了，为什么还需要 MTA-STS？
▼

**分工**

DNSSEC 保证 DNS 响应不被篡改，但 SMTP 的 TLS 投递是否发生、对端证书是否可信，并不由 DNSSEC 直接保证；而且现实中大量域并未部署 DNSSEC。

**互补**

MTA-STS 在应用层明确“必须 TLS、只允许这些 MX”，并通过 HTTPS 托管策略，独立于对端 DNSSEC 部署情况即可生效，是对 DANE/DNSSEC 路线的务实补充（尤其跨域互操作时）。

参考：RFC 8461 动机；Cloudflare 说明（并非人人用 DNSSEC，故用 HTTPS 避免新 MITM 面）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/mtasts-faq-07.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
