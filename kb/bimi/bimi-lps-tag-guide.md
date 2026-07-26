---
title: "BIMI lps 标签解析：如何为一个域名使用多个不同 Logo"
source: "https://ztpop.net/kb/bimi-lps-tag-guide.html"
license: CC-BY 4.0
---

# BIMI lps 标签解析：如何为一个域名使用多个不同 Logo

## 概述

大多数 BIMI 部署为单个域名展示一个统一的 Logo——对于许多组织来说，这正是他们所需要的。

然而，有些组织会发送不同类型的邮件，代表不同品牌或业务功能。营销邮件可能使用一个 Logo，客户支持邮件使用另一个，而员工邮件可能完全不展示 BIMI Logo。

BIMI lps 标签（Local-part as Selector，本地部分作为选择器）正是为了支持这些场景而引入的，无需修改邮件本身即可实现。虽然它提供了相当大的灵活性，但它仍是 BIMI 规范中相对较新的功能。目前支持情况取决于接收端邮箱提供商的实现，因此在将其作为品牌策略的核心依赖之前，组织应验证收件方兼容性。

## 什么是 BIMI lps 标签？

lps 代表 Local-part as Selector——本地部分作为选择器。

本地部分（local-part）是电子邮件地址中 @ 符号之前的部分。

例如：

| Email 地址 | Local-part |
| --- | --- |
| marketing@example.com | marketing |
| support@example.com | support |
| jane.smith@example.com | jane.smith |

通常，邮箱提供商会查找单个 BIMI 记录：

```
default._bimi.example.com
```

如果该记录中包含 lps 标签，邮箱提供商可以执行第二次 DNS 查找，使用发件人的本地部分作为 BIMI 选择器。

## 为什么使用 lps？

最直观的用例是为不同业务功能显示不同的 Logo。例如：

* 营销邮件使用企业品牌 Logo
* 客户支持邮件显示支持团队 Logo
* 账单邮件显示财务或支付 Logo

还有一个常被忽视的好处。

有些组织在其主域名上同时发送营销邮件和员工邮件。如果没有额外控制，该域名上的每个邮箱都可能获得相同的 BIMI Logo。

lps 标签允许组织将 BIMI 品牌限定在已批准的对客地址上，例如 newsletter@example.com、offers@example.com 或 support@example.com，而 alice@example.com 等个人邮箱则继续显示收件人的联系人照片、默认头像或不显示任何 Logo。

这给了组织更精细的控制权——无需创建独立的发信域名即可精确控制品牌展示位置。

## lps 的工作原理

可以把 lps 标签理解为一个路牌。

当邮箱提供商执行正常的 BIMI 查找时，它首先检查默认 BIMI 记录：

```
default._bimi.example.com TXT
  "v=BIMI1; l=; a=; lps=newsletter,offers,promotions"
```

这条记录告诉邮箱提供商：

* 默认情况下，不展示任何 BIMI Logo
* 如果发件人的本地部分以 newsletter、offers 或 promotions 开头，则使用该本地部分作为选择器执行第二次 BIMI 查找

例如，如果发件人是：

```
newsletter@example.com
```

邮箱提供商执行第二次 DNS 查找：

```
newsletter._bimi.example.com TXT
  "v=BIMI1; l=https://example.com/logos/newsletter.svg;
   a=https://example.com/certs/vmc.pem;"
```

由于该记录存在，newsletter 的 Logo 会被展示给该邮件的收件人。

如果发件人是：

```
alice@example.com
```

没有匹配的前缀，因此不会发生第二次查找。邮箱提供商直接使用默认 BIMI 记录——本例中明确发布了"无 Logo"。

## 为什么不直接使用 BIMI-Selector 邮件头？

BIMI 规范已经支持 BIMI-Selector 邮件头，允许发件方选择哪条 BIMI 记录应用于某封邮件。

挑战在于：许多邮件平台很难轻松添加或修改自定义邮件头。更新 DNS 通常比修改出站邮件系统简单得多——特别是当多个应用或服务商代表同一域名发信时。

lps 标签将此逻辑移至 DNS 中，允许邮箱提供商根据发件人的电子邮件地址自动确定适当的选择器。

## 注意事项

在实施 lps 之前，请注意以下几点：

* **规范化处理**：邮箱提供商会先规范化本地部分，再将其用作选择器。例如，去除 plus 地址后缀，将句点或下划线转换为连字符。
* **前缀列表**：lps 标签可以包含一个或多个逗号分隔的前缀，也可以留空（`lps=`）以允许每个发件人都触发选择器查找。
* **额外 DNS 查询**：每次成功匹配都需要一次额外的 DNS 查找。
* **渐进支持**：虽然 lps 已是 BIMI 规范的一部分，但邮箱提供商的支持仍在逐步推进中。未实现 lps 的提供商将忽略该标签，仅评估标准 BIMI 记录。

## 总结

lps 标签赋予组织更精细的品牌控制能力。它可以为不同业务功能显示不同的 Logo，也可以将 BIMI 限制在共享域名上获准的发件地址范围内，防止每个员工邮箱都继承组织的营销 Logo。

虽然邮箱提供商的全面支持仍在发展中，但 lps 为希望在无需修改出站邮件基础设施的情况下实施更精细化 BIMI 品牌策略的组织，提供了一个优雅的、基于 DNS 的解决方案。随着 BIMI 采用率持续增长，这是一个值得了解和关注的功能。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/bimi-lps-tag-guide.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
