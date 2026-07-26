---
title: "BIMI lps 标签详解：同一域名显示不同品牌 Logo"
source: "https://ztpop.net/kb/bimi-lps-tag-guide.html"
license: CC-BY 4.0
---

# BIMI lps 标签详解：同一域名显示不同品牌 Logo

大多数 BIMI 部署方案中，一个域名下发送的所有邮件都显示同一个 Logo。对于很多组织来说，这恰恰是他们想要的。

然而，有些组织会发送不同类型的邮件，代表不同的品牌或业务职能。营销邮件可能使用一个 Logo，客户支持邮件使用另一个，而员工个人邮件可能根本不需要显示 BIMI Logo。

BIMI lps 标签（Local-part as Selector，本地部分作为选择器）正是为支持这些场景而引入的，无需修改邮件本身。虽然它提供了相当大的灵活性，但它仍是 BIMI 规范中相对较新的特性。目前支持情况取决于收件邮箱提供商是否实现了该功能，因此组织在将其纳入品牌策略之前应先验证兼容性。

## 什么是 BIMI lps 标签？

lps 的全称是 Local-part as Selector（本地部分作为选择器）。

local-part（本地部分）即电子邮件地址中 @ 符号之前的部分。

例如：

* `marketing@example.com` → local-part: marketing
* `support@example.com` → local-part: support
* `jane.smith@example.com` → local-part: jane.smith

通常情况下，邮箱提供商会查询一个默认的 BIMI 记录：

```
default._bimi.example.com
```

如果该记录中包含 lps 标签，邮箱提供商可能再进行一次 DNS 查询，使用发件人的 local-part 作为 BIMI selector（选择器）。

## 为什么使用 lps？

最明显的用例是为不同业务职能显示不同的 Logo。

例如：

* 营销邮件显示企业品牌 Logo
* 客户支持邮件显示支持团队 Logo
* 账单邮件显示财务或支付 Logo

还有一个常被忽视的好处。

有些组织可能会从同一个主域名发送营销邮件和员工个人邮件。如果没有额外的控制手段，该域名上的每个邮箱地址都可能获得相同的 BIMI Logo。

lps 标签允许组织将 BIMI 品牌标识限制在已获授权的对外联系邮箱地址上，例如 newsletter@example.com、offers@example.com 或 support@example.com，而像 alice@example.com 这样的个人邮箱则继续显示收件人的联系人头像、默认头像或不显示任何 Logo。

这样一来，组织无需使用独立的发送域名，就能对品牌呈现的位置进行更精细的控制。

## 工作原理

可以把 lps 标签想象成一个路标。

当邮箱提供商执行常规 BIMI 查询时，首先检查默认的 BIMI 记录：

```
default._bimi.example.com TXT "v=BIMI1; l=; a=; lps=newsletter,offers,promotions"
```

这条记录告诉邮箱提供商：

* 默认情况下，不显示 BIMI logo
* 如果发件人的 local-part 以 newsletter、offers 或 promotions 开头，则用该 local-part 作为 selector（选择器）再执行一次 BIMI 查询

例如，如果发件人是 newsletter@example.com，邮箱提供商就会进行第二次 DNS 查询：

```
newsletter._bimi.example.com TXT "v=BIMI1; l=https://example.com/logos/newsletter.svg; a=https://example.com/certs/vmc.pem;"
```

由于这条记录存在，newsletter Logo 就会在该邮件旁显示。

如果发件人是 alice@example.com，则没有匹配的 prefix（前缀），不会触发第二次查询。邮箱提供商直接使用默认的 BIMI 记录——在本例中，该记录明确没有发布任何 Logo。

## 为何不直接使用 BIMI-Selector 标头？

BIMI 规范已经支持 BIMI-Selector 邮件标头，允许发件人选择该邮件应使用哪条 BIMI 记录。

问题在于，许多邮件平台很难轻松添加或修改自定义邮件标头。更新 DNS 通常比修改出站邮件系统要简单得多——尤其是当多个应用程序或服务提供商代表同一域名发送邮件时。

lps 标签将选择逻辑移入 DNS，让邮箱提供商能够根据发件人的邮箱地址自动确定合适的选择器（selector）。

## 注意事项

在实施 lps 之前，请留意以下几点：

* 邮箱提供商会先对 local-part 进行规范化处理，再将其用作 selector。例如，会去除 plus 地址部分（plus addressing），并将句点或下划线转换为连字符。
* lps 标签可以包含一个或多个逗号分隔的 prefix（前缀），也可以留空（`lps=`）以允许每个发件人都触发选择器查询。
* 每次成功匹配都需要一次额外的 DNS 查询。
* 虽然 lps 已纳入 BIMI 规范，但邮箱提供商的支持仍在逐步推广中。不支持 lps 的提供商会直接忽略该标签，继续按照标准方式评估 BIMI 记录。

lps 标签赋予了组织对品牌标识呈现方式的更精细控制。它可以为不同的业务职能显示不同的 Logo，也可以将 BIMI 限制在共享域名上已授权的邮箱地址，防止每个员工邮箱都继承组织的营销 Logo。

虽然各邮箱提供商的支持仍在发展中，但对于那些希望在不修改出站邮件基础设施的前提下实现更精细 BIMI 品牌呈现的组织来说，lps 提供了一种优雅的、基于 DNS 的解决方案。随着 BIMI 采纳率不断增长，这是一个值得了解并在未来部署中牢记的功能。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/bimi-lps-tag-guide.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
