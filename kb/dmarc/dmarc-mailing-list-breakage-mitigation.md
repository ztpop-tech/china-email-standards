---
title: "邮件列表（邮件组/转发）为什么会破坏 DMARC，有哪些缓解办法？"
source: "https://ztpop.net/kb/dmarc-mailing-list-breakage-mitigation.html"
license: CC-BY 4.0
---

# 邮件列表（邮件组/转发）为什么会破坏 DMARC，有哪些缓解办法？

1
邮件列表（邮件组/转发）为什么会破坏 DMARC，有哪些缓解办法？
▼

**为什么会破坏**

RFC 7489 §10.5 指出，邮件列表转发常会修改邮件（改 Subject、加列表页脚、把信封重写为列表地址），导致两件事：①原始 DKIM 签名失效，因为签名覆盖了被改动的头部/正文；②MAIL FROM 变为列表服务器的域，使 SPF 对齐失败。于是来自列表的合法邮件可能被判 DMARC 失败而被拒或进垃圾箱。

**发送方缓解**

使用 relaxed 对齐（默认）以容忍子域差异；确保 From、Date、Message-ID 等关键头在 DKIM 签名体内且不被列表改写；对高价值列表部署 ARC（Authenticated Received Chain）以保留原始认证链。

**列表服务端缓解**

在转发前对来自已通过 DMARC 的邮件重新签名（re-sign）；采用 SRS 重写 envelope sender 以保留 SPF；尽量避免改写会破坏 DKIM 的头部/正文，或改用只签名"安全"头的密钥。

**接收方缓解**

可基于列表声誉与 ARC 链对来自已知良性列表的邮件做例外处理，而非一律按 DMARC 失败处置。

参考：RFC 7489 §10.5

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/dmarc-mailing-list-breakage-mitigation.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
