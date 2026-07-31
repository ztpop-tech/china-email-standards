---
title: "为什么 SPF、DKIM、DMARC 要一起部署，而不是只上其中一个？"
source: "https://ztpop.net/kb/mailops-faq-08.html"
license: CC-BY 4.0
---

# 为什么 SPF、DKIM、DMARC 要一起部署，而不是只上其中一个？

1
为什么 SPF、DKIM、DMARC 要一起部署，而不是只上其中一个？
▼

**各自角色**

**SPF** 验证信封域的发送主机授权；**DKIM** 用签名保证邮件内容未被篡改且来自持有私钥的域；**DMARC** 基于前两者做“对齐”策略，并规定失败时的处置（none/quarantine/reject）与汇总报告。

**协同**

单独 SPF 在转发时易失效；单独 DKIM 不约束 From 显示域；只有三者配合，才能既防冒用、又能在失败时统一处置与获得可见性。详见我们的 [部署检查清单](/kb/spf-dkim-dmarc-checklist.html)。

参考：RFC 7208(SPF) / RFC 6376(DKIM) / RFC 7489(DMARC)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/mailops-faq-08.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
