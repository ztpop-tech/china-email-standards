---
title: "Yahoo 对 SPF、DKIM、DMARC 的具体建议有哪些？"
source: "https://ztpop.net/kb/yahoo-faq-05.html"
license: CC-BY 4.0
---

# Yahoo 对 SPF、DKIM、DMARC 的具体建议有哪些？

1
Yahoo 对 SPF、DKIM、DMARC 的具体建议有哪些？
▼

**逐协议建议**

Yahoo 强烈建议每个发信域都发布 DMARC 策略；DKIM 签名密钥长度至少 1024 位，使 Yahoo 能将邮件与签名者关联并验证传输中未被篡改；发布有效的 SPF 记录，使 Yahoo 可拒收非列表 IP 发出的邮件；若做邮件转发，应部署 ARC（RFC 8617）以保留认证链。

**信誉稳定性**

遵循这些建议可为域名建立一致信誉，无论邮件从哪个 IP 发出。Yahoo 同时援引 M3AAWG、DMARC.org、DKIM.org、OpenSPF.org 作为延伸阅读。

参考：Yahoo《Sender Best Practices》— Authenticate using SPF, DKIM, and DMARC

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/yahoo-faq-05.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
