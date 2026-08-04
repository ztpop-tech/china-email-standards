---
title: "RFC 9580 定义的 OpenPGP 与 RFC 3156 的 PGP/MIME 在邮件加密中如何配合？"
source: "https://ztpop.net/kb/rfc9580-openpgp-email-encryption.html"
license: CC-BY 4.0
---

# RFC 9580 定义的 OpenPGP 与 RFC 3156 的 PGP/MIME 在邮件加密中如何配合？

1
RFC 9580 定义的 OpenPGP 与 RFC 3156 的 PGP/MIME 在邮件加密中如何配合？
▼

**现行标准是 RFC 9580，不再是 RFC 4880**

长期以来被引用的 OpenPGP 标准是 2007 年的 RFC 4880。**2024 年 7 月发布的 RFC 9580 已经正式取代它**，同时取代了 RFC 5581（Camellia 密码算法）与 RFC 6637（椭圆曲线密码支持），成为单一的现行规范。任何在 2026 年撰写的技术方案，若仍以 RFC 4880 为唯一依据，都应当复核是否需要更新到 RFC 9580。

RFC 9580 定义的是**消息格式与密码学容器**：数据包（packet）语法、密钥与子密钥结构、签名类型、字符串到密钥的转换（S2K）、密钥指纹计算等。它本身并不规定这些数据如何放进一封邮件——那是 RFC 3156 的职责。

**RFC 9580 的主要演进点**

* **版本 6 密钥与版本 6 签名**：在既有的 v4 之外引入新的密钥与签名版本，指纹计算方式随之更新，为长期算法敏捷性留出空间。
* **AEAD 认证加密**：新的对称加密数据包形态支持带关联数据的认证加密模式，取代早期"对称加密 + MDC 完整性包"的组合，把机密性与完整性合并到一个经过充分分析的原语中。
* **现代曲线与算法**：正式纳入 X25519 / X448 用于密钥协商、Ed25519 / Ed448 用于签名，并为它们分配了新的算法标识。
* **更强的口令派生**：引入内存硬（memory-hard）的 Argon2 作为 S2K 选项，显著提高对口令保护私钥做离线爆破的成本。

对部署方的直接影响是**互操作窗口**：新旧实现在过渡期内并存，生成 v6 密钥或使用新 AEAD 形态的一方，可能无法被仍停留在 v4/RFC 4880 语义的对端解析。批量迁移前必须先摸清通信对象的实现版本，或在密钥上同时提供向后兼容的能力声明。

**PGP/MIME：邮件侧的承载规则**

RFC 3156 定义了三个媒体类型与两种组合方式：

* **加密**：`multipart/encrypted`，protocol 参数为 `application/pgp-encrypted`；第一部分是版本标识部分，第二部分为 `application/octet-stream` 承载实际密文。
* **签名**：`multipart/signed`，protocol 参数为 `application/pgp-signature`，第二部分承载分离式签名。

与之相对的是历史上的**内联 PGP**（把 ASCII armor 直接写进 text/plain 正文）。内联方式无法覆盖附件、无法正确处理多部分结构与字符集，也容易被邮件系统的换行与编码改写破坏签名，规范化的做法是使用 PGP/MIME。

另有一处工程细节常被忽略：RFC 3156 要求签名前对内容做规范化处理（行结束符统一为 CRLF、避免尾随空白），因为传输过程中的空白与换行改写是 PGP 邮件签名失效最常见的原因之一。

**与 S/MIME 的信任模型差异**

技术封装之外，OpenPGP 与 S/MIME 最根本的差别在信任来源：S/MIME 依赖**层级式 CA**，信任自根锚点向下传递，天然适配企业统一签发与集中管理；OpenPGP 传统上依赖**去中心化的信任网络**与直接密钥交换，密钥的真实性由用户自行确认或由本地策略决定。

这导致运维模式完全不同。OpenPGP 部署的真正难点不在加解密，而在**密钥发现与真实性确认**：如何在首次通信时拿到对方正确的公钥、如何在密钥更换或吊销后让对端及时感知。企业环境中若无法建立可靠的密钥分发通道，端到端加密的实际安全收益会被中间人替换公钥的风险大幅抵消。选型时应把"密钥生命周期能否被管住"作为首要判据，而非算法强度。

参考：IETF [RFC 9580《OpenPGP》](https://www.rfc-editor.org/rfc/rfc9580.txt)（Standards Track，2024-07，取代 RFC 4880、RFC 5581、RFC 6637）；邮件承载见 [RFC 3156《MIME Security with OpenPGP》](https://www.rfc-editor.org/rfc/rfc3156.txt)（Standards Track，2001-08）；历史版本 [RFC 4880](https://www.rfc-editor.org/rfc/rfc4880.txt)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/rfc9580-openpgp-email-encryption.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
