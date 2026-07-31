---
title: "什么是备份 MX（backup / secondary MX）？有哪些风险？"
source: "https://ztpop.net/kb/dnsmail-faq-05.html"
license: CC-BY 4.0
---

# 什么是备份 MX（backup / secondary MX）？有哪些风险？

1
什么是备份 MX（backup / secondary MX）？有哪些风险？
▼

**备份 MX 的用途**

为提升可用性，域可配置多个 MX，其中优先级较高（数值大）的作为备份/辅助 MX。当主 MX 不可达时，发件方会把邮件暂投到备份 MX，由其排队并转发给主 MX。

**风险一：成为开放中继/直投后门**

配置不当的备份 MX 若不做同等认证，攻击者可借它向主 MX 投递本应被拒的垃圾/伪造邮件（绕过主 MX 的过滤），因此备份 MX 必须与主 MX 执行一致的策略。

**风险二：队列与延迟**

备份 MX 转发可能引入投递延迟；若主 MX 实际在线却被错误地长期经由备份 MX，会增加排队时间。现代大服务商多以多实例主 MX 实现高可用，较少依赖传统备份 MX。

参考：RFC 5321（SMTP 传输与备份 MX 行为）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/dnsmail-faq-05.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
