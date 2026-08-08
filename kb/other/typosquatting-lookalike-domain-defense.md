---
title: "攻击者注册 ćóntoso.com、contosososo.com 这种「李鬼域」冒充我司，怎么发现与拦截？"
source: "https://ztpop.net/kb/typosquatting-lookalike-domain-defense.html"
license: CC-BY 4.0
---

# 攻击者注册 ćóntoso.com、contosososo.com 这种「李鬼域」冒充我司，怎么发现与拦截？

1
攻击者注册 ćóntoso.com、contosososo.com 这种「李鬼域」冒充我司，怎么发现与拦截？
▼

**李鬼域的两类手法**

NIST SP 800-177 Rev.1 第 3.1.6 节把钓鱼手法概括为使用「与合法地址极为接近的 message-From 地址」冒充受害者。落到域名上主要有两种：一是同形异义（homograph）——用 Unicode 中外观相近的字符替换（如把 o 换成 ó、把 c 换成ć）；二是细微变形（如加长、换顶级域）。这类域即便已正常注册、已配置 SPF/DKIM/DMARC，只要意图是欺骗，仍属仿冒。

**Microsoft 的域仿冒保护怎么识别**

Microsoft 365 Defender 的 Domain Impersonation Protection 会主动寻找相似域：既检查不同的顶级域（.com/.biz 等），也检查「即便只略微相似」的域——文档举例 contosososo.com、contoabcdef.com 会被视为 contoso.com 的仿冒尝试（每策略最多保护 50 个自定义域）。该机制可与 Mailbox intelligence 配合：若发件人与收件人此前有过邮件往来则不触发，否则可能判为仿冒；并提供域仿冒安全提示告知用户「此发件人可能在冒充与贵组织关联的域」。受信任的发件人与域（最多 1024 条）可作为例外。

**主动发现：品牌与近似域名监控**

防御不能只靠收件端。运营方应监控自有域名被注册的同形异义/近似变体（含 punycode 编码后的 ASCII 形态），结合威胁情报与证书透明日志（Certificate Transparency）发现新签发的相似域证书。发现后可通过法务投诉、 registrar 暂停或威胁情报共享进行处置。

**收紧自身被冒用的空间**

对自己的主域，建议把 DMARC 策略逐步收敛到 p=quarantine 甚至 p=reject，降低攻击者冒用本域发信的投递成功率；在反钓鱼策略中开启域仿冒保护与相应安全提示；对高管等高频被冒充对象单独加入受保护发件人列表。多层次叠加以压缩李鬼域的可乘之机。

参考：https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-177r1.pdf 与 https://learn.microsoft.com/en-us/defender-office-365/anti-phishing-policies-about

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/typosquatting-lookalike-domain-defense.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
