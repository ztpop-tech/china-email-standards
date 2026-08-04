---
title: "国际化邮件（RFC 8616）下 SPF/DKIM/DMARC 认证如何处理？"
source: "https://ztpop.net/kb/rfc8616-eai-authentication.html"
license: CC-BY 4.0
---

# 国际化邮件（RFC 8616）下 SPF/DKIM/DMARC 认证如何处理？

1
国际化邮件（RFC 8616）下 SPF/DKIM/DMARC 认证如何处理？
▼

**背景与原则**

§1/2：国际化邮件(EAI, RFC 6530)允许 SMTP 会话(RFC 6531)与信头(RFC 6532)使用 U-label，且 local-part 可为 UTF-8；但 DNS 记录始终为 ASCII，因为无法判断取记录的客户端期望 EAI 还是 ASCII 结果。信头中的域名在查 DNS 前须由 U-label 转为 A-label（RFC 5891）。

**SPF 与国际化邮件**

§4：SPF 使用 EHLO 主机名与 MAIL FROM 域两个身份。EHLO 在服务器声明是否支持 SMTPUTF8 之前发出，故 IDN 主机名 MUST 为 A-label；MAIL FROM 中的 IDN 可为 U-label 或 A-label。所有 U-label 在 SPF 校验前 MUST 转为 A-label（含原始查找名与 macro 扩展中的域名）。若 local-part 含非 ASCII，含 `%{s}`/`%{l}` 的宏因无法作为 DNS label 而不匹配任何项。

**DKIM 与国际化邮件**

§5：RFC 6376 原要求 `d=`/`i=`/`s=` 中的 IDN 必须为 A-label；本规定在国化信头中放宽为 SHOULD 用 U-label（A-label 仍有效以兼容旧软件）。dkim-quoted-printable 的定义被修改，使非 ASCII UTF-8 字符不必 quoted。计算/验证 DKIM 哈希时 MUST 用信头中实际出现的域名格式；DKIM 密钥记录本身不含域名，规范不变。

**DMARC 与国际化邮件**

§6：RFC 7489 §6.6.1 对 From 域 IDN 的处理被更新为“所有 U-label 先转为 A-label 再处理”，§7.1 同样更新。DMARC 策略记录（§6.3/7.1）的 `rua`/`ruf` 地址因须同时服务国化与传统邮件，**仍须为传统 ASCII 地址而非国化地址**。§8 指出这些更新旨在让认证在国化邮件上与 ASCII 邮件同样可靠。

参考：RFC 8616（Email Authentication for Internationalized Mail），https://www.rfc-editor.org/rfc/rfc8616 —— 章节 1 / 2 / 4 / 5 / 6 / 8（注：REQUIRETLS 实为 RFC 8689，本篇按 RFC 8616 真实主题撰写）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/rfc8616-eai-authentication.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
