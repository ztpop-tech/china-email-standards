---
title: "DANE 和 MTA-STS 应该选哪个？两个能同时部署吗？"
source: "https://ztpop.net/kb/cfg-dane-or-mta-sts-selection.html"
license: CC-BY 4.0
---

# DANE 和 MTA-STS 应该选哪个？两个能同时部署吗？

**两者解决同一个问题，但信任根不同**

DANE（RFC 7672）与 MTA-STS（RFC 8461）都用于阻止 SMTP 传输被降级到明文，区别在于「凭什么相信这份声明」。DANE 把 TLSA 记录放在 DNS 中，由 DNSSEC 签名保证真实性；MTA-STS 把策略放在 HTTPS 上，由 WebPKI 证书体系背书。这一差异决定了两者几乎全部的取舍。

**DANE 的前置条件是 DNSSEC**

DANE 的安全性完全建立在 DNSSEC 之上：TLSA 记录必须处于签名区域，且发送方需要具备做验证的解析能力。若域名未签名，TLSA 记录不提供任何保护。因此选型的第一个判定点很直接——你的权威 DNS 是否已启用 DNSSEC、是否有能力承担密钥轮换（KSK/ZSK rollover）与签名过期的运维责任。签名过期会导致域名整体解析失败，其影响面远大于邮件本身。

**MTA-STS 的前置条件是一张证书和一个 HTTPS 站点**

MTA-STS 不要求 DNSSEC，只要求能在 `mta-sts.<域名>` 上提供一个由受信任 CA 签发证书保护的 HTTPS 站点，用于分发策略文件。这大幅降低了部署门槛，代价是引入了缓存语义：策略按 max\_age 缓存，变更不会立即对所有发送方生效，回滚存在滞后。

**失败模式的差异**

DANE 的校验是每次连接实时进行的，改了 TLSA 记录、等 DNS TTL 过去即可生效，回滚较快；但 DNSSEC 一旦出问题，影响的是整个域名。MTA-STS 的失败更局部——策略站点挂掉时，未缓存的发送方取不到策略、按无策略处理，已缓存的发送方继续按旧策略执行；但正因为缓存，错误策略的影响会持续到 max\_age 结束。简单说：DANE 是「快但脆」，MTA-STS 是「稳但钝」。

**选型判定**

已经运行 DNSSEC、且团队有相应运维能力的，优先 DANE，它的实时性与防降级强度更好；尚未启用 DNSSEC、或不愿承担签名运维风险的，选 MTA-STS，它能在不动 DNS 信任链的前提下拿到防降级能力。如果条件允许，两者同时部署是被推荐的做法——它们面向的是不同能力的发送方，支持 DANE 的按 DANE 走，不支持的按 MTA-STS 走，覆盖面相加。

**双栈共存的注意事项**

同时部署时最关键的一条是保持两边声明一致：MTA-STS 策略中的 mx 列表、TLSA 记录所绑定的证书、以及实际 MX 记录三者必须同步维护。证书轮换尤其容易出错——需要先发布新的 TLSA 记录并等待 TTL 过期，再切换证书，顺序颠倒会造成校验失败。建议把证书轮换与 TLSA/策略更新固化为同一套流程，并全程通过 TLS-RPT 观测两类策略各自的失败计数。

参考：[RFC 7672 SMTP Security via Opportunistic DANE TLS](https://www.rfc-editor.org/rfc/rfc7672.html) ｜ [RFC 8461 SMTP MTA Strict Transport Security](https://www.rfc-editor.org/rfc/rfc8461.html) ｜ [RFC 8460 SMTP TLS Reporting](https://www.rfc-editor.org/rfc/rfc8460.html)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/cfg-dane-or-mta-sts-selection.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
