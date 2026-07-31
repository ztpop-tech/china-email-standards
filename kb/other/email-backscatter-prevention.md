---
title: "什么是“退信反弹（Backscatter）”？邮件系统如何防止被利用成垃圾放大器？"
source: "https://ztpop.net/kb/email-backscatter-prevention.html"
license: CC-BY 4.0
---

# 什么是“退信反弹（Backscatter）”？邮件系统如何防止被利用成垃圾放大器？

1
什么是“退信反弹（Backscatter）”？邮件系统如何防止被利用成垃圾放大器？
▼

**定义**

Backscatter 指“服务器给伪造发件人（其实是受害者）发送退信/DSN”，当垃圾邮件冒用他人地址时，受害者收到海量退信——既骚扰又暴露你为“开放退信源”。

**成因**

对“信封发件人可伪造”的来信，若接收后校验失败才退信，退信会发往伪造地址；攻击者用你的服务器向受害者“借刀杀人”发噪声。

**防护**

① 收信阶段早拒绝（SMTP 对话内 5xx 拒收，不退信）；② 仅对通过 SPF/DKIM/白名单的可信发件人发 DSN；③ 对无法验证的失败“静默丢弃”而非退信；④ BATV/发信签名校验入站退信。

**实践**

网关/MTA 默认“对话内拒收 > 事后退信”；出站退信也要鉴别真伪（SRS/BATV），避免在风暴中被拉黑。

参考：RFC 3464（DSN 规范，退信来源）；M3AAWG 反 Backscatter 建议

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-backscatter-prevention.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
