---
title: "Autocrypt 是什么，和普通 PGP / S/MIME 端到端加密有何不同？"
source: "https://ztpop.net/kb/autocrypt-end-to-end-encryption.html"
license: CC-BY 4.0
---

# Autocrypt 是什么，和普通 PGP / S/MIME 端到端加密有何不同？

1
Autocrypt 是什么，和普通 PGP / S/MIME 端到端加密有何不同？
▼

**与传统 PGP/S-MIME 的区别**

PGP 与 S/MIME 端到端加密长期卡在「手动交换公钥、管理密钥环」的高门槛。Autocrypt 把密钥发现与发布自动化：客户端把公钥随邮件头的 Autocrypt 头字段附带发出，收件方客户端自动学会对方公钥，首次即可加密回复，无需用户干预密钥交换。

**密钥轮换与恢复**

Autocrypt 引入「密钥八卦（gossip）」：当 A 与 C 都和 B 通信时，A 从 B 处也能学到 C 的密钥，降低单点丢失密钥的风险；并定期轮换密钥、用「prefer-encrypt=mutual」提示双向加密偏好。它仍基于 OpenPGP 标准，不另造密码学。

**局限**

Autocrypt 只解决密钥分发，不解决元数据保护（主题、收件人仍明文），也不防服务端持久化；它面向「机会性加密」而非强匿名。对合规强加密场景，仍需 S/MIME 或受管 PGP 体系。它追求的是「默认可用」而非「默认完美」。

参考：Autocrypt 规范（autocrypt.org）、OpenPGP（RFC 4880）、与 S/MIME（RFC 8551）对比。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/autocrypt-end-to-end-encryption.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
