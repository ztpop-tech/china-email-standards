---
title: "PGP/GPG 邮件加密完全指南"
source: "https://ztpop.net/kb/pgp-gpg-guide.html"
license: CC-BY 4.0
---

# PGP/GPG 邮件加密完全指南

摘要：PGP（Pretty Good Privacy）由 Phil Zimmermann 于 1991 年创建，开创了大众可用的强加密时代。其开源实现 GnuPG（GPG）今天仍是技术社区和隐私倡导者首选的邮件加密工具。与 S/MIME 依赖 CA 的分层信任模型不同，PGP 采用去中心化的信任网络（Web of Trust）模型，赋予用户完全自主的密钥管理权。本文基于 RFC 4880（OpenPGP 消息格式）和 RFC 3156（PGP/MIME），从非对称加密原理到 GPG 实践，提供一份独立完整的 PGP 邮件加密指南。

**一、非对称加密原理与 PGP 混合加密**
PGP 的安全基础是非对称加密（也称公钥加密）。每位用户生成一对数学关联的密钥——公钥（Public Key）和私钥（Private Key）。公钥可以公开分发给任何人，私钥必须严格保密且由强密码短语保护。公钥加密的数据只有对应私钥能解密，私钥签名的数据任何人都可以用公钥验证。然而，非对称加密计算量巨大，不适合直接加密长邮件。PGP 采用混合加密方案：为每封邮件随机生成一个一次性会话密钥（Session Key），用对称加密算法（如 AES-256）快速加密邮件内容，再用接收者的公钥加密这个会话密钥。接收者收到邮件后，用自己的私钥解密出会话密钥，再用会话密钥解密邮件正文。这种设计兼顾了安全性与性能。

**二、GPG 密钥生成与最佳实践**
GnuPG（GPG）是 OpenPGP 标准（RFC 4880）最广泛使用的开源实现。安装 GPG（Linux/macOS 通常预装，Windows 安装 Gpg4win）后，使用 gpg --full-generate-key 命令生成密钥对。密钥生成过程中的关键选择：算法推荐使用 ECC（椭圆曲线）如 Curve25519（ed25519/cv25519），比传统 RSA 提供相同安全强度下更短的密钥长度和更快的运算速度。如无特殊兼容性要求，优先选择 ed25519 签名密钥 + cv25519 加密子密钥的组合。

密钥保护至关重要。主密钥（Master Key/Certification Key）仅用于签发子密钥和认证其他密钥，日常不应使用主密钥进行签名和加密。应生成独立的签名子密钥（Signing Subkey）和加密子密钥（Encryption Subkey），日常操作仅使用子密钥。主密钥私钥应从日常使用的计算机中导出并离线存储在加密的 USB 驱动器或硬件安全模块（如 YubiKey、Nitrokey）中，仅在签发新子密钥或吊销密钥时才将其临时加载到安全环境中。这种「主密钥离线、子密钥在线」的实践可以最大限度地降低密钥泄露风险——即使日常工作计算机被攻破，攻击者也只能获取子密钥，无法彻底接管整个 PGP 身份。

**三、PGP/MIME 格式规范 (RFC 3156)**
PGP/MIME 定义了 PGP 加密邮件在 MIME 邮件框架中的封装方式。RFC 3156 规定了两种内容类型：multipart/signed 用于 PGP 签名邮件（邮件正文为明文，签名数据作为第二个 MIME 部分附加），multipart/encrypted 用于 PGP 加密邮件（第一个部分标识加密参数，第二个部分为加密后的数据）。标准的 PGP/MIME 邮件头会包含 Content-Type: multipart/encrypted; protocol="application/pgp-encrypted" 等信息，兼容的邮件客户端据此自动识别并解密/验证。PGP/Inline 是另一种旧式格式，将 PGP 加密块直接嵌入邮件正文，兼容性更好但容易在转发和引用时出现问题，建议优先使用 PGP/MIME 格式。

**四、Web of Trust 信任网络模型**
与 S/MIME 依赖 CA 的层级信任模型不同，PGP 采用去中心化的信任网络（Web of Trust）模型。在这个模型中，每位用户可以通过数字签名为他人的公钥「背书」——当你验证了 Alice 的身份并签名她的公钥后，你的签名表示「我确认这个公钥确实属于 Alice」。当你收到 Bob 的公钥时，如果你信任的 Alice 签名了 Bob 的公钥，你就可以通过信任传递间接信任 Bob 的公钥。信任网络通过多个信任路径的交织形成一张「网络」，使得用户无需依赖中央 CA 就能验证陌生人的公钥。

信任网络的运维涉及几个关键概念：密钥签名（Key Signing）——使用你的私钥为他人公钥生成数字签名；信任级别（Trust Level）——你对某个密钥持有者身份的确认程度（unknown/none/marginal/full/ultimate）；签名策略——签发密钥时可以指定签名范围（本地、通用、管制）。在实际使用中，密钥签名派对（Key Signing Party）是信任网络建设的重要社区活动——参与者携带身份证明和密钥指纹，在物理见面中相互验证身份并交换和签名公钥。

**五、Thunderbird 与 GPG 客户端配置**
Thunderbird 78 及以上版本内置了 OpenPGP 支持，无需额外安装插件。配置步骤：安装 Gpg4win（Windows）或 GPG Suite（macOS）→ 生成密钥对（或导入已有密钥）→ 打开 Thunderbird → 菜单 → 账户设置 → 端到端加密 → 选择 OpenPGP → 选择对应的密钥 → 设置默认签名和加密策略。Thunderbird 内置的 OpenPGP 实现（使用 RNP 库）支持密钥生成、导入导出、密钥服务器同步和自动加密（如果已拥有所有接收者的公钥）。

对于偏好命令行或需要自动化集成的用户，GPG 直接操作是最灵活的方式。常用命令包括：gpg --encrypt --sign --armor -r recipient@example.com message.txt（签名并加密文件）、gpg --decrypt encrypted.asc（解密文件）、gpg --list-keys（查看公钥环）、gpg --send-keys --keyserver keys.openpgp.org FINGERPRINT（上传公钥到密钥服务器）、gpg --recv-keys FINGERPRINT（从密钥服务器获取公钥）。自动化脚本（如 procmail、cron）可以集成 GPG 命令实现邮件的自动加解密和归档。

**六、PGP 密钥管理与维护最佳实践**
密钥管理是 PGP 使用中最容易出错的环节。以下是关键最佳实践：设置密钥过期日期——不要创建永不过期的密钥。建议主密钥有效期 2-3 年，子密钥 1-2 年，到期前续期或生成新子密钥。这是因为如果密钥永不过期且私钥丢失（且没有吊销证书），你将被永久锁定在该 PGP 身份之外。创建吊销证书——在生成密钥后立即创建吊销证书（gpg --gen-revoke），将其打印在纸上并安全保存。如果私钥泄露或丢失，发布吊销证书可以通知其他人该密钥不再可信。

使用强密码短语——保护私钥的密码短语应至少有 60 位熵（约等于 10 个随机单词或 20 个随机字符）。可以考虑使用 Diceware 方法生成易记但高熵的密码短语。定期轮换子密钥——主密钥应保持长期不变（因为你的信任网络和声誉累积在主密钥上），但签名和加密子密钥应定期轮换（1-2 年），以限制单一子密钥泄露的影响范围。在切换到新计算机或重装系统前，务必备份 .gnupg 目录（私钥、公钥环和信任数据库），否则将永久失去 PGP 身份。

总结：PGP/GPG 提供了独立于 CA 体系的去中心化邮件加密方案，赋予用户完全自主的密钥管理权。虽然学习曲线较 S/MIME 更陡峭，但其开放性、灵活性和隐私保护特性使其在技术社区中拥有不可替代的地位。掌握 GPG 密钥管理的最佳实践，是安全使用 PGP 邮件加密的前提。

**参考来源**
RFC 4880 - OpenPGP Message Format; RFC 3156 - MIME Security with OpenPGP; GnuPG 官方文档 (https://gnupg.org/documentation/); RFC 6637 - ECC in OpenPGP; NIST SP 800-57 - Key Management Recommendations。

了解更多邮件技术实践，请访问知识库或联系

## 📦 相关产品与方案

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/pgp-gpg-guide.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
