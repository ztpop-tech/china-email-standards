---
title: "M3AAWG 推荐 DMARC 策略用 p=reject 还是 p=quarantine？p=none 意味着什么？"
source: "https://ztpop.net/kb/m3aawg-faq-04.html"
license: CC-BY 4.0
---

# M3AAWG 推荐 DMARC 策略用 p=reject 还是 p=quarantine？p=none 意味着什么？

1
M3AAWG 推荐 DMARC 策略用 p=reject 还是 p=quarantine？p=none 意味着什么？
▼

**首选 reject**

M3AAWG 建议发布 DMARC 记录的域名其策略声明为 `p=reject`；若对某些域名存在运营挑战，则在其他情形下考虑 `p=quarantine`。组织应结合自身被伪造/钓鱼的风险状况，在“reject/quarantine 的保护收益”与“因缺失或错误签名导致合法邮件丢失”之间取得平衡。

**p=none 只是过渡**

`p=none`、`sp=none` 与 `pct<100` 只应被视为过渡状态，目标是尽快移除它们。因为只有在能接收并处理报告的前提下，域名所有者才能确认所有合法邮件都正确认证，从而安全地从 p=none 收紧到更严格的策略。

参考：M3AAWG《Email Authentication Recommended Best Practices》(2020-09)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/m3aawg-faq-04.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
