---
title: "MTA-STS（RFC 8461）部署有哪些陷阱？"
source: "https://ztpop.net/kb/rfc8461-mta-sts-deployment-traps.html"
license: CC-BY 4.0
---

# MTA-STS（RFC 8461）部署有哪些陷阱？

1
MTA-STS（RFC 8461）部署有哪些陷阱？
▼

**记录与策略文件**

§3.1：在 Policy Domain 下发布 `_mta-sts.<domain>` 的 TXT 记录，格式 `"v=STSv1; id=20160831085700Z;"`，**必须以 `v=STSv1;` 开头**。§3.2/3.3：策略文件经 HTTPS GET 取自 `https://mta-sts.<domain>/.well-known/mta-sts.txt`，媒体类型应为 `text/plain`。

**策略字段语义**

字段含 `version`（仅 STSv1）、`mode`（enforce/testing/none，必填）、`mx`（至少一条，mode=none 除外，支持 `*.example.net` 左标签通配）、`max_age`（非负秒，上限 31557600）。§4.1 明确通配符 `*.example.com` 仅匹配 `mail.example.com`，不匹配 `example.com` 或 `foo.bar.example.com`。

**校验与报告**

§4/5：发送方对有效策略需做 MX 主机名匹配与证书校验（§4.2，须 SNI、含匹配 DNS-ID、可经 OCSP/CRL 查吊销）。`enforce` 下校验失败 MUST NOT 投递；`testing` 下仍投递但应报告；`none` 视为无活跃策略。失败报告经由 TLSRPT（RFC 8460）的 `rua` 机制，而非 DMARC 的 rua。

**部署陷阱**

§8/10 列出高频坑：① `mx: *.example.com` 会让任何持有合法证书的主机（如 `dhcp-123.example.com`）成为有效 MX；② 退出应先 `mode: none` 配小 `max_age`（如 1 天）再撤端点（§8.3）；③ 更新顺序须**先改 HTTPS 策略体、再改 TXT 的 id**（§8.1），否则发送方可能缓存旧策略；④ 子域只从其自身取策略，不向上父域；⑤ 长 max\_age 可抗策略发现阻断，但更新须等 TTL 过期。

参考：RFC 8461（SMTP MTA Strict Transport Security），https://www.rfc-editor.org/rfc/rfc8461 —— 章节 3.1 / 3.2 / 3.3 / 4 / 5 / 6 / 8 / 10

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/rfc8461-mta-sts-deployment-traps.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
