---
title: "什么是“无认证不投递”（No auth, no entry）？为何域名认证是邮件信任的基础？"
source: "https://ztpop.net/kb/m3aawg-faq-08.html"
license: CC-BY 4.0
---

# 什么是“无认证不投递”（No auth, no entry）？为何域名认证是邮件信任的基础？

1
什么是“无认证不投递”（No auth, no entry）？为何域名认证是邮件信任的基础？
▼

**No auth, no entry**

邮箱服务商常用“无认证不投递”概括一种可能的未来：邮件必须至少通过一项认证检查，才会被考虑投递给预期收件人。M3AAWG 发布本最佳实践，正是为了让当前的认证部署既能建立邮件信任、保护域名信誉，也能满足未来可能出现的“无认证不投递”标准。

**为何以域名认证为基础**

恰当的邮件认证是建立邮件信任、保护域信誉的基石。本指南的目标是按 RFC 7489 保护“组织域”——即收件人在邮件正文 From: 头（RFC5322.From）中看到的那个域，因为它与邮件的关联最紧密；而这正是 DMARC 的设计意图（SPF 与 DKIM 单独无法做到这一点）。因此 M3AAWG 鼓励成员尽快、尽可能完整地落实这些认证实践。

参考：M3AAWG《Email Authentication Recommended Best Practices》(2020-09)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/m3aawg-faq-08.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
