---
title: "国密 SM4 算法在邮件系统中的应用"
source: "https://ztpop.net/kb/sm4-encryption-email-application.html"
license: CC-BY 4.0
---

# 国密 SM4 算法在邮件系统中的应用

## 一、引言

国家密码管理局发布的 SM4 分组密码算法（GB/T 32907-2016）是我国商用密码体系的核心算法之一。随着《密码法》和信创政策的深入推进，SM4 在邮件系统中的应用正从局部试点走向全面落地。邮件系统作为党政机关和关键信息基础设施的核心业务系统，必须满足等保三级/等保 2.0 中对密码保护的要求。

## 二、SM4 算法简介

SM4 是一种 128 位分组、128 位密钥的对称分组密码算法，采用 32 轮非线性迭代结构。其设计适用于软件和硬件实现，在国密系列中对应对称加密角色，相当于 AES 在国际标准中的地位。SM4 算法的分组长度和密钥长度均为 128 比特，解密过程与加密过程使用相同的密钥调度算法，结构对称。

国密加密体系包含以下核心算法：

* **SM2** — 椭圆曲线公钥密码算法（对标 ECDSA/ECDH）
* **SM3** — 密码杂凑算法（256 位输出，对标 SHA-256）
* **SM4** — 分组密码算法（对标 AES-128）
* **SM9** — 基于标识的密码算法（对标 IBC）

## 三、SM4 在邮件系统中的应用场景

### 3.1 SMTP 传输层加密

RFC 8998（2021 年 3 月发布，Informational）定义了将国密算法应用于 TLS 1.3 的密码套件。这使邮件系统的 STARTTLS 或隐式 TLS 可以使用 SM4 进行传输加密。具体套件为：

* `TLS_SM4_GCM_SM3` — 使用 SM4-GCM 模式进行加密，SM3 作为 HMAC。该套件在 TLS 1.3 中使用。  
  对应的 TLS 1.2 版本为 `TLS_ECDHE_SM4_CBC_SM3`（需配合 SM2 签名）。

通过配置 SM4 套件，信创邮件系统可在传输层满足国密合规，同时与使用国际标准的 MTA（如 Gmail、Outlook）通过协商降级到共同支持的加密方式——这也需要 [MTA-STS](/kb/mta-sts-guide.html) 或 [DANE](/kb/dane-smtp.html) 支持密码套件优先级宣告。

### 3.2 邮件内容加密（S/MIME）

传统 S/MIME 使用 RSA 或 ECDH 进行密钥交换，使用 AES 进行对称加密。在信创环境中，可以使用 SM2 替代 RSA/ECDH 进行密钥封装，使用 SM4 替代 AES 进行邮件正文的对称加密。实现方式：

* 发件人使用收件人的 **SM2 公钥证书**加密一个临时密钥（内容加密密钥，CEK）。
* 使用 **SM4 算法**以该 CEK 加密邮件正文（SM4-CBC 或 SM4-GCM）。
* 在 CMS（Cryptographic Message Syntax，RFC 5652）结构中封装为 enveloppedData。

类比国际标准体系：SM2（公开密钥）+ SM4（对称加密）+ SM3（散列）的组合，相当于 RSA（公钥）+ AES（对称）+ SHA-256（散列）。

### 3.3 邮件数字签名

[S/MIME 数字签名](/kb/smime-guide.html)方面，SM3 杂凑算法可替代 SHA-256 对邮件内容生成摘要，随后使用 SM2 签名算法对摘要进行签名。验签方使用发件人 SM2 公钥证书验证签名。整套流程符合 GM/T 0010-2012《SM2 密码算法加密签名消息语法规范》的要求。

## 四、国密邮件证书体系

国密 SM4 在邮件系统中的有效应用依赖于完善的国密证书体系：

* **SM2 国密证书** — 由国密 CA 中心签发（如中国金融认证中心 CFCA、各省 CA 中心），支持 SM2/SM3 算法。
* **双证书体系** — 每用户持有签名证书和加密证书两张证书，加密证书的私钥可由密钥管理中心备份托管以支持邮件审计。
* **证书格式** — 遵循 GB/T 20518《信息安全技术 公钥基础设施 数字证书格式》，与 X.509 v3 格式兼容。

## 五、部署建议

在信创邮件系统中部署 SM4 加密时，应注意：

* 确保邮件客户端（如 Foxmail 信创版、\u56fd\u4ea7\u90ae\u4ef6\u7cfb\u7edf 信创客户端）支持 SM2/SM4 的 S/MIME 实现。
* SM4 在 SMTP 传输层和邮件内容加密层的应用需要分别配置，不可混为一谈。
* 与外部互联网邮件系统通信时，国密套件可能需要降级到 TLS 1.2 AES 或 STARTTLS——建议配置策略协商优先级。
* 参考 [信创邮件密码标准](/kb/xinchuang-email-crypto-standards.html)和 [国密邮件密码学](/kb/guomi-email-cryptography.html)的详细部署文档。

### 相关文章

* [信创邮件密码标准](/kb/xinchuang-email-crypto-standards.html)
* [国密邮件密码学](/kb/guomi-email-cryptography.html)
* [S/MIME 指南](/kb/smime-guide.html)
* [信创邮件架构设计](/kb/xinchuang-email-architecture-design.html)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/sm4-encryption-email-application.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
