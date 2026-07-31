---
title: "邮件投递延迟（Delivery Delay）如何排查？从哪些环节入手？"
source: "https://ztpop.net/kb/email-delivery-delay.html"
license: CC-BY 4.0
---

# 邮件投递延迟（Delivery Delay）如何排查？从哪些环节入手？

1
邮件投递延迟（Delivery Delay）如何排查？从哪些环节入手？
▼

**定位环节**

延迟可能发生在：① 发送方队列（积压/限流/重试）；② 网络/DNS（MX 解析慢、链路抖动）；③ 接收方灰名单（greylisting 故意延迟首投）；④ 对方限流（4xx tarpit）；⑤ 内容扫描/网关处理慢。

**看日志**

从 maillog/传输日志看每跳时间戳差：连接耗时、等待 220、TLS 握手、各 RCPT 与 DATA 响应时长；找出“卡在哪一步”。

**常见元凶**

灰名单（首次延迟数分钟到小时）、对方过载 4xx 限流、DNS 解析超时、以及本地队列积压。灰名单属正常机制，重试即达。

**处置**

确认是否灰名单/限流（等待重试即可）；检查本地队列与 DNS；对持续异常的目标域调高并发或换路由；必要时联系对方管理员。

参考：RFC 5321（投递流程）；MTA 日志排查实践；RFC 6647（灰名单）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-delivery-delay.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
