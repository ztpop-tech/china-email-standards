---
title: "MTA-STS 策略如何部署与验证？"
source: "https://ztpop.net/kb/mta-sts-policy-deployment.html"
license: CC-BY 4.0
---

# MTA-STS 策略如何部署与验证？

1
MTA-STS 策略如何部署与验证？
▼

**发布 DNS 策略**

在域下发布 `_mta-sts.<domain>` 的 TXT 记录，含版本、`id`（策略变更后必须更新以便对端刷新）与可选 `rua` 报告地址，例如 `v=STSv1; id=20260803100000; rua=mailto:tlsrpt@<domain>`。该记录本身仅声明「有策略」，真正的策略内容放在 HTTPS 上。

**托管策略文件**

在 `https://mta-sts.<domain>/.well-known/mta-sts.txt` 提供策略文件，含 `version: STSv1`、`mode`（`none` 仅观测、`test` 记录但不强制、`enforce` 强制）、`mx:` 白名单（列出允许的 MX 主机名）、`max_age:`（策略缓存秒数，建议 ≥604800）。`mode=enforce` 时，发送方若无法对列出的 MX 建立有效 TLS，必须放弃明文投递并报错。

**验证步骤**

①`dig _mta-sts.<domain> TXT` 确认策略存在且 id 最新；②`curl -I https://mta-sts.<domain>/.well-known/mta-sts.txt` 确认 HTTPS 可达、证书有效、内容合规；③用 `swaks --tls --to user@<domain>` 或 `openssl s_client -starttls smtp -connect mx:25` 验证 MX 支持 STARTTLS 且证书匹配；④观察 TLS-RPT 报告确认无 `starttls-not-supported` 失败。注意：MTA-STS 依赖发送方实现，且 HTTPS 证书需可信 CA 签发。

参考：RFC 8461《SMTP MTA Strict Transport Security》、RFC 8460《TLS-RPT》、RFC 6125《证书身份校验》。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/mta-sts-policy-deployment.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
