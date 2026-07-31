---
title: "M3AAWG 建议发送方实施哪些邮件认证？核心清单是什么？"
source: "https://ztpop.net/kb/m3aawg-faq-01.html"
license: CC-BY 4.0
---

# M3AAWG 建议发送方实施哪些邮件认证？核心清单是什么？

1
M3AAWG 建议发送方实施哪些邮件认证？核心清单是什么？
▼

**发送方认证清单**

M3AAWG 在《邮件认证推荐最佳实践》中为发送方（品牌方、邮箱服务商、ESP）给出一份“非有即无”的二元清单：**SPF**——为 MAIL FROM 与 EHLO 域名发布记录，记录以 `~all` 结尾，不过度授权 IP，并尽量让 MAIL FROM 域与邮件头 From 域对齐；不发送邮件的域名发布 `v=spf1 -all`。**DKIM**——用与 RFC5322.From 域对齐的密钥为所有外发邮件签名，并遵循密钥管理最佳实践。**DMARC**——策略尽量用 `p=reject`，否则用 `p=quarantine`；`p=none`、`sp=none` 与 `pct<100` 仅作为过渡状态，应尽快移除；记录须包含 `rua` 标签。

参考：M3AAWG《Email Authentication Recommended Best Practices》(2020-09)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/m3aawg-faq-01.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
