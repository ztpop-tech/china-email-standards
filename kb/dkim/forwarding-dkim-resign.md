---
title: "转发服务器如何“重签 DKIM”（re-sign）来保证转发后认证仍通过？"
source: "https://ztpop.net/kb/forwarding-dkim-resign.html"
license: CC-BY 4.0
---

# 转发服务器如何“重签 DKIM”（re-sign）来保证转发后认证仍通过？

1
转发服务器如何“重签 DKIM”（re-sign）来保证转发后认证仍通过？
▼

**背景**

DKIM 签名随邮件传输，转发通常不破坏它；但若转发服务器改写正文/头（如加页脚、改写路由头），原签名可能失效。此时转发方可用自己的域重签（re-sign）。

**机制**

转发 MTA 在转发前用自己域的 DKIM 私钥对新邮件（含可能被改写的头体）生成新 DKIM-Signature（d=转发域），原签名保留或移除。这样至少“转发域的 DKIM”通过。

**对齐考量**

重签后 DKIM d= 是转发域，与可见 From 域不对齐，DMARC 仍可能失败（除非转发域是 From 域的授权子域或存在信任链）。故单纯重签不足以让 DMARC 对齐。

**实践**

为让 DMARC 通过，转发/列表服务常配合“改写 envelope-from 为自身域”（SRS 或自有 Return-Path）+ 自身 DKIM 重签 + 保留原 DKIM，使至少一项对齐。

参考：RFC 6376 §5.3（重签实践）；RFC 7489（对齐要求）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/forwarding-dkim-resign.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
