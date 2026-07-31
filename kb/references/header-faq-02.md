---
title: "Received 头里的 from / by / with / for / id / date 各代表什么？"
source: "https://ztpop.net/kb/header-faq-02.html"
license: CC-BY 4.0
---

# Received 头里的 from / by / with / for / id / date 各代表什么？

1
Received 头里的 from / by / with / for / id / date 各代表什么？
▼

**from**

表示这“一跳”的连接来源：通常是上一跳的 hostname 与 IP（如 from mail.relay.example [203.0.113.9]）。出现括号里的 IP 是 TCP 连接的对端地址，是判断真实来源的重要依据。

**by**

表示“接收这一跳”的服务器自身（如 by mx.corp.cn with ESMTPS）。说明是谁收下了这封邮件。

**with**

表示使用的传输协议（如 with ESMTP / ESMTPS / SMTPUTF8）。带 S 通常指启用了 TLS 加密传输。

**for**

表示信封收件人（Return-Path 指定的收件地址，即 RCPT TO），不一定等于邮件正文里看到的 To。

**id / date**

id 是该服务器给邮件的本地队列/Message-ID；date 是这一跳接收时打的时间戳，可用于核对各跳时间是否连续合理。

参考：RFC 5321 第 4.4 节（Received 头字段语法）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/header-faq-02.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
