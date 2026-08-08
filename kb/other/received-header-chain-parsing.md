---
title: "Received 头链应该怎么逐跳解析？哪一跳的信息可以采信？"
source: "https://ztpop.net/kb/received-header-chain-parsing.html"
license: CC-BY 4.0
---

# Received 头链应该怎么逐跳解析？哪一跳的信息可以采信？

1
Received 头链应该怎么逐跳解析？哪一跳的信息可以采信？
▼

**Received 行是谁写上去的**

RFC 5321 第 4.4 节（Trace Information）规定：当 SMTP 服务器收到一封待投递或待进一步处理的邮件时，**必须**在邮件内容的开头插入追踪信息，即时间戳行（Received 行）。同节还给出了三条硬约束：互联网邮件程序**不得**更改或删除此前已被加入邮件头的 Received 行；SMTP 服务器**必须**把 Received 行前置（prepend）；**不得**改变已有各行的顺序，也**不得**把 Received 行插入到其他位置。这三条决定了解析方法：邮件头中**最上面的 Received 是最后一跳，最下面的是最早一跳**。

**各子句的规范含义**

同样在 RFC 5321 第 4.4 节：FROM 子句在 SMTP 环境下**必须**提供，且**应当**同时包含两项内容——(1) 源主机在 EHLO 命令中自报的名字，(2) 一个地址字面量，内含**由 TCP 连接确定的**源 IP 地址。ID 子句**可以**按 RFC 822 的建议包含一个 @，但不作要求。FOR 子句若出现，则**必须**只含一个 path 条目，即使此前给出了多条 RCPT 命令——多个 path 会带来安全问题，已被废弃（见第 7.2 节）。RFC 5322 第 3.6.7 节（Trace Fields）从消息格式角度给出语法：trace 由可选的 Return-Path 加一个或多个 Received 组成，Received 的形式是若干 token 后跟一个分号与一个 date-time。

**关键判据：EHLO 名可伪造，TCP 层 IP 不可**

FROM 子句里的两项信息可信度截然不同：EHLO 名字是对端自报的字符串，谁都能填；地址字面量则由本机 TCP 连接直接观测得到。**因此追踪来源时应以本方基础设施写下的那一跳的地址字面量为准，而不是以对端自报的主机名为准。**由于第 4.4 节禁止修改已有 Received 行，任何在你的边界服务器之外产生的 Received 行都可能是攻击者预先伪造后随邮件带入的——它们在语法上完全合法，但在证据链上不可采信。**可信边界就是「本组织控制的第一台接收主机」写下的那一行。**

**时间字段的读法**

第 4.4 节明确：随着互联网的增长，Received 头字段之间的可比性对发现问题（尤其是慢速中继）很重要，因此生成 Received 头的服务器**应当**在日期中使用显式的时区偏移（例如 -0800），而不是任何形式的时区名称；在可行时**应当**使用带偏移的本地时间而非 UT。若确实需要提供时区名称，**应当**把它放在注释里。排查投递延迟时，把相邻两跳的 date-time 换算到同一基准做差，即可定位是哪一跳耗时。

**Return-Path 与 Received 的区别**

第 4.4 节还规定：当投递 SMTP 服务器做「最终投递」时，会在邮件数据开头插入一行 return-path，这一用法是必需的，邮件系统**必须**支持。Return-Path 保存的是 MAIL 命令中的反向路径信息，其首要用途是指定退信与故障通知的接收地址。同节指出，投递时**应当**恰好只存在一条 return path；转发、网关或中继系统**可以**移除并按需重建，以保证最终只出现一条。**因此 Return-Path 反映的是信封发件人，与邮件头中显示给用户的 From 不是一回事。**

参考：https://www.rfc-editor.org/rfc/rfc5321.txt 与 https://www.rfc-editor.org/rfc/rfc5322.txt

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/received-header-chain-parsing.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
