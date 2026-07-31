---
title: "SMTP ETRN 命令（RFC 1985）是什么？拨号/动态 IP 主机如何用它对列刷新？"
source: "https://ztpop.net/kb/smtp-etrn.html"
license: CC-BY 4.0
---

# SMTP ETRN 命令（RFC 1985）是什么？拨号/动态 IP 主机如何用它对列刷新？

1
SMTP ETRN 命令（RFC 1985）是什么？拨号/动态 IP 主机如何用它对列刷新？
▼

**背景**

早期很多邮件服务器位于拨号或动态 IP，平时不在线或无法被反向解析，发送方只能把发往它的邮件排队等待。RFC 1985 的 ETRN 让这类主机上线后主动触发队列刷新。

**机制**

主机连上自己域的 SMTP 服务器（或中继）发 ETRN ，要求对方立即尝试投递排队中发往该域的邮件，避免被动等待重试周期。

**价值**

动态 IP/拨号邮件系统上线即收信，无需漫长重试；也可用于“按需拉取”场景（如分支办公室定时收信），只触发不传输。

**注意**

ETRN 本身不传邮件，只是触发；接收方仍需有到该域的有效 MX/路由。现代固定 IP 环境用得少，但仍是标准扩展。

参考：RFC 1985（SMTP Service Extension for Remote Message Queue Starting）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/smtp-etrn.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
