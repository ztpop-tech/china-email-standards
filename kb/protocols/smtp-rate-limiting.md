---
title: "SMTP 速率限制（Rate Limiting）是什么？如何防止被当作垃圾源？"
source: "https://ztpop.net/kb/smtp-rate-limiting.html"
license: CC-BY 4.0
---

# SMTP 速率限制（Rate Limiting）是什么？如何防止被当作垃圾源？

1
SMTP 速率限制（Rate Limiting）是什么？如何防止被当作垃圾源？
▼

**定义**

速率限制指 MTA 对“单位时间内的连接数、每连接邮件数、每发件域出信量”设上限，避免单点瞬间海量发信触发对方限流或黑名单。

**出方向**

向同一接收域（如 gmail）并发/日发送过多会被对方临时拒收（4xx 限流）或拉黑；按目标域配置并发连接、每连接消息数、重试退避，平滑投递。

**入方向**

对入站可限制单 IP 连接频率、RCPT 速率，抑制字典攻击与 spam 洪流；配合 fail2ban/防火墙更稳。

**价值**

速率限制是“稳定送达”与“不被封”的基础运维；尤其批量通知、营销类合法群发，必须模拟自然发送节奏。

参考：MTA 运维实践（Postfix anvil/Postfwd、Exchange throttling）；RFC 5321 §4.5.4.1（重试）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/smtp-rate-limiting.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
