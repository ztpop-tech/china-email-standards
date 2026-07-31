---
title: "MTA-STS 与 TLS-RPT 是什么关系？为什么要一起部署？"
source: "https://ztpop.net/kb/mtasts-faq-08.html"
license: CC-BY 4.0
---

# MTA-STS 与 TLS-RPT 是什么关系？为什么要一起部署？

1
MTA-STS 与 TLS-RPT 是什么关系？为什么要一起部署？
▼

**协同**

MTA-STS 负责“强制 TLS”，而 TLS-RPT（RFC 8460）负责“报告 TLS 连接失败”。两者通过各自 DNS 记录（`_mta-sts` 与 `_smtp._tls`）配合。

**价值**

仅启用 MTA-STS 时，若策略配错或对端证书异常，你可能只看到邮件被拒却不知原因。开启 TLS-RPT 后，发送方会把每次 TLS 失败（证书不匹配、MX 不匹配、不支持 STARTTLS 等）汇成报告发到你指定的邮箱，便于排查与持续优化。

参考：RFC 8460 (TLS-RPT)；Cloudflare “Next steps” 提及 TLS/ARC Postmaster

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/mtasts-faq-08.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
