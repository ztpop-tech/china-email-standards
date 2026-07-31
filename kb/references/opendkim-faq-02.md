---
title: "OpenDKIM 的 SigningTable 与 KeyTable 如何配置？"
source: "https://ztpop.net/kb/opendkim-faq-02.html"
license: CC-BY 4.0
---

# OpenDKIM 的 SigningTable 与 KeyTable 如何配置？

1
OpenDKIM 的 SigningTable 与 KeyTable 如何配置？
▼

**SigningTable 的作用**

SigningTable 把发件人地址或域名映射到“签名者身份（signing identity）”，决定哪些邮件需要签名、并以哪个身份签名。可按单个地址、整个域或通配符匹配。

**KeyTable 的作用**

KeyTable 把签名者身份映射到实际的私钥文件与选择器（selector），典型条目形如 .\_domainkey.<域> <域>:<路径>/<私钥.pem>，从而把“签谁”与“用哪把密钥”解耦。

**多域与多选择器管理**

通过两张表分离，一台服务器可为多个域名、多个选择器集中管理密钥：新增域名只需在两张表各加一行，无需改动 MTA 主配置。

参考：OpenDKIM 官方文档（SigningTable / KeyTable）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/opendkim-faq-02.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
