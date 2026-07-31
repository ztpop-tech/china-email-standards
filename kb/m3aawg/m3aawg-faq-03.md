---
title: "为什么 DKIM 签名要与邮件头 From 域对齐？ESP 为什么要分客户密钥、双签？"
source: "https://ztpop.net/kb/m3aawg-faq-03.html"
license: CC-BY 4.0
---

# 为什么 DKIM 签名要与邮件头 From 域对齐？ESP 为什么要分客户密钥、双签？

1
为什么 DKIM 签名要与邮件头 From 域对齐？ESP 为什么要分客户密钥、双签？
▼

**对齐 From 域**

任何基于域的信誉体系都需要可靠地确认“对这封邮件负责的域”。M3AAWG 建议用与 RFC5322.From 头域对齐的 DKIM 密钥为所有外发邮件签名，并签名一组合理的头字段（参考 RFC 6376 第 5.4.1 节）。

**ESP 的双签与分客户密钥**

邮件服务商（ESP）应强烈考虑用自己的域进行“双签”，以便基于每个域名分别评估信誉；同时应为每位客户使用独立的 DKIM 密钥。此外应遵循 M3AAWG 的 DKIM 密钥轮换与避免密钥长度漏洞的最佳实践。

参考：M3AAWG《Email Authentication Recommended Best Practices》(2020-09)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/m3aawg-faq-03.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
