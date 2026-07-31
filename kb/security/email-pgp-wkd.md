---
title: "PGP 的 Web Key Directory（WKD，RFC 7929）是什么？它如何让人“免手动交换公钥”就能加密？"
source: "https://ztpop.net/kb/email-pgp-wkd.html"
license: CC-BY 4.0
---

# PGP 的 Web Key Directory（WKD，RFC 7929）是什么？它如何让人“免手动交换公钥”就能加密？

1
PGP 的 Web Key Directory（WKD，RFC 7929）是什么？它如何让人“免手动交换公钥”就能加密？
▼

**原理**

WKD 把用户 PGP 公钥按“邮箱哈希”放在其域名的 https://.../well-known/openpgpkey/ 路径下；发信方客户端查该 HTTPS 端点自动取对方公钥，无需手动导入（RFC 7929）。

**流程**

Alice 给 bob@example.com 发加密信，客户端 GET https://example.com/.well-known/openpgpkey/.../ 取 Bob 公钥→加密→发送；Bob 私钥本地解密。密钥发现自动化、基于 HTTPS 可信。

**价值**

解决“公钥分发难”痛点，使端到端加密可规模使用；与密钥服务器相比更可控、防污染。

**实践**

域名可部署 WKD（需 HTTPS + 正确路径与哈希）；邮件系统若支持 WKD 发现，可提升用户间加密可用性（见 S/MIME+PGP 基础）。

参考：RFC 7929（Web Key Directory）；OpenPGP / WKD 实践

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-pgp-wkd.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
