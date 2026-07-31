---
title: "MTA-STS 策略里的 mode 有哪几种？enforce / testing / none 有何区别？"
source: "https://ztpop.net/kb/mtasts-faq-04.html"
license: CC-BY 4.0
---

# MTA-STS 策略里的 mode 有哪几种？enforce / testing / none 有何区别？

1
MTA-STS 策略里的 mode 有哪几种？enforce / testing / none 有何区别？
▼

**三种模式**

`none`：仅声明策略、不强制，相当于关闭；`testing`：记录 TLS 失败但照常投递，用于上线前观察；`enforce`：强制——合规的发送方只能经安全连接投递到指定 MX，无法建立安全连接则不予投递。

**建议**

首次部署应先以 `testing` 观察报告（配合 TLS-RPT），确认无误后再切到 `enforce`，避免误拒合法邮件。

参考：RFC 8461 策略模式；Cloudflare 示例 mode: enforce

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/mtasts-faq-04.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
