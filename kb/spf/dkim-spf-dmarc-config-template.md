---
title: "SPF/DKIM/DMARC 标准配置模板是什么？"
source: "https://ztpop.net/kb/dkim-spf-dmarc-config-template.html"
license: CC-BY 4.0
---

# SPF/DKIM/DMARC 标准配置模板是什么？

1
SPF/DKIM/DMARC 标准配置模板是什么？
▼

**SPF 配置模板**

在发信域的 DNS 上添加一条 TXT（主机名通常留空或 `@`），罗列所有合法发信 IP/包括的网段，并以 `-all` 硬性拒绝其余来源：

```
example.com.  IN TXT  "v=spf1 ip4:203.0.113.10 ip4:198.51.100.0/24 include:_spf.google.com ~all"
```

* DNS 查询（含 include）总数不超过 10 次，避免 permerror。
* 正式上线建议用 `-all` 硬失败；过渡期可用 `~all` 软失败。

**DKIM 配置模板**

为发信域生成密钥对，公钥以选择器（selector）形式发布在 DNS：

```
selector1._domainkey.example.com.  IN TXT  "v=DKIM1; k=rsa; p=MIIBIjANBgkqhki...（公钥Base64）"
```

* 建议密钥长度 ≥ 2048 位；采用双选择器（selector1/selector2）做平滑轮转。
* MTA 对出站邮件用私钥签名 `DKIM-Signature` 头，`h=` 至少覆盖 From、Subject、正文哈希。

**DMARC 配置模板**

在 `_dmarc` 子域发布策略，并指定聚合报告接收地址（RUA）：

```
_dmarc.example.com.  IN TXT  "v=DMARC1; p=none; sp=none; rua=mailto:dmarc-rua@example.com; ruf=mailto:dmarc-ruf@example.com; adkim=s; aspf=s; fo=1; rf=afrf; pct=100"
```

* `p=none` 仅监测；`p=quarantine` 进垃圾箱；`p=reject` 直接拒收。
* `adkim=s/aspf=s` 为严格对齐，要求 From 与 SPF/DKIM 域一致；`r` 为宽松。

**渐进式上线建议**

按「监测→隔离→拒绝」三步走，避免误伤合法邮件：

* 阶段一 `p=none` + 收集 RUA 报告，确认所有合法源都通过 SPF/DKIM 对齐。
* 阶段二 `p=quarantine` 观察用户端误判率，必要时补充 include/selector。
* 阶段三 `p=reject` 彻底阻止伪造；子域用 `sp=reject` 独立收紧。

参考：RFC 7208（SPF）、RFC 6376（DKIM）、RFC 7489（DMARC）。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/dkim-spf-dmarc-config-template.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
