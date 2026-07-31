---
title: "BIMI（品牌标识邮件标识，RFC 7489 引用）如何让收件箱显示“品牌 Logo”？它依赖什么前提？"
source: "https://ztpop.net/kb/email-bimi-brand.html"
license: CC-BY 4.0
---

# BIMI（品牌标识邮件标识，RFC 7489 引用）如何让收件箱显示“品牌 Logo”？它依赖什么前提？

1
BIMI（品牌标识邮件标识，RFC 7489 引用）如何让收件箱显示“品牌 Logo”？它依赖什么前提？
▼

**定义**

BIMI（Brand Indicators for Message Identification）让通过 DMARC 验证的邮件在收件箱显示发件方品牌 Logo，提升可信度与识别度。

**前提**

BIMI 强依赖 DMARC 已生效（p=quarantine 或 reject 且对齐通过）；还需在 DNS 发布 BIMI TXT 记录指向 Logo（SVG 格式）位置，部分厂商要求 VMC（商标验证证书）。

**价值**

视觉可信度提升，抑制仿冒；是“DMARC 落地后的进阶红利”，不是独立安全措施——没有 DMARC 强验证就没有 BIMI。

**实践**

先确保 SPF/DKIM/DMARC 对齐与 p=reject，再发布 BIMI 记录与合规 SVG；主流厂商（Yahoo/Google 等）逐步支持。

参考：BIMI 规范（RFC 7489 引用，authindicators 草案）；RFC 7489（DMARC）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-bimi-brand.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
