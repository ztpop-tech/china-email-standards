---
title: "BIMI 全面解读：工作原理、Logo 规范与实施清单"
source: "https://ztpop.net/kb/bimi-all-about.html"
license: CC-BY 4.0
---

# BIMI 全面解读：工作原理、Logo 规范与实施清单

## 什么是 BIMI？

品牌邮件标识（Brand Indicators for Message Identification，BIMI）是一项邮件认证标准，使品牌能够在其经过认证的邮件旁显示经过验证的品牌 Logo。BIMI 依托于 **DMARC**（基于域的消息认证）等技术，确保只有通过认证的邮件才能展示品牌标识，从而帮助收件人快速识别真实的品牌邮件。

## BIMI 如何工作？

1. **DNS 发布品牌声明**：域名所有者（品牌方）通过 DNS 发布 BIMI DNS 记录，声明品牌 Logo 的位置和验证信息。
2. **邮件认证**：邮箱提供商收到邮件后，首先对邮件进行认证（SMTP 认证，如 SPF、DKIM 和 DMARC 策略检查）。
3. **DNS 查询**：如果邮件通过了认证检查，邮箱提供商查询发件域名的 DNS，查找对应的 BIMI 记录。
4. **Logo 展示**：如果 BIMI 记录存在且有效（可选配 VMC/CMC 证书验证），邮箱提供商在收件箱的邮件详情中显示品牌 Logo。

注意：每个参与的邮箱提供商有各自的判断标准，决定何时显示某个域的 BIMI Logo。请参阅 [BIMI Senders FAQ](https://bimigroup.org/faqs-for-senders-esps/?utm_source=AllAboutBIMI) 了解更多。

## 为什么需要 BIMI？

将品牌 Logo 与邮件关联是一项挑战——数以万计的品牌与 Logo 组合需要管理。如果没有标准化的发现和发布机制，每个对展示 Logo 感兴趣的邮箱提供商必须自行开发专属的 Logo 管理系统。这导致复杂、维护困难且各自为政的系统，品牌经常因邮件中显示的错误 Logo 而困扰。BIMI 为参与组织提供了 Logo 展示的标准化方案。

实施 BIMI 带来的核心收益：

* **品牌控制权**：品牌可以对邮件中展示的 Logo 拥有自主控制权。
* **提升信任度**：收件人通过品牌 Logo 快速识别真实邮件，降低被钓鱼邮件欺骗的风险。
* **增强邮件互动率**：品牌邮件在收件箱中的视觉识别度大幅提升。

## BIMI Logo 当前在哪里显示？

目前，BIMI Logo 通常在邮件客户端的邮件展示区域（邮件详情视图）中显示在发件人地址旁边。部分邮箱客户端也在邮件列表视图中展示 Logo。详细信息请参阅 BIMI Group 文章 [Where Is My BIMI Logo Displayed?](https://bimigroup.org/where-is-my-bimi-logo-displayed/)。

## Logo 规范

要与 BIMI 关联使用，Logo 必须满足以下规范要求：

* **正方形**：Logo 必须为正方形比例。
* **SVG 格式**：必须保存为可缩放矢量图形（SVG）格式。
* **SVG Tiny Portable/Secure 规范**：必须遵循 BIMI 工作组定义的 SVG Tiny P/S（便携/安全）配置文件限制。
* **禁止脚本标签**：Logo 文件中不得包含任何 <script> 标签。
* **禁止外部链接**：不应包含任何外部链接。
* **手动调整**：需要手动进行一些调整以满足尺寸和安全要求。
* **注册商标优先**：随着规范的持续发展，部分邮箱提供商可能要求 Logo 聚焦于品牌合法注册的"Logo Type"，而不包含二级文字商标或未注册商标。

更详细的 SVG 创建指南请参考 BIMI Group 的 [Creating BIMI SVG Logo Files](https://bimigroup.org/creating-bimi-svg-logo-files/)。

## 如何实施 BIMI？

实施 BIMI 对一些组织来说可能具有挑战性。以下是实施前的检查清单：

1. **邮件认证前置（必须）**：确保所有组织的邮件通过以下认证：
   * 邮件通过 DMARC 验证检查
   * 发件域（RFC5322.From 域和所属组织域）的 DMARC 策略设置为 `p=quarantine`（且 `pct=100`）或 `p=reject`
2. **DNS 发布 BIMI 记录**：在 DNS 中发布 BIMI TXT 记录，指向：
   * SVG 格式的 Logo 文件（通过 `l` 标签指定 URL）
   * 可选：包含 VMC/CMC 证书信息（通过 `a` 标签指定证书 URI）
3. **准备 Logo 文件**：按照 SVG Tiny P/S 规范创建品牌 Logo。
4. **获取证书（可选但推荐）**：对于要求证书的邮箱提供商（如 Gmail、Apple Mail），需申请 VMC 或 CMC 证书。

## 在哪里获取更多 BIMI 更新？

* BIMI Group 官网：<https://bimigroup.org>
* Twitter：[@bimigroup](https://twitter.com/bimigroup)
* YouTube：[BIMI Group Channel](https://www.youtube.com/channel/UC8IXA1iJ0RV0xG6i8Jgk8Qg)
* LinkedIn：[BIMI Group](https://www.linkedin.com/company/66710136)
* IETF BIMI 邮件列表：[加入列表](https://www.ietf.org/mailman/listinfo/bimi)

## 参考文献

1. BIMI Group. *All About BIMI*. <https://bimigroup.org/all-about-bimi/>
2. BIMI Group. *Where Is My BIMI Logo Displayed?*. <https://bimigroup.org/where-is-my-bimi-logo-displayed/>
3. BIMI Group. *Creating BIMI SVG Logo Files*. <https://bimigroup.org/creating-bimi-svg-logo-files/>
4. BIMI Group. *BIMI Implementation Guide*. <https://bimigroup.org/implementation-guide/>
5. BIMI Group. *Mark Verifying Authority FAQs*. <https://bimigroup.org/mva-faqs/>
6. RFC 7489 — DMARC. <https://datatracker.ietf.org/doc/html/rfc7489>
7. RFC 7208 — SPF. <https://datatracker.ietf.org/doc/html/rfc7208>
8. RFC 6376 — DKIM. <https://datatracker.ietf.org/doc/html/rfc6376>
9. IETF BIMI Working Group. <https://datatracker.ietf.org/wg/bimi/about/>
10. ztpop.net 知识库. [BIMI 品牌邮件标识深度解析](/kb/bimi-guide.html)
11. ztpop.net 知识库. [DMARC 完整实施指南](/kb/dmarc-guide.html)
12. ztpop.net 知识库. [BIMI 标记验证机构（MVA）FAQ](/kb/bimi-mva-faqs.html)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/bimi-all-about.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
