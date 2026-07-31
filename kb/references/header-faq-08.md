---
title: "常见的邮件头伪造手法与识别要点有哪些？"
source: "https://ztpop.net/kb/header-faq-08.html"
license: CC-BY 4.0
---

# 常见的邮件头伪造手法与识别要点有哪些？

1
常见的邮件头伪造手法与识别要点有哪些？
▼

**手法一：显示名伪装**

只改 From 的人名部分（见 header-faq-03），域名不变或无关；识别靠展开真实地址与 DMARC 结论。

**手法二：相似域名/同形异义字**

用 c0rp.cn、corp.co 或 Unicode 伪装域名发信；识别靠精确域名比对与 IDN 同形检测。

**手法三：Received 链篡改**

攻击者在自己发出的邮件里手动塞入伪造的 Received 头，企图让其“看起来”来自可信中继；识别靠核对最底部 Received 的 IP/时间是否自洽，以及是否有受信网关重新打标。

**手法四：DKIM 重放**

把一封合法签名的邮件原样转发给新目标，DKIM 仍 pass 但收件人并非原定对象；识别靠结合 DMARC 对齐、收件人与业务上下文。

**通用防线**

以“域名级认证（SPF+DKIM+DMARC）”为底线，配合显示名/域名人工核对与威胁情报，才是稳健的识别体系。

参考：RFC 7489（DMARC）；反钓鱼运维实务；MITRE ATT&CK T1566

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/header-faq-08.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
