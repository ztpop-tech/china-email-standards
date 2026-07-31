---
title: "Exim 邮件服务器的安全要点（ACL、TLS、防中继、宏风险）有哪些？"
source: "https://ztpop.net/kb/exim-config-security.html"
license: CC-BY 4.0
---

# Exim 邮件服务器的安全要点（ACL、TLS、防中继、宏风险）有哪些？

1
Exim 邮件服务器的安全要点（ACL、TLS、防中继、宏风险）有哪些？
▼

**ACL**

Exim 用 acl\_smtp\_rcpt / acl\_smtp\_mail / acl\_smtp\_data 控制“谁可发、收、中继”；必须显式拒绝“非授权中继”，仅 trusted\_networks/authenticated 可外发。

**TLS**

用 tls\_certificate/tls\_privatekey 启用 STARTTLS（tls\_advertise\_hosts=\*）；现代 Exim 默认要求 TLS 1.2+，禁用弱协议。

**宏与扩展**

Exim 配置强表达力但复杂，expand 字符串需防注入；谨慎使用 ${run}、外部查表，避免配置级命令执行风险。

**实践**

保持版本最新（历史有多起 Exim CVE，如 RCE）；最小化可选特性；用 ratelimit/acl 限流与拦垃圾；变更后 exim -bV 校验配置。

参考：Exim 官方文档（ACL、TLS、spec）；CVE 安全公告

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/exim-config-security.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
