---
title: "BIMI 证书类型详解：自声明、公共标识证书与验证标识证书"
source: "https://ztpop.net/kb/bimi-certificate-types.html"
license: CC-BY 4.0
---

# BIMI 证书类型详解：自声明、公共标识证书与验证标识证书

在实施 BIMI（Brand Indicators for Message Identification，品牌标识消息识别）时，使用 BIMI 证书验证品牌 Logo 可以为全球邮箱提供商处的收件人带来额外收益。品牌 Logo 的声明方式共有三种类型：自声明（Self-assertion）、公共标识证书（CMC, Common Mark Certificate）和验证标识证书（VMC, Verified Mark Certificate）。理解这些区别，才能确保 BIMI 实施带来预期的效果。

## BIMI 证书声明类型的区别

BIMI 证书的核心区别在于所验证的标识类型及其关联要求。根据 MC Guidelines（标识证书指南）第 1.1 节概述，这些区别定义如下：

* **自声明 Logo（Self-asserted Logos）**：这是最简单的 BIMI 实施形式，无需通过证书进行验证，因此是 BIMI 采用的良好入门点。目前仅有少数邮箱提供商支持此类 BIMI 记录，但在 Yahoo、Fastmail 和 LaPoste 等提供商处仍可获益。自声明通过在 BIMI 记录中省略 `a=;` 或将 `a=` 值中的 URL 部分留空来表示。它们仍然需要一个通过 HTTPS 托管的 SVG 文件、一条 BIMI DNS 记录以及强制执行状态的 DMARC。
* **公共标识证书（CMC, Common Mark Certificate）**：此类证书适用于可能不是注册商标的标识。
  + **在先使用标识（Prior Use Mark）**：依据第 3.2.16.1 节定义，此类证书反映了一段合法的使用历史，无需商标注册。这种灵活性使 CMC 对更广泛的组织具有可及性。
  + **修改后注册商标（Modified Registered Mark）**：依据第 3.2.16.2 节定义，此类证书表示在保持与原注册商标关联的前提下经过修改的标识。它们在兼顾适应性的同时，不损害验证过程的完整性。
* **验证标识证书（VMC, Verified Mark Certificate）**：此类证书专为拥有注册商标或政府认可标识的组织量身定制。
  + **注册商标（Registered Mark）**：依据第 3.2.17.1 节验证，此类标识经过严格的验证流程，确保符合高标准的认证要求。VMC 在传递可信度和真实性方面发挥着关键作用。
  + **政府标识（Government Mark）**：依据指南第 3.2.17.2 节验证，此类标识获得政府机构的官方认可，强调其法律上的真实性。

每种证书类型都有特定的使用场景和标识其用途的字段，因此必须根据品牌的资质和邮件营销目标来匹配正确的选择。

## CMC 中"在先使用"的作用

对于"在先使用"（Prior Use）证书，证书中的特定字段有助于识别标识类型。指南第 7.1.4.2.2.r 节对此有详细描述：

* **证书字段**：subject:markType（OID: 1.3.6.1.4.1.53087.1.13）
* **要求**：此字段为必填项。
* **内容**：必须包含以下值之一，对应不同的验证方法：
  + 注册商标（Registered Mark）：第 3.2.17.1 节
  + 政府标识（Government Mark）：第 3.2.17.2 节
  + 在先使用标识（Prior Use Mark）：第 3.2.16.1 节
  + 修改后注册商标（Modified Registered Mark）：第 3.2.16.2 节

## 如何识别你的 BIMI 证书类型

要确定你的证书是 VMC 还是 CMC：

* 查阅 MC Guidelines（标识证书指南）中的证书概要（Profile）。
* 检查 subject:markType 字段的值。
* 参照第 3.2.16 节或第 3.2.17 节中概述的验证方法。

例如，如果 subject:markType 包含"Prior Use Mark"（在先使用标识），则该证书属于第 3.2.16.1 节定义的 CMC。

## BIMI 证书选择为何重要

VMC 和 CMC 之间的区别直接影响品牌 Logo 在收件箱中的展示方式。不同邮箱提供商的处理方式可能有所不同，Logo 的展示由各提供商自行决定；AuthIndicators 工作组并未就这些区别提供明确的指导。我们可以想象的示例如：VMC 可能同时获得 Logo 和信任指示器，而 CMC 可能仅获得 Logo 但无信任指示器。由于目前对 CMC 的支持有限，我们暂时无法提供具体的实例。

正确配置的证书可以加强邮件身份认证，并增强收件人对品牌的信任。

如需全面了解，请从第 1.1 节开始查阅 MC Guidelines（标识证书指南），并深入了解第 3.2.16 节和第 3.2.17 节中验证方法的详细信息。

### 相关主题

* [BIMI Logo 更新完整指南：品牌换标后如何保持邮件身份认证](/kb/bimi-logo-update-guide.html)
* [BIMI lps 标签详解：同一域名显示不同品牌 Logo](/kb/bimi-lps-tag-guide.html)
* [邮件身份认证生态体系全景解读](/kb/email-authentication-alignment.html)
* [邮件 DNS 一键诊断](/tools/dns-check.html)（含 BIMI 记录检查）

本文涉及的关键技术领域：邮件认证、BIMI、DMARC

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/bimi-certificate-types.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
