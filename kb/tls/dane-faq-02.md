---
title: "DANE 如何用 DNSSEC“绑定”证书、从而摆脱对公共 CA 的依赖？"
source: "https://ztpop.net/kb/dane-faq-02.html"
license: CC-BY 4.0
---

# DANE 如何用 DNSSEC“绑定”证书、从而摆脱对公共 CA 的依赖？

1
DANE 如何用 DNSSEC“绑定”证书、从而摆脱对公共 CA 的依赖？
▼

**机制**

管理员在已签名的 DNS 区里发布 TLSA 记录，写明“本服务应呈现的证书指纹或受信任锚”。由于整个区由 DNSSEC 签名，解析结果可被验证、不可被中间人篡改。

**效果**

接收方在 TLS 握手时，把对端出示的证书与 DNS 中的 TLSA 声明比对：只要 DNSSEC 校验通过且证书匹配，即便该证书不是公共 CA 签发（自签或用私有 CA），也被视为可信。这就把信任根从“公共 CA”转移到“DNSSEC + 域名持有者”。

参考：RFC 6698 第 3 节；RFC 7671

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/dane-faq-02.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
