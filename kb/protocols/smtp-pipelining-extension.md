---
title: "SMTP 的 PIPELINING 扩展（RFC 2920）如何减少“往返等待”提升吞吐？"
source: "https://ztpop.net/kb/smtp-pipelining-extension.html"
license: CC-BY 4.0
---

# SMTP 的 PIPELINING 扩展（RFC 2920）如何减少“往返等待”提升吞吐？

1
SMTP 的 PIPELINING 扩展（RFC 2920）如何减少“往返等待”提升吞吐？
▼

**原理**

标准 SMTP 每发一条命令要等服务器响应再发下条；PIPELINING（EHLO 声明）允许客户端“一次性发多条命令”（如 EHLO 后连发 MAIL/RCPT/DATA），服务器按顺序回包。

**收益**

大幅减少网络往返（RTT）开销，尤其高延迟链路上显著加速批量投递；是性能优化扩展，不改变语义。

**约束**

仅“确定无依赖”的命令可批；DATA 之后必须等 354 才能发信体；管线中任一命令失败仍按序处理，客户端需正确解析每条响应。

**实践**

现代 MTA 普遍支持 PIPELINING；邮件系统批量投递开启管线可提升吞吐，但需保证命令顺序与响应解析正确。

参考：RFC 2920（SMTP Pipelining 扩展）；RFC 5321

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/smtp-pipelining-extension.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
