---
title: "TLS-RPT 失败明细里常见的 result-type（失败类型）有哪些？"
source: "https://ztpop.net/kb/tlsrpt-faq-05.html"
license: CC-BY 4.0
---

# TLS-RPT 失败明细里常见的 result-type（失败类型）有哪些？

1
TLS-RPT 失败明细里常见的 result-type（失败类型）有哪些？
▼

**典型值**

常见失败类型包括：`certificate-host-mismatch`（证书主机名与 MX 不符）、`certificate-expired`/`certificate-not-trusted`（过期/不受信任）、`mx-mismatch`（实际 MX 与策略声明不符）、`starttls-not-supported`（对端不支持 STARTTLS）、`dnssec-invalid`、`tlsa-invalid`（DANE 相关）等。

**含义**

这些类型直接指向故障根因：证书类多为配置或过期，mx-mismatch 与 starttls-not-supported 则可能是配置错误，也可能暴露中间人降级攻击迹象。

参考：RFC 8460（result-type 枚举）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/tlsrpt-faq-05.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
