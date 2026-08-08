---
title: "邮件里的「一键退订」背后是什么协议？List-Unsubscribe-Post 怎么工作？"
source: "https://ztpop.net/kb/list-unsubscribe-one-click-rfc8058.html"
license: CC-BY 4.0
---

# 邮件里的「一键退订」背后是什么协议？List-Unsubscribe-Post 怎么工作？

1
邮件里的「一键退订」背后是什么协议？List-Unsubscribe-Post 怎么工作？
▼

**一键退订要解决什么**

RFC 8058 标题即「Signaling One-Click Functionality for List Email Headers」。传统 List-Unsubscribe 头常给一个 mailto: 地址，用户需手动发信，易出错、退订率低；RFC 8058 定义了在 List-Unsubscribe 头之外再增加一个 List-Unsubscribe-Post 头，使退订变成一次点击即可完成的 HTTPS POST。

**两个头的写法**

RFC 8058 第 3 节规定：希望启用一键退订的发件人，应在邮件中放**一个** List-Unsubscribe 头与**一个** List-Unsubscribe-Post 头。List-Unsubscribe 头**必须**包含一个 HTTPS URI（也可附带 MAILTO: 等非 HTTP/S 的 URI）；List-Unsubscribe-Post 头**必须**包含单一取值。两相结合即向邮件客户端声明「此退订支持一键」。

**一次点击的实际流程**

RFC 8058 第 3 节描述的一键流程：用户点击退订 → 邮件客户端向 List-Unsubscribe 中的 HTTPS URI 发送一个 POST 请求，请求体携带 `List-Unsubscribe=One-Click` → 接收方据此把该请求与其他退订请求区分，作为「一键退订」处理。整个过程用户无需撰写或发送邮件。

**合规与投递收益**

一键退订降低了用户的退订摩擦，从而提升实际退订率、减少「直接举报为垃圾」的投诉。这对满足 CAN-SPAM、CASL、GDPR 等法规下的退订权要求、以及维持发信域信誉（投诉率过高会进黑名单）都有直接帮助。主流邮件服务商已把 List-Unsubscribe-Post 作为批量发信的推荐甚至强制能力。

参考：https://www.rfc-editor.org/rfc/rfc8058.txt

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/list-unsubscribe-one-click-rfc8058.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
