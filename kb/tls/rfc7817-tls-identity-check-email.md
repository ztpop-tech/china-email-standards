---
title: "RFC 7817 规定邮件客户端如何校验 TLS 服务器证书身份？"
source: "https://ztpop.net/kb/rfc7817-tls-identity-check-email.html"
license: CC-BY 4.0
---

# RFC 7817 规定邮件客户端如何校验 TLS 服务器证书身份？

1
RFC 7817 规定邮件客户端如何校验 TLS 服务器证书身份？
▼

**规范定位与替代关系**

RFC 7817 描述 SMTP 提交、IMAP、POP 与 ManageSieve 客户端的 TLS 服务器身份核验流程。它取代了 RFC 2595 的 2.4 节（Server Identity Check），并更新了 RFC 3207 的 4.1 节（STARTTLS 之后的处理）、RFC 3501 的 11.1 节（STARTTLS 安全考量）以及 RFC 5804 的 2.2.1 节。换言之，凡是仍按 RFC 2595 老规则做主机名匹配的邮件客户端实现，都应迁移到本文档。

**核验流程与参考标识**

在 TLS 协商期间，邮件客户端**必须**将自己理解的服务器身份（客户端的「参考标识」）与服务器 Certificate 消息中呈现的身份进行比对，以防范中间人攻击。该检查只在服务器证书通过 RFC 5280 第 6 节的证书路径验证之后执行，匹配则依 RFC 6125 第 6 节的规则进行，包括不同标识类型的匹配优先次序、「证书固定」以及匹配失败时的处理流程。

参考标识的取值规则为：对 DNS-ID 与 CN-ID 类型，客户端必须使用以下之一或多个——(a) 用户邮件地址的域名部分，(b) 用于建立连接的主机名（不做 CNAME 规范化）；也可以使用 (c) 由 (a) 或 (b) 安全派生的值，例如经 DNSSEC 校验的查询结果。当使用 RFC 6186 的邮件服务发现流程时，客户端**还必须**把用户邮件地址的域名部分作为另一个参考标识，用于与证书中的 SRV-ID 比对。

**五条补充规则**

* 邮件客户端软件实现**必须**支持 DNS-ID 标识类型（dNSName 类型的 subjectAltName）。
* 支持 RFC 6186 的邮件客户端实现**必须**支持 SRV-ID 标识类型（RFC 4985 定义的 SRVName 类型 subjectAltName）；ManageSieve 协议使用服务名 `sieve`。
* 客户端**不得**使用 URI-ID 标识类型（uniformResourceIdentifier 类型 subjectAltName）做服务器核验，因为 URI-ID 在历史上并未用于邮件。
* 为兼容既有部署软件，**可以**使用 CN-ID 标识类型（subject 名称中的 CN 属性）做身份核验。
* 邮件协议允许服务器所呈现标识中使用一定形式的通配符：`*` 可用作 DNS-ID 或 CN-ID 的**最左名称组件**。例如 `*.example.com` 匹配 `a.example.com`、`foo.example.com`，但不匹配 `example.com`。通配符**不得**作为最左名称组件的片段使用，即 `*oo.example.com`、`f*o.example.com`、`foo*.example.com` 这类写法均不合规。

**部署要点**

文档另设两份合规检查清单：一份面向证书颁发机构（含对受托代管邮件服务的处理说明），一份面向邮件服务提供商与证书签名请求（CSR）生成工具（含多域名托管场景的说明）。对运维的实际含义是：当邮件域与实际邮件主机名不一致（例如域为 `example.com` 而服务器为 `mail.hoster.net`）时，仅靠 DNS-ID 无法让基于邮件地址域名的客户端通过校验，应当在证书中同时签发覆盖邮件域的 SRV-ID（如 `_imaps.example.com`）或相应 DNS-ID，否则采用 RFC 6186 自动发现的客户端会出现身份校验失败。

参考：IETF [RFC 7817《Updated Transport Layer Security (TLS) Server Identity Check Procedure for Email-Related Protocols》](https://www.rfc-editor.org/rfc/rfc7817.txt)（Standards Track，2016-03）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/rfc7817-tls-identity-check-email.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
