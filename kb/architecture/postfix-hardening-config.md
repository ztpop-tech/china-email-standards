---
title: "Postfix 邮件服务器有哪些关键安全加固项（防开放中继、TLS、访问控制）？"
source: "https://ztpop.net/kb/postfix-hardening-config.html"
license: CC-BY 4.0
---

# Postfix 邮件服务器有哪些关键安全加固项（防开放中继、TLS、访问控制）？

1
Postfix 邮件服务器有哪些关键安全加固项（防开放中继、TLS、访问控制）？
▼

**防开放中继**

默认 mynetworks 仅限本地/内网；relay\_domains 谨慎设置；用 smtpd\_relay\_restrictions 严格判定“谁可中继”，绝不把未知来源当可中继。

**TLS**

smtpd\_tls\_security\_level=may（入站鼓励加密）/encrypt（强制）；smtp\_tls\_security\_level=encrypt（出站强制）；禁用弱密码套件，优先 ECDHE；配置证书链与 OCSP。

**访问控制**

smtpd\_client\_restrictions / sender / recipient 限制链做 HELO 校验、RBL 拒绝、限流；用 postscreen 做入站前置防护（僵尸网络筛查）。

**实践**

Postfix 默认相对安全，但“中继策略”与“TLS 等级”是最大变量；变更后用 postconf -n 复核、swaks 实测对话，避免开放中继与明文泄露。

参考：Postfix 官方文档（TLS、access、postscreen）；RFC 3207（STARTTLS）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/postfix-hardening-config.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
