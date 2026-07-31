---
title: "DMARC 记录为什么必须包含 rua 标签？ruf 标签呢？"
source: "https://ztpop.net/kb/m3aawg-faq-05.html"
license: CC-BY 4.0
---

# DMARC 记录为什么必须包含 rua 标签？ruf 标签呢？

1
DMARC 记录为什么必须包含 rua 标签？ruf 标签呢？
▼

**rua 必选**

任何已发布的 DMARC 记录，即便策略是 `p=none`，也应至少包含一个指向接收聚合报告邮箱的 `rua` 标签。聚合报告由执行 DMARC 校验的接收方发出，包含其看到的、声称来自该域的邮件统计。没有报告，域名所有者就无法判断能否安全从 p=none 收紧策略。

**ruf 可选**

鉴于隐私顾虑及需对可能含个人身份信息（PII）的内容做脱敏，DMARC 失败报告（ruf）多数接收方既不发送、对多数域名所有者也不太有用，因此 ruf 标签为可选。`rua` 与 `ruf` 邮箱收到报告后都不应自动回复。

参考：M3AAWG《Email Authentication Recommended Best Practices》(2020-09)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/m3aawg-faq-05.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
