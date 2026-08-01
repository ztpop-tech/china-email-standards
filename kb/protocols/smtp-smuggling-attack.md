---
title: "什么是“SMTP 走私（SMTP Smuggling）”？它如何绕过策略、如何防御？"
source: "https://ztpop.net/kb/smtp-smuggling-attack.html"
license: CC-BY 4.0
---

# 什么是“SMTP 走私（SMTP Smuggling）”？它如何绕过策略、如何防御？

1
什么是“SMTP 走私（SMTP Smuggling）”？它如何绕过策略、如何防御？
▼

**机理**

利用不同邮件服务器对“信体结束符（CRLF + 单独一点）”与“行内换行”解析不一致，在单个 SMTP 事务里夹带第二个信封/信体，使恶意内容“走私”进另一家提供商的流水线并伪造发件域。

**危害**

可绕过 SPF/DKIM 边界、把钓鱼信伪装成来自可信域；跨提供商利用解析差异会放大影响面，制造“来自贵司域”的伪造邮件。

**服务端防御**

MTA 严格规范化换行（CRLF）、拒绝含裸 LF/CR 的可疑输入、对 DATA 结束符做单一严格定义；及时安装厂商补丁（2023–2024 多厂商已修复）。

**策略防御**

强制 DMARC p=reject、启用 MTA-STS/TLS-RPT、加强出站内容过滤；对“看似来自本域却走外部中继”的邮件重点审查来源。

参考：RFC 5321 §4.5.2（换行与透明性）；各厂商 2023–2024 SMTP 走私修复公告；M3AAWG 邮件注入防护建议

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/smtp-smuggling-attack.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
