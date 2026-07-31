---
title: "迁移 DKIM selector 时如何保证邮件不断签、不丢失对齐？"
source: "https://ztpop.net/kb/dkim-selector-migration.html"
license: CC-BY 4.0
---

# 迁移 DKIM selector 时如何保证邮件不断签、不丢失对齐？

1
迁移 DKIM selector 时如何保证邮件不断签、不丢失对齐？
▼

**并行发布**

迁移到新 selector 时，先在 DNS 同时保留新旧两个 selector 公钥，使发信系统对新邮件用新 selector 签名，旧邮件/重试仍可用旧 selector 验证。

**渐进切换**

通过发信配置逐步把默认 selector 从旧切到新（如先 10% 流量），监控 DMARC 报告确认新 selector 的 dkim=pass 占比上升、旧 selector 流量归零。

**收尾**

确认旧 selector 已无新签名后，再将其公钥从 DNS 移除；过早删除会导致仍带旧 selector 的邮件 DKIM 验证失败。

**对齐**

selector 只决定“用哪把钥匙签名/验签”，不改变域对齐；迁移期间保持 From 域不变即可维持 DMARC 对齐。

参考：RFC 6376 §3.1（selector）；RFC 7489（DMARC 对齐）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/dkim-selector-migration.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
