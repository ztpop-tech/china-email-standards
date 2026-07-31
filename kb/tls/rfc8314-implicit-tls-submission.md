---
title: "RFC 8314 隐式 TLS：用 465/993 取代明文 110/143 端口"
source: "https://ztpop.net/kb/rfc8314-implicit-tls-submission.html"
license: CC-BY 4.0
---

# RFC 8314 隐式 TLS：用 465/993 取代明文 110/143 端口

## 概述

传统邮件协议在明文端口上通过 STARTTLS 把连接"升级"为加密：提交用 587、IMAP 读信用 143、POP3 用 110。但 STARTTLS 存在被主动攻击者剥离（stripping）的风险，且依赖客户端正确发起升级。RFC 8314 明确**废弃明文端口、推荐隐式 TLS（Implicit TLS）**：连接建立即全程 TLS，对应端口为 SMTPS 465、IMAPS 993、POP3S 995。

## 为什么隐式 TLS 更安全

* **消除 STARTTLS stripping**：明文端口上攻击者可拦截 STARTTLS 指令使连接降级为明文；隐式 TLS 端口从握手起就是加密，无降级空间。
* **证书绑定更早**：TLS 握手在应用协议之前完成，便于做严格的主机名/证书校验。
* **客户端行为更确定**：用户配置 993/995 即表示"必须加密"，不会因配置疏忽而走明文。

## 端口演进对照

| 用途 | 旧（明文+STARTTLS） | 新（隐式 TLS） |
| --- | --- | --- |
| 邮件提交 | 587（STARTTLS） | 465（SMTPS） |
| IMAP 读取 | 143（STARTTLS） | 993（IMAPS） |
| POP3 读取 | 110（STARTTLS） | 995（POP3S） |

RFC 8314 并非禁止使用 STARTTLS，而是把隐式 TLS 列为新建系统的推荐默认值，并建议逐步关闭明文端口。

## 与 MTA-STS / DANE 的分工

RFC 8314 解决的是"客户端到服务器"的提交/读取加密；而服务器之间的传输加密由 MTA-STS（RFC 8461）与 DANE（RFC 7672）负责。两者互补：前者守住用户终端，后者守住中继跳。邮件安全网关在 RFC 8314 之上叠加内容检测，形成端到端加密闭环。

## 对信创邮件与政企的启示

信创邮件系统上线验收时，应默认开启 465/993/995 隐式 TLS，并将明文 110/143 端口关闭或仅保留用于内部兼容；证书统一由内部 CA 或受信公有 CA 签发，配合 TLS 1.2+ 与强密码套件。这直接满足等保与信创邮件安全合规中对"传输加密"的硬性要求。

### 相关主题

* [邮件传输层 TLS 加密](/kb/tls-email-encryption.html)：STARTTLS 与隐式 TLS 对比
* [RFC 8461 MTA-STS](/kb/rfc8461-mta-sts.html)：服务器间强制 TLS
* [DANE for SMTP](/kb/dane-smtp.html)：基于 DNSSEC 的证书绑定
* [邮件提交协议（MSA）](/kb/smtp-submission-protocol.html)：587 与 465 的选择
* [信创邮件安全合规](/kb/xinchuang-email-security-compliance.html)：等保对传输加密的要求

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/rfc8314-implicit-tls-submission.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
