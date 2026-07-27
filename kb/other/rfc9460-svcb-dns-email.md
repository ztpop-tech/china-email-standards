---
title: "RFC 9460 SVCB/HTTPS 记录：邮件服务的 DNS 发现与加密指示"
source: "https://ztpop.net/kb/rfc9460-svcb-dns-email.html"
license: CC-BY 4.0
---

# RFC 9460 SVCB/HTTPS 记录：邮件服务的 DNS 发现与加密指示

## 概述

传统上，邮件客户端要靠硬编码端口（587/993/995）与人工配置连服务器。RFC 9460 定义的 SVCB（Service Binding）记录让域名在 DNS 中权威声明"我的邮件提交/读取服务在哪、用什么参数、是否强制加密"。它是现代邮件自动化发现（autoconfig/autodiscover）与服务绑定的基础，也是 MTA-STS 之外又一层 DNS 驱动的能力。

## SVCB 结构

SVCB 记录形如：

```
_submission._tcp.example.com. 3600 IN SVCB 1 mail.example.com.
   (port=465 alpn=xmtp)
_imap._tcp.example.com.   3600 IN SVCB 1 imap.example.com.
   (port=993 alpn=imap)
```

其中 `priority`（0 为别名模式、1+ 为服务模式）、`Target` 主机、以及 SvcParams（`port`、`alpn`、`ech` 等）。客户端查 DNS 即可拿到"连哪、用什么端口、什么协议"。

## 对邮件的价值

* **服务发现**：客户端无需预置端口，按域名查 SVCB 自动定位 submission/imap/pop3 端点。
* **加密指示**：通过 `alpn` 与 `ech`（加密客户端 Hello）暗示优先隐式 TLS，配合 RFC 8314。
* **与 MTA-STS 互补**：MTA-STS 解决"服务器间传输加密"，SVCB 解决"客户端到服务器"的发现与参数，两者都基于 DNS 权威声明。

## 与 autodiscover 的关系

SVCB 把原先靠 HTTP/MX 探测的 autoconfig 流程标准化到 DNS，更可靠、更难被中间人篡改（配合 DNSSEC）。信创邮件系统可借此实现"输入域名即自动配好客户端"。

## 对信创邮件与政企的启示

信创邮件系统对外提供服务时，应在 DNS 发布 submission/imap/pop3 的 SVCB 记录，声明 465/993/995 隐式 TLS 端点，并启用 DNSSEC 防篡改；客户端支持 SVCB 后，用户配置成本降到最低，且默认走加密通道。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/rfc9460-svcb-dns-email.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
