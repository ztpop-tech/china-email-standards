---
title: "Postfix 如何配置 TLS 加密（ opportunistic vs enforced）？"
source: "https://ztpop.net/kb/postfix-tls-config.html"
license: CC-BY 4.0
---

# Postfix 如何配置 TLS 加密（ opportunistic vs enforced）？

1
Postfix 如何配置 TLS 加密（ opportunistic vs enforced）？
▼

**机会加密（opportunistic）**

Postfix 默认 smtpd\_tls\_security\_level=may、smtp\_tls\_security\_level=may：对端支持 STARTTLS 就加密，不支持就明文。目标是“尽量加密”而非强制，保证互通性。

**强制加密（enforced）**

设为 encrypt（或 dane/mta-sts）后，与对端必须成功 TLS 才投递，否则拒绝；适合内部或已知对端。需配好证书（公钥+链）与协议/密码套件白名单。

**证书与参数**

用 smtpd\_tls\_cert\_file / smtpd\_tls\_key\_file 指定证书；smtpd\_tls\_protocols=!SSLv2,!SSLv3,!TLSv1,!TLSv1.1 禁用弱协议；并开启 TLS 日志观察握手情况。

**注意**

机会加密下攻击者可在中途剥离 STARTTLS（STRIPTLS）；对高安全域应升级到 MTA-STS/DANE 强制，而非仅靠 may。

参考：Postfix TLS README（TLS\_README）；RFC 3207（STARTTLS）；RFC 8461（MTA-STS）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/postfix-tls-config.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
