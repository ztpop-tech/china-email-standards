---
title: "如何检测与防止开放中继（Open Relay）？"
source: "https://ztpop.net/kb/open-relay-detection-prevention.html"
license: CC-BY 4.0
---

# 如何检测与防止开放中继（Open Relay）？

1
如何检测与防止开放中继（Open Relay）？
▼

**什么是开放中继**

开放中继指 MTA 接受并转发「发件域与收件域均非本域」的邮件，即对任意外部双方提供中转。这会被垃圾邮件发送者滥用，使你的服务器 IP 迅速进入黑名单（DNSBL），损害正常投递信誉。现代 MTA 默认应关闭开放中继。

**检测方法**

从外部网络（非信任网段）用 `telnet mx 25` 或 `swaks` 发起会话：`MAIL FROM: attacker@external.com` 发给 `RCPT TO: victim@other.com`（第三方域）。若服务器返回 25x 接受而非 5xx 拒绝，即为开放中继。也可使用公开的 open-relay 测试服务或 `nmap` 脚本辅助。务必在获得授权的前提下对自身服务器测试。

**防护措施**

①提交端口（587）强制 SASL 认证，仅认证用户可外发；②不在 `mynetworks`/中继白名单中放行不可信网段，禁止仅依据信封发件人域名就中继；③将端口 25 入站限制为「仅收本地域」，外发仅经认证 MSA；④启用防滥用限速与 TLS；⑤定期用上述探测做自测并监控 IP 是否出现在 DNSBL。对必须中继的合作伙伴，采用基于 IP+SMTP AUTH 的显式授权而非全网开放。

参考：RFC 5321《SMTP》中继模型、Spamhaus 开放中继风险说明、Postfix《中继与访问控制》文档。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/open-relay-detection-prevention.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
