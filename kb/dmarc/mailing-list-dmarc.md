---
title: "邮件列表（mailing list）为什么会破坏 DMARC？列表服务该如何兼容？"
source: "https://ztpop.net/kb/mailing-list-dmarc.html"
license: CC-BY 4.0
---

# 邮件列表（mailing list）为什么会破坏 DMARC？列表服务该如何兼容？

1
邮件列表（mailing list）为什么会破坏 DMARC？列表服务该如何兼容？
▼

**冲突**

邮件列表收到投稿后，常以列表自身信封（改写 envelope-from 为列表域）转发给订户，且常改写 Subject、加 List- 头、加页脚——这些会破坏原 DKIM 签名；同时 envelope-from 变了使 SPF 不对齐。结果：以严格 DMARC(p=reject) 域为 From 的投稿，经列表转发后被多数收件方拒绝。

**列表侧缓解**

用自己域 DKIM 重签（d=列表域）并保留作者原 DKIM（若未被破坏）；对 From 域策略为 reject 的投稿，列表可把作者地址封装进信封并把显示 From 改为列表地址（或经成员域信任的转发），避免作者域 DMARC 失败。

**订阅方侧**

收件域应识别 List-Id / 列表特征，对已知良好列表放宽（而非硬拒），减少误伤。

**实践**

现代列表软件（Mailman 3、Sympa）已内置 DMARC 兼容（如 From 改写 + 重签）；订阅大量 strict-DMARC 域的列表需谨慎配置。

参考：RFC 7489（DMARC 与转发/列表交互）；Mailman/Sympa DMARC 兼容实践

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/mailing-list-dmarc.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
