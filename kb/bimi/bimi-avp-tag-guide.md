---
title: "BIMI avp 标签详解：控制邮件中显示个人头像还是品牌 Logo"
source: "https://ztpop.net/kb/bimi-avp-tag-guide.html"
license: CC-BY 4.0
---

# BIMI avp 标签详解：控制邮件中显示个人头像还是品牌 Logo

谈到 BIMI，大多数营销人员都了解基础知识：`v=BIMI1` 版本标签、指向 Logo 位置的 `l=` 标签，以及指向标识证书（Mark Certificate, MC）的可选 `a=` 证据标签。但有一个较新的特性常常被忽视——`avp` 标签，它在 BIMI 标准 v09 版本中引入。

让我们来解读它是什么、为什么存在，以及何时应该包含它。

## 什么是 avp 标签？

avp（Avatar Preference，头像偏好）标签用于设置显示偏好。它有两个值：

* `avp=personal`：如果发件人有个人头像，邮箱提供商应显示个人头像。如果没有个人头像，则显示 BIMI Logo。
* `avp=brand`：即使存在个人头像，邮箱提供商也应显示该域名的 BIMI Logo。

这为品牌提供了一个选项，以控制收件人看到的视觉标识。

## 为什么它很重要？

想象一下某家大公司的员工。他们的邮箱提供商可能有一个绑定到个人邮箱地址的个人头像（个人资料照片）。如果没有 `avp` 标签，提供商自行决定显示哪个——这可能导致跨邮件的品牌呈现不一致。

`avp` 标签通过明确表达发件人的偏好解决了这个问题。品牌可以坚持始终显示自己的 Logo，也可以允许个人头像优先显示。

## BIMI 记录示例

偏好个人头像，BIMI Logo 作为后备：

```
v=BIMI1; l=https://example.com/logo.svg; a=https://example.com/vmc.pem; avp=personal;
```

偏好品牌 Logo，即使存在个人头像：

```
v=BIMI1; l=https://example.com/logo.svg; a=https://example.com/vmc.pem; avp=brand;
```

虽然 `avp` 标签是可选的，但它是一个将显示效果与品牌策略对齐的巧妙工具。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/bimi-avp-tag-guide.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
