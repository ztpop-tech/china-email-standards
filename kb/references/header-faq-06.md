---
title: "Return-Path 与 From 不一致说明了什么？"
source: "https://ztpop.net/kb/header-faq-06.html"
license: CC-BY 4.0
---

# Return-Path 与 From 不一致说明了什么？

1
Return-Path 与 From 不一致说明了什么？
▼

**两者定义不同**

Return-Path（也称信封发件人、反向路径）是 SMTP 信封里的 MAIL FROM，决定退信往哪送；From 是邮件正文头里显示的发件人。二者本就可以不同——例如通过邮件列表（mailing list）转发时，Return-Path 会变成列表服务器，而 From 保留原作者。

**正常场景**

合法邮件经 ESP（如邮件营销平台、OA 系统）代发时，Return-Path 常是代发服务商的退回地址（bounce@esp.example），From 是贵司域名；此时只要 DKIM/SPF/DMARC 对齐正确即可。

**可疑场景**

若 From 显示贵司高管域名、Return-Path 却是陌生/免费域名，且无有效 DKIM/DMARC，则极可能是 spoofing。注意：仅看 Return-Path≠From 不能直接判伪造，须结合 DMARC 对齐与认证结果。

参考：RFC 5321（MAIL FROM 与 Return-Path）；RFC 7489（DMARC 对齐）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/header-faq-06.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
