---
title: "RFC 8616 解读：国际化邮件（EAI）下的 SPF/DKIM/DMARC 认证机制"
source: "https://ztpop.net/kb/rfc8616-eai-email-authentication.html"
license: CC-BY 4.0
---

# RFC 8616 解读：国际化邮件（EAI）下的 SPF/DKIM/DMARC 认证机制

## 概述

国际化邮件（Email Address Internationalization, EAI，又称 UTF-8 邮件）允许邮件地址与域名使用非 ASCII 字符：域名可呈现为 U-label（Unicode 标签，如"例子.测试"），邮箱本地部分也可含 UTF-8 字符。SPF（RFC 7208）、DKIM（RFC 6376）、DMARC（RFC 7489）原本都假设域名是纯 ASCII，当邮件中出现国际化域名时，究竟是应该用 U-label 还是 A-label（punycode，形如 xn--…）写入 DNS 与认证标识符，便产生歧义。RFC 8616（2019 年 6 月，Standards Track，更新 6376/7208/7489）正是为这三套机制澄清国际化邮件下的表示规则。

## 通用原则

RFC 8616 首先明确两条基线：

* **DNS 中的域名必须保持 ASCII**：因为 DNS 客户端无法预知对方期望 EAI 还是 ASCII 结果，所有存入 DNS 记录（SPF、DKIM 密钥、DMARC 策略）的域名都必须是 A-label；当邮件信头中的域名含 U-label 时，先转换为 A-label 再做 DNS 查询（遵循 RFC 5891）。
* **信头文本可含 U-label**：邮件信头字段里原本限定 ASCII 的域名可以呈现为 U-label，邮箱本地部分可为 UTF-8；但仅供机器解析的字段名等仍保持 ASCII。

## SPF 与国际化邮件

SPF 使用 SMTP 会话中的两个身份：EHLO 命令的主机名，以及 MAIL FROM 命令地址中的域名。关键约束：

* EHLO 主机名**必须**用 A-label——因为 EHLO 出现在服务器告知是否支持 SMTPUTF8 扩展之前，无法使用 U-label。
* MAIL FROM 中的国际化域名可为 U-label 或 A-label；但在做 SPF 校验前，所有 U-label 都必须转换为 A-label（包括原始 DNS 查找名与宏展开中的域名）。
* SPF 宏 %{s} 与 %{l} 展开发件人本地部分；若本地部分含非 ASCII 字符，相关宏因无法匹配 DNS 标签而不命中——实践中这些宏很少用，影响有限。

## DKIM 与国际化邮件

DKIM 在签名头与 DNS 密钥记录中处理域名：

* dkim-quoted-printable 的定义被放宽：在国际化信头消息中，非 ASCII 的 UTF-8 字符无需再 quoted-printable 编码（ABNF 的 dkim-safe-char 扩展纳入 UTF8-2/3/4）。
* DKIM-Signature 头中 d=（域）、i=（身份）、s=（选择器）标签的 IDN，原本要求必须为 A-label；RFC 8616 放宽——仅在国际化信头字段中允许表示为 U-label（A-label 仍合法以兼容旧软件），与其他信头字段保持一致。
* 计算或验证 DKIM 签名哈希时，必须使用域名在信头字段中出现的原始格式。

## DMARC 与国际化邮件

由于 DMARC 当时尚非 Standards Track 协议，RFC 8616 对其给出"建议"而非强制要求：

* RFC 5322.From 地址域中的 U-label，在进一步处理前**必须**转换为 A-label（更新 RFC 7489 第 6.6.1 与 7.1 节）。
* DMARC 策略记录（rua/ruf 标签）中的邮箱地址仍须为传统 ASCII 地址——因为同一条策略记录可能被国际化邮件与传统邮件共用。

## 安全考量

RFC 8616 本身不引入新的威胁，其目标是让 SPF/DKIM/DMARC 在国际化邮件上的表现与 ASCII 邮件同样可靠，从而使依赖它们的垃圾与钓鱼过滤系统也能稳定工作于国际化邮件。简言之：正确序列化域名，是邮件认证在多语言环境下不失灵的前提。

## 对信创邮件与多语言环境的启示

信创邮件系统常需服务含中文域、中文邮箱名的多语言环境。实现时必须：在写入 DNS 的 SPF/DKIM/DMARC 记录中一律使用 A-label（xn--）；在信头展示与哈希计算时保持与 RFC 8616 一致的 U/A-label 处理；邮件安全网关与认证组件需能正确转换并比对两种标签，避免"同一域名因表示形式不同被判为不匹配"的误拦或漏放。这与 MTA-STS、TLS-RPT 等同样依赖 DNS 的机制的标签处理需一并纳入联调。

### 相关主题

* [SPF 部署与排错](/kb/spf-guide.html)：10 次 DNS 查询上限与 soft/hard fail
* [DKIM 密钥管理与轮换](/kb/dkim-guide.html)：2048 位密钥与多选择器平滑切换
* [DMARC 完全指南](/kb/dmarc-guide.html)：从 p=none 到 p=reject 的部署路径
* [SMTPUTF8 与 EAI 部署](/kb/smtp-utf8-eai-deployment.html)：UTF-8 邮件的端到端落地
* [国际化邮件（EAI）概述](/kb/eai-internationalized-email.html)：U-label 与 A-label 的基础
* [MTA-STS 部署指南](/kb/mta-sts-guide.html)：同样依赖 DNS 的标签一致性

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/rfc8616-eai-email-authentication.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
