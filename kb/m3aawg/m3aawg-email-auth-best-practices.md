---
title: "M3AAWG 电子邮件认证推荐最佳实践——SPF/DKIM/DMARC/ARC 配置检查清单"
source: "https://ztpop.net/kb/m3aawg-email-auth-best-practices.html"
license: CC-BY 4.0
---

# M3AAWG 电子邮件认证推荐最佳实践——SPF/DKIM/DMARC/ARC 配置检查清单

#### 📑 目录

1. [摘要](#s1)
2. [引言](#s2)
3. [发送方最佳实践](#s3)
4. [中介机构最佳实践](#s4)
5. [接收方最佳实践](#s5)
6. [结论](#s6)
7. [参考文献与延伸阅读](#s7)

## 一、摘要

本文档基于 M3AAWG（Messaging, Malware and Mobile Anti-Abuse Working Group）**电子邮件认证推荐最佳实践**（M3AAWG-134，2020 年 9 月发布），系统性地梳理了使用安全协议进行电子邮件认证的配置要求与操作指南。涵盖以下四大协议：

* **SPF**（Sender Policy Framework，RFC 7208）——授权发信源验证
* **DKIM**（DomainKeys Identified Mail，RFC 6376）——消息完整性签名
* **DMARC**（Domain-based Message Authentication, Reporting, and Conformance，RFC 7489）——策略执行与报告
* **ARC**（Authenticated Received Chain，RFC 8617）——多跳认证链传递

文章面向三类目标受众分别给出检查清单：**原始发送方**（邮件运营商）、**中介机构**（转发服务和邮件列表）和**接收方**（邮件提供商）。每部分末尾附有国内邮件系统场景的补充说明。

## 二、引言

电子邮件认证技术自 21 世纪初逐步发展至今，已经从"可选增强"演变为"行业基本要求"。全球主流邮箱服务商（Gmail、Outlook.com、Yahoo Mail、QQ 邮箱、163 邮箱、阿里邮箱等）均已全面部署认证检查，未通过 SPF/DKIM/DMARC 的邮件面临较高的拒绝或投递到垃圾箱的风险。

M3AAWG 作为全球重要的反垃圾邮件和消息安全组织，定期发布行业最佳实践文档。M3AAWG-134 自 2020 年发布以来，因其明确的角色分工和可执行的操作清单，被业界广泛采纳作为电子邮件认证的参考基准。

本文在忠实翻译原文核心检查清单的基础上，结合中国邮件生态的特点，在每部分加入「国内场景补充」小段，帮助国内邮件系统运营者更好地落地执行。

## 三、发送方最佳实践

发送方（原始发件邮件运营商）是认证链的起点。发送方对 SPF、DKIM 和 DMARC 的配置质量，直接决定了最终收件端对邮件的信任度。

### 3.1 SPF 配置要求

表 1：SPF 发送方检查清单

| # | 操作项 | 说明 |
| --- | --- | --- |
| 1 | 为 MAIL FROM 和 EHLO 域发布 SPF 记录 | 对于所有发送邮件的域，必须在 DNS 中发布有效的 SPF TXT 记录，覆盖 MAIL FROM 和 EHLO 阶段使用的域。 |
| 2 | SPF 记录应以 `~all` 结尾 | `~all`（softfail）作为推荐的最低配置，`-all`（fail）适用于已充分枚举发信源的场景。 |
| 3 | 不应授权超过必要的 IP | 仅授权实际发信的 IP 地址范围，避免因过度授权增加伪造风险。 |
| 4 | MAIL FROM 域应与 RFC5322.From 域对齐 | 尽可能使用与 Header From 域一致的 MAIL FROM 域，以提高 DMARC 的对齐通过率。 |
| 5 | 为不发送邮件的域发布 SPF `v=spf1 -all` | 对于纯粹展示用途或停放域名，使用硬失败策略以阻止伪造。 |

```
; 示例：发送域 example.com 的 SPF 记录
example.com.  IN  TXT  "v=spf1 ip4:192.0.2.0/24 ip4:198.51.100.10 include:_spf.google.com ~all"

; 示例：不发送邮件的域 parked-example.com
parked-example.com.  IN  TXT  "v=spf1 -all"
```

### 3.2 DKIM 配置要求

表 2：DKIM 发送方检查清单

| # | 操作项 | 说明 |
| --- | --- | --- |
| 1 | 用与 RFC5322.From 域对齐的域签署所有出站邮件 | 签名域（d=）应与 Header From 域一致，确保 DKIM 对齐。 |
| 2 | 遵循密钥管理最佳实践 | 定期的密钥轮换（建议 3-6 个月）、避免 RSA 512/768 位等已知短密钥。推荐 RSA 2048 位或 Ed25519（RFC 8463）。 |
| 3 | ESP 应双重签署 | 邮件服务提供商应同时使用自己的域和客户域进行签名，确保在客户域尚未完成 DKIM 部署时仍有一定认证保障。 |
| 4 | 每个客户使用不同的 DKIM 密钥 | 多租户 ESP 必须为每个客户分配独立的选择器/密钥对，防止跨租户的安全风险。 |
| 5 | 签署合理的头字段 | 按 RFC 6376 §5.4.1 要求，至少签署 From、Date、Subject、Message-ID、To 等关键头字段。 |

```
; 示例：DKIM 公钥记录（选择器 s1）
s1._domainkey.example.com.  IN  TXT  "v=DKIM1; h=sha256; k=rsa; p=MIGfMA0GCSqGSIb4..."

; 示例：DKIM 签名头（发件）
DKIM-Signature: v=1; a=rsa-sha256; c=relaxed/relaxed;
  d=example.com; s=s1; t=1721800000;
  bh=47DEQpj8HBSa+/TImW+5JCeuQeRkm5NMpJWZG3hSuFU=;
  h=From:Date:Subject:Message-ID:To;
  b=AwB5Bq2IwZkFwTio3hXMCfIu5TM4oEJjH4o...Cw==
```

### 3.3 DMARC 配置要求

表 3：DMARC 发送方检查清单

| # | 操作项 | 说明 |
| --- | --- | --- |
| 1 | 策略声明的目标设置为 `p=reject` | 长期目标应为 p=reject；若暂时无法达到则可接受 p=quarantine 作为过渡。 |
| 2 | `p=none`、`sp=none` 和 `pct<100` 仅应作为过渡状态 | p=none 仅用于监控和收集数据阶段，不应长期使用。 |
| 3 | 必须包含 `rua` 标签 | 聚合报告地址（rua）是获取认证数据的核心机制，必须配置。 |
| 4 | `ruf` 标签可选 | 法医报告（ruf）因包含邮件样本内容，涉及隐私合规考虑，可按需配置。 |

```
; 示例：渐进式 DMARC 部署

; 阶段 1 — 监控期 (p=none)
_dmarc.example.com.  IN  TXT  "v=DMARC1; p=none; rua=mailto:dmarc-rua@example.com; pct=100"

; 阶段 2 — 过渡期 (p=quarantine)
_dmarc.example.com.  IN  TXT  "v=DMARC1; p=quarantine; sp=quarantine; rua=mailto:dmarc-rua@example.com; pct=100"

; 阶段 3 — 最终状态 (p=reject)
_dmarc.example.com.  IN  TXT  "v=DMARC1; p=reject; sp=reject; aspf=s; adkim=s; rua=mailto:dmarc-rua@example.com; pct=100; ri=86400"
```

#### 📌 国内场景补充（发送方）

* 国内邮件系统通常通过 **25/465/587** 端口发送邮件。部署 SPF 时，需确认所有出站 MTA 的公网 IP 已包含在 SPF 记录中，特别是使用第三方邮件中继服务（如阿里云邮件推送、腾讯企业邮、网易企业邮）的情况，应使用对应的 `include:` 机制。
* QQ 邮箱和 163 邮箱的 DKIM 签名默认使用各自域（qq.com、163.com），而非常户自有域。如果客户使用自有域名发送，应确保完成自有域的 DKIM 配置，否则 DMARC 对齐可能失败。
* 国内部分邮件服务商默认使用 `p=none` 或根本未发布 DMARC 记录。建议尽快升级至 `p=quarantine` 或 `p=reject` 以提升域信誉。
* DMARC rua 报告建议使用能够接收中文域名的邮箱地址（如 `mailto:dmarc@example.com`），部分国内解析器对非 ASCII 字符支持不佳。

## 四、中介机构最佳实践

中介机构包括**转发服务**（如邮件转发、别名转发）、**邮件列表**（Mailing List）、以及**其他消息修改代理**（如反垃圾邮件网关、签名/加密网关、内容过滤器）。中介机构在传递邮件的过程中可能对原始消息进行修改，这些修改会破坏原始发件方的认证状态。

表 4：中介机构检查清单

| # | 操作项 | 说明 |
| --- | --- | --- |
| 1 | 尽量减少传输过程中的消息更改 | 将消息修改降至最低，尤其避免修改 From 头、Subject 等 DMARC 强相关的字段。 |
| 2 | 降低认证失败风险 | 对于转发场景（如邮件转发服务），实施 From 重写或 SRS（Sender Rewriting Scheme）以避免 SPF 失败。 |
| 3 | 实施 ARC | ARC（Authenticated Received Chain）允许中介机构在转发时保留原始认证结果，避免后续收件端因消息修改而拒绝。 |
| 4 | 生成 DMARC 报告 | 向原始发件域发送 DMARC 聚合报告，帮助原始发送方了解其邮件被转发后的认证状态。 |

### 4.1 转发场景的 SPF 问题

转发是最经典的 SPF 失败场景。当邮件从原始发件方发送至中间 MTA，再由中间 MTA 转发至最终收件方时，终端的 SPF 检查面对的是转发 MTA 的 IP，而非原始发件方的 IP——这通常导致 SPF 失败。

```
原始发送方 (SPF: 192.0.2.0/24)
     │ 发件: MAIL FROM <alice@example.com>
     ▼
接收 MTA --> 转发
     │ 新连接: MAIL FROM <alice@example.com> (from 转发 IP: 203.0.113.5)
     ▼
目标收件方
  SPF 检查: 203.0.113.5 vs example.com SPF → FAIL
```

**解决方案**：实施 ARC（见 4.2 节）或 SRS（Sender Rewriting Scheme，将 MAIL FROM 重写为转发域的子地址）。

### 4.2 ARC 实施要点

ARC（RFC 8617）通过三个头字段建立认证链：

* **ARC-Seal**：由当前中介对 ARC 链的完整性进行签名
* **ARC-Message-Signature**（AMS）：对当前消息的认证相关头进行签名
* **ARC-Authentication-Results**（AAR）：记录当前中介的认证结果

```
; ARC 链示例（Gmail 转发场景）
ARC-Seal: i=1; a=rsa-sha256; d=forwarder.example; s=arc2026;
  t=1721800000; cv=none; b=H4kD8p2...
ARC-Message-Signature: i=1; a=rsa-sha256; c=relaxed/relaxed;
  d=forwarder.example; s=arc2026; t=1721800000;
  h=from:date:subject:message-id;
  bh=uE3SCq...
ARC-Authentication-Results: i=1; mx.example;
  spf=pass smtp.mailfrom=example.com;
  dkim=pass header.d=example.com;
  dmarc=pass header.from=example.com
```

#### 📌 国内场景补充（中介机构）

* 国内企业邮箱迁移场景非常常见（如从自建 Postfix 迁移至腾讯企业邮、阿里邮箱等）。迁移过程中常涉及邮件转发或别名转发，此时需要特别关注 SPF 失败和 DMARC 失败问题。建议企业在迁移完成前配置 ARC 或使用 SRS。
* 邮件列表服务（如 Google Groups、钉钉群发邮件、企业微信群发邮件）在国内使用广泛。国内邮件列表服务商应考虑实施 ARC，以避免因 Message-ID 或 Subject 头修改导致的 DKIM 签名失效。
* 国内部分邮件安全网关（如阿里云邮件网关、Coremail 邮件安全网关）也扮演中介角色。这些网关在扫描附件或添加免责声明时的消息修改，均应在 ARC 链中记录原始认证状态。
* ARC 在国内的部署率仍然较低，但已获得主要海外服务商（Gmail、Yahoo、Outlook）的支持。国内邮件运营商部署 ARC 将显著改善来自海外中转邮件的投递率。

## 五、接收方最佳实践

接收方（邮件提供商）是认证链的最终执行者。接收方认证策略的合理性与一致性，直接影响整个邮件信任体系的完整性。

表 5：接收方检查清单

| # | 操作项 | 说明 |
| --- | --- | --- |
| 1 | 执行 SPF、DKIM 和 DMARC 认证检查 | 对所有入站消息执行完整的认证检查，这是接收方的基本职责。 |
| 2 | 遵守 DMARC 策略 | 按发布方指定的 p=/sp= 策略执行。覆盖（override）应不频繁，且必须有明确、记录的理由。 |
| 3 | DMARC pass 覆盖 SPF fail 裁决 | 当 DMARC 综合判定通过（即 DKIM 对齐通过）时，不应仅因 SPF 失败而拒绝邮件。 |
| 4 | 除非 SPF 记录为 `v=spf1 -all` | 仅当 SPF 记录明确为 "-all" 且授权集已知为空时，SPF 失败可独立引起拒绝。 |
| 5 | 发送 DMARC aggregate 报告 | 接收到 DMARC 策略的域后，应向 rua 地址发送聚合报告。 |
| 6 | 入站消息中处理 ARC 头 | 验证 ARC 链，用于在转发场景中决定认证结果的信任度。 |

### 5.1 DMARC 判定规则详解

DMARC 的判定以 OR 逻辑为核心：**SPF pass 且对齐** 或 **DKIM pass 且对齐**，满足任一即得 DMARC pass。这一设计确保即使 SPF 因转发场景而失败，只要 DKIM 验证通过且签名域与 From 域对齐，邮件仍能正常投递。

```
def dmarc_evaluate(spf_pass, spf_domain, dkim_results, from_domain, dmarc_record):
    """DMARC 综合判定 — OR 逻辑"""

    # SPF 对齐检查
    spf_aligned = domains_aligned(
        spf_domain, from_domain,
        strict=dmarc_record.get("aspf", "r") == "s"
    )

    # DKIM 对齐检查（任一签名通过即可）
    dkim_aligned = any(
        dkim["pass"] and domains_aligned(
            dkim["domain"], from_domain,
            strict=dmarc_record.get("adkim", "r") == "s"
        )
        for dkim in dkim_results
    )

    # OR 判定
    if (spf_pass and spf_aligned) or dkim_aligned:
        return "pass"
    return "fail"
```

### 5.2 "DMARC pass overrides SPF fail" 原则

这一原则是接收方实施中的关键细节。核心含义：**当 DKIM 对齐通过时，即使 SPF 未通过，DMARC 也应判为 pass**，不应因 SPF fail 直接拒绝邮件。

唯一例外：当 SPF 记录为 `v=spf1 -all`（硬失败）且该域不包含任何发信授权时，接收方可以选择忽略 DMARC pass 覆盖规则——但这属于"明知不可为而为之"类的极端情况，应极为谨慎。

### 5.3 接收方 ARC 处理策略

接收方在入站邮件中遇到 ARC 头时，应按以下步骤处理：

1. **验证 ARC 签名链**：从 i=1 到最大 i 值逐跳验证 ARC-Seal 和 AMS。
2. **评估 ARC 链信任度**：检查链是否完整、签名是否有效、cv（chain validation）状态。
3. **使用 ARC 结果**：对于 cv=pass 的 ARC 链，可用中间 MTA 的认证结果作为辅助判断依据。
4. **降级策略**：ARC 验证失败（cv=fail）不应自动导致拒绝，但应降低认证可信度。

#### 📌 国内场景补充（接收方）

* 国内邮箱服务商在 DMARC 策略执行的一致性上存在差异。部分国内邮箱在收到 `p=reject` 的 DMARC 策略后，仍将邮件投递至收件箱而非拒收。建议国内邮箱服务商完整实现 RFC 7489 的要求，**同时**考虑兼容国内用户的使用习惯。
* ARC 头在国内邮箱系统中的利用率仍不高。QQ 邮箱、163 邮箱等主流国内邮箱服务商尚未公开宣布 ARC 链验证支持，导致经转发服务（如 Apple Mail 的私人中继、Fastmail 转发）的邮件可能被误判。
* 中国互联网协会反垃圾信息中心（12321 网络不良与垃圾信息举报受理中心）在邮件认证方面的要求逐年加强。国内邮件服务商应关注工信部及 12321 的相关邮件安全指南更新。
* 国内 DMARC 聚合报告的接收和解析能力尚处于早期阶段。建议接收方部署标准的 DMARC 报告解析器（如 OpenDMARC、parsedmarc），并确保 rua 地址可以接收大体积的聚合报告附件。

## 六、结论

电子邮件认证已经从"加分项"演变成为维护邮件通道健康运行的**基本要求**。无论是原始发送方、中介机构还是接收方，完善的认证配置不仅保护自身域名的品牌信誉，也维护了整个邮件生态的安全性。

M3AAWG-134 检查清单的核心要点总结：

表 6：三类角色核心行动总结

| 角色 | 核心行动 | 优先级 |
| --- | --- | --- |
| 发送方 | 发布 SPF（~all）、签署 DKIM（域对齐）、部署 DMARC（p=reject 目标） | 高 |
| 中介机构 | 减少消息修改、实施 ARC、生成 DMARC 报告 | 中 |
| 接收方 | 执行完整认证检查、遵守 DMARC 策略、"DMARC pass overrides SPF fail"、支持 ARC | 高 |

对于国内邮件系统运营者而言，在遵循国际标准的同时，还需关注国内特有的邮件运维场景：企业的跨平台迁移、邮件列表的 ARC 实施、以及国内邮箱服务商在 DMARC 策略执行上的一致性。中国作为全球邮件市场的重要组成部分，在认证协议部署方面的提升将显著改善国内外邮件互通的可靠性。

下一步，建议读者进一步了解 **BIMI**（消息识别品牌指标，基于 DMARC pass 的品牌 Logo 展示）和 **MTA-STS**（SMTP MTA 严格传输安全，TLS 强制加密）——它们分别位于认证链的顶端和底层，共同构成完整的邮件安全体系。

## 七、参考文献与延伸阅读

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/m3aawg-email-auth-best-practices.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
