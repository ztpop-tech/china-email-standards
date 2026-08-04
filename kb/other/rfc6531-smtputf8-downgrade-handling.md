---
title: "RFC 6531 SMTPUTF8 扩展如何支持国际化邮件地址？回复码怎么处理？"
source: "https://ztpop.net/kb/rfc6531-smtputf8-downgrade-handling.html"
license: CC-BY 4.0
---

# RFC 6531 SMTPUTF8 扩展如何支持国际化邮件地址？回复码怎么处理？

1
RFC 6531 SMTPUTF8 扩展如何支持国际化邮件地址？回复码怎么处理？
▼

**扩展框架的十一条定义（§3.1）**

RFC 6531 以标准 ESMTP 扩展框架定义国际化邮件，要点如下：

* 服务扩展名为 “Internationalized Email”，**EHLO 关键字为 `SMTPUTF8`**。
* **该 EHLO 关键字不定义任何参数值**；为给未来扩展留余地，EHLO 响应中 MUST NOT 为该关键字附带参数，而支持 SMTPUTF8 的客户端 MUST 忽略出现的任何参数（表现得如同参数不存在）。服务器一旦在 EHLO 响应中列出 SMTPUTF8，就 MUST 完全符合本规范。
* 为 `MAIL` 命令新增一个**不接受取值**的可选参数 `SMTPUTF8`。该参数出现即表示客户端具备 SMTPUTF8 能力，并**断言**：信封含非 ASCII 地址、或该邮件是国际化邮件、或该邮件需要 SMTPUTF8 支持。
* `MAIL` 命令行最大长度**增加 10 个字符**以容纳该参数。
* `VRFY` 与 `EXPN` 也新增同名无值可选参数，表示客户端可接受回复中出现 UTF-8 编码的 Unicode 字符。
* **不定义任何新的 SMTP 动词。**
* **提供该扩展的服务器 MUST 支持并通告 8BITMIME 扩展（RFC 6152）。**
* `MAIL` 与 `RCPT` 的 reverse-path 和 forward-path 被扩展，允许邮箱名（地址）中出现 UTF-8 编码的 Unicode 字符；邮件正文按 RFC 6532 扩展。
* 该扩展在**提交端口（RFC 6409）有效，也可用于 LMTP（RFC 2033）**。

**与 8BITMIME 的关系（§3.6）**

`SMTPUTF8` 参数只是「断言」，**带该参数发出的邮件仍有可能实际上并非国际化邮件**。需要准确判断的客户端或服务器必须解析全部邮件头字段与正文中的 MIME 头字段（RFC 2045），但**本规范并不要求实现去检视邮件内容**。另外，虽然规范要求 SMTPUTF8 服务器支持 8BITMIME 以确保具备 8 位数据处理能力，**但并不要求 MIME 报文中必须存在非 ASCII 正文部分**。SMTPUTF8 可与 `BODY=8BITMIME` 同用，或在服务器通告 BINARYMIME（RFC 3030）时与 `BODY=BINARYMIME` 同用。

**U-label 与 A-label 的取舍规则（§3.7）**

邮件传输过程中除 MAIL/RCPT 外还有多处涉及地址与域名。总规则是：**RFC 5321 中规定为 mailbox 之处，本扩展要求整串使用 UTF-8 形式；RFC 5321 中规定为域名之处，若支持 SMTPUTF8 则国际化域名 SHOULD 用 U-label 形式，否则 SHOULD 用 A-label 形式。**

一个关键例外在 §3.7.1：SMTP 连接建立后服务器发 220 问候，客户端随即发 EHLO，而**客户端在收到 EHLO 响应之前无从得知服务器是否支持 SMTPUTF8**，因此支持 SMTPUTF8 的客户端 **MUST 在 EHLO 命令中只发送 ASCII 域名（LDH label 或 A-label，见 RFC 5890）**；服务器若在 EHLO 响应中给出域名，同样 MUST 使用 LDH label 或 A-label。§3.7.2 进一步讨论 MX（Mail eXchangers）场景下的对应处理。

**回复码的国际化处理**

规范对若干回复码作了明确约束：

* 当命令要求 ASCII 地址而实际给出非 ASCII 地址时，返回 **`550`**；与「邮箱名不被允许」语义相关的场景返回 **`553`**。
* 对 `251` 与 `551` 这两个会携带转发邮箱地址的回复码：**服务器 MUST NOT 返回含非 ASCII 邮箱的 251 或 551 响应**，而必须将其转换为对应的 **`250` 或 `550`** 响应。客户端也必须能够处理这一转换。
* 在相关校验场景下，服务器 MUST 使用 **`252`** 或 **`550`**。其中 252 的语义是「无法校验用户，但会接受该邮件并尝试投递」。
* SMTPUTF8 服务器 **MUST NOT 在不含非 ASCII 地址的场合擅自引入非 ASCII 字符**；规范另为无法轻松阅读非 ASCII 信息的日志读取者保留了相应考量。

参考：RFC 6531《SMTP Extension for Internationalized Email》，https://www.rfc-editor.org/rfc/rfc6531 —— 章节 3.1 / 3.6 / 3.7 / 3.7.1 / 3.7.2 及回复码相关条款

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/rfc6531-smtputf8-downgrade-handling.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
