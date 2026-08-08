---
title: "Postfix 如何用 per-destination TLS 策略映射（tls_policy_maps）控制按目标域的 TLS？"
source: "https://ztpop.net/kb/postfix-smtp-tls-policy-maps-per-destination.html"
license: CC-BY 4.0
---

# Postfix 如何用 per-destination TLS 策略映射（tls_policy_maps）控制按目标域的 TLS？

1
Postfix 如何用 per-destination TLS 策略映射（tls\_policy\_maps）控制按目标域的 TLS？
▼

**配置方式**

在 main.cf 设 smtp\_tls\_policy\_maps = hash:/etc/postfix/tls\_policy（或 lmdb/cidr），表中每行形如 [mx.example.com] encrypt 或 example.com secure match=nexthop，按目标域（或目的 IP/主机）声明 TLS 要求。

**策略等级**

none（不强制）；may（opportunistic，能加密就加密）；encrypt（必须加密，否则不发送）；secure（必须加密且证书需匹配）；dane（基于 DNS 的 DANE TLSA 校验）；verify（证书需由信任 CA 签发并匹配主机名）。可附加 match=（校验主机名方式）、ciphers=（密码等级）等。

**如何取舍**

encrypt 可防止明文泄露，但无法防中间人；secure/verify/dane 进一步校验对端证书，适合与已知伙伴的邮件。Opportunistic（may）是默认安全提升，不会因对方不支持 TLS 而丢信。

参考：Postfix 官方文档 TLS\_README（smtp\_tls\_policy\_maps 与策略等级）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/postfix-smtp-tls-policy-maps-per-destination.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
