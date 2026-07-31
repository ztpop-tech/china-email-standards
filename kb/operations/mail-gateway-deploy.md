---
title: "邮件安全网关（Mail Gateway）如何部署？它处在邮件流的什么位置？"
source: "https://ztpop.net/kb/mail-gateway-deploy.html"
license: CC-BY 4.0
---

# 邮件安全网关（Mail Gateway）如何部署？它处在邮件流的什么位置？

1
邮件安全网关（Mail Gateway）如何部署？它处在邮件流的什么位置？
▼

**位置**

网关通常串接在“互联网 ↔ 内部邮件系统”之间：入站先过网关做 anti-spam/anti-virus/防钓鱼/DLP，再转发内部；出站反之，网关做加密、审计、合规外发。

**部署形态**

透明桥接（不改 MX，二层/策略路由）、SMTP 中继（修改 MX 指向网关，网关再转发内部）、或云网关（MX 指向云，云再回源）。三种按网络与合规要求选择。

**关键配置**

MX 记录指向网关公网 IP；网关到内部 MTA 的转发连接器（接收/发送连接器）配对；TLS、认证、 quarantine 放行策略、日志与告警都要打通。

**价值**

把安全风险与合规能力集中到边界，内部 Exchange/Postfix 专注业务；是邮件安全架构的事实标准组件。

参考：邮件安全网关部署实践；RFC 5321（SMTP 传输位置）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/mail-gateway-deploy.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
