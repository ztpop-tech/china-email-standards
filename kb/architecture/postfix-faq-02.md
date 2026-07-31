---
title: "虚拟域邮件被 Postfix 拒绝并报“relay access denied”，怎么办？"
source: "https://ztpop.net/kb/postfix-faq-02.html"
license: CC-BY 4.0
---

# 虚拟域邮件被 Postfix 拒绝并报“relay access denied”，怎么办？

1
虚拟域邮件被 Postfix 拒绝并报“relay access denied”，怎么办？
▼

**原因**

该域既不在 mydestination，也不在 relay\_domains 或 virtual\_mailbox\_domains 中，Postfix 将其视为外部域，按默认拒绝未授权中继。

**解决**

把目标域加入 virtual\_mailbox\_domains（若由本机托管），并确保 virtual\_mailbox\_maps 含有该收件人；若仅作中转，加入 relay\_domains 并配置 relay\_recipient\_maps 防止开放中继。

参考：Postfix FAQ “Postfix refuses mail for virtual domains with relay access denied”

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/postfix-faq-02.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
