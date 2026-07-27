---
title: "RFC 6531 SMTPUTF8：让邮件地址与域名支持中文等非 ASCII 字符"
source: "https://ztpop.net/kb/rfc6531-smtputf8-internationalized.html"
license: CC-BY 4.0
---

# RFC 6531 SMTPUTF8：让邮件地址与域名支持中文等非 ASCII 字符

## 概述

传统 SMTP（RFC 5321）只允许 ASCII 字符，这导致中文邮箱名（如 `张涛@昆仑邮件.中国`）无法在网络中传输。RFC 6531 为 SMTP 增加 `SMTPUTF8` 扩展，配合 IETF 国际化邮件（EAI，RFC 6530 系列），使邮件地址的本地部分与域名都能携带 UTF-8 字符，实现真正的"母语邮箱"。

## 工作机制

1. 提交方在 `EHLO` 阶段声明支持 `SMTPUTF8`；
2. 发信时在 `MAIL FROM` 后附加 `SMTPUTF8` 参数，表明信封含非 ASCII 内容；
3. 邮件头使用 RFC 6532 定义的 UTF-8 头格式（如 `Subject:`、`From:` 可直接写中文）；
4. 非 ASCII 域名在 DNS 中仍用 punycode（A-label，如 `xn--...`）表示，仅在信头展示层可见 U-label。

## 与邮件认证的关系

国际化邮件下，SPF/DKIM/DMARC 的表示有专门规则（见 RFC 8616）：DNS 记录里一律用 A-label（punycode），信头里可保留 U-label，验证器在比较前必须做 U→A 强制转换。也就是说，SMTPUTF8 解决"能不能传"，RFC 8616 解决"传过去后认证怎么对齐"，二者缺一不可。

## 部署注意：端到端一致性

SMTPUTF8 是"木桶效应"——只要 MUA、MTA、MDA 任意一环不支持，整封邮件就会失败或被迫降级（downgrade，转成 ASCII 伪地址）。常见坑：

* 旧版网关/反垃圾设备不识别 `SMTPUTF8` 参数，直接拒收（5xx）；
* 名单/日志系统按 ASCII 设计，存入中文地址乱码；
* 第三方中继未开启 EAI，导致国际化邮件被弹回。

## 信创场景价值

信创邮件强调自主可控与本土化体验。支持 SMTPUTF8 的昆仑邮件系统可直接承载中文域名邮箱（如 `@辰童.中国`）、中文账号名，贴合政务与国企的本地化诉求；但同时要在架构上保证全链路（含认证、归档、审计）对 UTF-8 地址的一致性处理，避免"能发不能收"或"能收不能检索"。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/rfc6531-smtputf8-internationalized.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
