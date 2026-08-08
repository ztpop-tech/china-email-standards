---
title: "BIMI 怎么让认证通过的邮件在收件箱显示品牌 Logo？"
source: "https://ztpop.net/kb/bimi-logo-certification.html"
license: CC-BY 4.0
---

# BIMI 怎么让认证通过的邮件在收件箱显示品牌 Logo？

1
BIMI 怎么让认证通过的邮件在收件箱显示品牌 Logo？
▼

BIMI（Brand Indicators for Message Identification）是一项**在收件端展示发件品牌 Logo**的标准，由 BIMI Group 与各大邮件服务商推动。

#### 一、DNS 里怎么声明

在域名发布 TXT 记录 `default._bimi.example.com`，内容形如 「v=BIMI1; l=https://example.com/logo.svg; a=https://example.com/vmc.pem」。其中 `l` 指向 Logo 文件，`a` 可选指向 VMC。

#### 二、Logo 与 VMC 要求

* Logo 必须为 **SVG 格式**（方形、矢量、含明确留白）。
* **VMC（Verified Mark Certificate，验证标志证书）**由受认可 CA 签发，证明你确有权使用该商标；部分主流服务商要求 VMC 才展示。

#### 三、硬前提：DMARC 必须强制

BIMI 仅在**域名已部署 DMARC 且策略为 p=quarantine 或 p=reject** 时才生效——BIMI 建立在「邮件已强认证」之上，未通过认证的邮件不会获得 Logo 展示。它提升品牌可信度，但不替代认证本身。

参考：https://bimigroup.org/

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/bimi-logo-certification.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
