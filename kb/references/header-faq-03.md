---
title: "如何识别伪造的发件人显示名（From 显示名欺骗 / Display Name Spoofing）？"
source: "https://ztpop.net/kb/header-faq-03.html"
license: CC-BY 4.0
---

# 如何识别伪造的发件人显示名（From 显示名欺骗 / Display Name Spoofing）？

1
如何识别伪造的发件人显示名（From 显示名欺骗 / Display Name Spoofing）？
▼

**什么是显示名欺骗**

攻击者把 From 头写成 “张三 ”，收件人邮件客户端往往只突出显示“张三”而把真实地址收起。用户看到的是信任的人名，实际地址却毫无关系——这属于显示名欺骗，并未伪造 SMTP 信封或真实域名。

**识别要点一：看真实地址**

永远展开/查看 From 头的完整地址，而不仅看显示名。若显示“财务部”但地址是陌生域名或 free 邮箱，即为可疑。

**识别要点二：比对域名**

将 From 地址域名与发件人所属组织的真实域名精确比对（注意相似域名如 c0rp.cn 冒充 corp.cn、使用西里尔字母伪装）。

**识别要点三：看认证结果**

即使显示名可随意填写，DMARC/DKIM/SPF 是对“域名”的认证。若邮件声称来自 corp.cn 但 dkim=pass 的域名是 evil.com，或 dmarc=fail，则显示名不可信。

参考：RFC 5322（From 头与显示名）；反钓鱼实务

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/header-faq-03.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
