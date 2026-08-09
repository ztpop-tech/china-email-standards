---
title: "MTA-STS 的 enforce 模式该怎么部署？从 testing 切到 enforce 的判定条件是什么？"
source: "https://ztpop.net/kb/cfg-tls-enforce-mta-sts.html"
license: CC-BY 4.0
---

# MTA-STS 的 enforce 模式该怎么部署？从 testing 切到 enforce 的判定条件是什么？

**MTA-STS 解决什么问题**

RFC 8461 定义的 MTA-STS 是一种让收件域声明「本域支持 TLS、且 MX 必须通过证书校验」的机制。它针对的是 STARTTLS 可被中间人剥离、以及 MX 记录可被篡改这两类降级攻击：发送方一旦缓存了收件域的 MTA-STS 策略，就会在后续投递中拒绝接受不符合策略的连接，而不是无声回落到明文。

**第一步：发布 DNS TXT 记录**

在 `_mta-sts.<域名>` 发布 TXT 记录，格式为 `v=STSv1; id=<策略版本号>`。id 是一个策略版本标识，策略文件每次变更都必须同步改 id，否则发送方会继续用缓存中的旧策略。常见做法是用时间戳（如 `id=20260808T120000`）保证单调递增、便于排查。

**第二步：发布 HTTPS 策略文件**

策略文件必须放在 `https://mta-sts.<域名>/.well-known/mta-sts.txt`，由一张对 `mta-sts.<域名>` 有效的 WebPKI 证书保护——这是 MTA-STS 的信任根，不依赖 DNSSEC。文件为纯文本键值对，包含 `version: STSv1`、`mode:`、若干行 `mx:`、以及 `max_age:`（缓存秒数）。mx 行可用通配，如 `mx: *.example.net`。

**三种 mode 的行为差异**

`mode: none` 表示本域声明不再有策略，用于干净下线；`mode: testing` 表示发送方在校验失败时仍应正常投递，但应通过 TLS-RPT 上报失败；`mode: enforce` 表示校验失败时发送方不得投递到该 MX。换句话说，testing 只观测不拦截，enforce 才真正提供防降级保护。

**从 testing 切 enforce 的判定条件**

建议同时满足以下几条再切换：一是全部 MX 主机的证书都覆盖了 mx 行中声明的名字，且证书链完整、未过期；二是 TLS-RPT 报告连续观测一段完整周期（覆盖证书轮换与运维变更窗口）后，failure 计数为零或仅剩已定位的可解释来源；三是 mx 列表与实际 MX 记录逐条核对一致，包含灾备 MX 与第三方代收节点——遗漏任何一台，切 enforce 后寄往该节点的邮件会被发送方直接拒投。

**max\_age 的灰度与回滚含义**

max\_age 决定发送方缓存策略的时长，上限为 31557600 秒（约一年）。灰度期建议先设一个较短的值（例如数小时到一天），确认稳定后再逐步调大。这一点在回滚时尤其关键：因为发送方按缓存执行，改回 testing 并不会立刻生效，仍在 max\_age 内的发送方会继续按旧的 enforce 策略拒投。所以「先短后长」是可回滚部署的前提。

参考：[RFC 8461 SMTP MTA Strict Transport Security](https://www.rfc-editor.org/rfc/rfc8461.html) ｜ [RFC 7817 Updated TLS Server Identity Check Procedure for Email](https://www.rfc-editor.org/rfc/rfc7817.html)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/cfg-tls-enforce-mta-sts.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
