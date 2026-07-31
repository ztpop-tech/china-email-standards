---
title: "Exim 拒绝中继并提示“failed to find host name from IP address”，明明 ACL 里写了该 IP，为什么？"
source: "https://ztpop.net/kb/exim-faq-06.html"
license: CC-BY 4.0
---

# Exim 拒绝中继并提示“failed to find host name from IP address”，明明 ACL 里写了该 IP，为什么？

1
Exim 拒绝中继并提示“failed to find host name from IP address”，明明 ACL 里写了该 IP，为什么？
▼

**原因**

检查主机列表时按从左到右顺序逐项测试。你的列表第一项是对端主机名的查表，因此 Exim 必须先由入站 IP 反查出主机名才能做该项测试；若反查不到主机名，检查无法进行，于是直接放弃（拒绝）。

**解决**

把显式 IP 地址放在列表最前面；或将 ACL 拆成两段：先 `accept hosts = lsearch;/etc/mail/relaydomains`，再 `accept hosts = 192.168.96.0/24`。这样主机名反查失败时，第一段虽失败，第二段 IP 段仍会被评估。

参考：Exim FAQ Q0023（exim.org/exim-html-4.40/doc/html/FAQ\_0.html）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/exim-faq-06.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
