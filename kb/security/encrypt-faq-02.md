---
title: "S/MIME 是什么？它如何对邮件加密与签名？"
source: "https://ztpop.net/kb/encrypt-faq-02.html"
license: CC-BY 4.0
---

# S/MIME 是什么？它如何对邮件加密与签名？

1
S/MIME 是什么？它如何对邮件加密与签名？
▼

**定义**

S/MIME（Secure/Multipurpose Internet Mail Extensions）是一套基于 PKI 的邮件安全标准，最新版本为 S/MIME 4.0（RFC 8551）。它用 X.509 证书中的公钥/私钥对邮件做加密（机密性）和数字签名（完整性+不可抵赖）。

**加密流程**

发件人用收件人的 X.509 证书公钥加密会话密钥，再用该会话密钥加密邮件正文；收件人用自己的私钥解出会话密钥进而还原明文。无需双方预先共享密码。

**签名流程**

发件人用自己证书的私钥对邮件摘要签名，收件人用发件人证书公钥验证，从而确认邮件确实来自该证书持有者且未被篡改，并显示“已签名”标识。

参考：RFC 8551（S/MIME 4.0）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/encrypt-faq-02.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
