---
title: "M3AAWG SPF 记录管理最佳实践"
source: "https://ztpop.net/kb/m3aawg-managing-spf-records.html"
license: CC-BY 4.0
---

# M3AAWG SPF 记录管理最佳实践

## 一、引言

SPF（Sender Policy Framework，发件人策略框架）是一种允许域所有者通过在 DNS 中发布标准 TXT 记录来声明哪些系统有权代表该域名发送邮件的机制。它为反滥用提供了一项强有力的工具，能够防止域名被伪造（spoofing）及未经授权的发信行为。此外，SPF 还能帮助大型邮件接收方为域名建立信誉评价，进而提升非滥用域名的邮件送达率。

然而，发布错误的 SPF 记录可能带来严重的非预期后果——使域名容易遭受邮件滥用。本文档涵盖以下内容：如何正确构造和维护 SPF 记录的最佳实践、常见错误及其非预期后果。

**原文来源：**M3AAWG Best Practices for Managing SPF Records, August 2017 © M3AAWG。本文为中文意译，保留所有 RFC 引用和技术示例。

## 二、错误配置的后果

一个域的 SPF 记录本质上是一项公开策略，用于声明谁可以代表该域发送邮件。发布**过度宽松**的 SPF 记录：可能允许未授权的来源使用该域名发送邮件，从而损害该域名的信誉，甚至导致域名被列入黑名单（blocklist）。发布**过度严格**的 SPF 记录：可能导致合法邮件被拒收或被过滤为垃圾邮件。

因此，SPF 记录的正确性是一项关键的安全控制措施，绝不应掉以轻心。

## 三、如何构造 SPF 记录

以下是构造一个正确 SPF 记录的标准步骤：

1. **确保记录以 `v=spf1` 开头。**这是 SPF 格式标识，缺少该标记的记录将被视为无效。
2. **列出内部管理的发信系统。**识别那些使用该域名发送邮件的内部管理系统，并使用 `ip4` 和 `ip6` 指令列出它们的 IP 地址或 IP 段。
3. **识别第三方发件方。**对于代表该域发送邮件的第三方服务（如邮件营销平台、CRM 系统等），使用该服务商推荐的 `include:` 参数。
4. **确保记录以 `~all` 或 `-all` 收尾。**这样可以确保任何未被前面规则匹配的 IP 地址都不被允许为该域发送邮件。大多数接收方对 `~all`（软失败）和 `-all`（硬失败）的处理方式相似，但某些接收方在后一种情况下更有可能直接拒绝未认证邮件。
5. **确保新 SPF 记录是该域唯一发布的 SPF 记录。**删除该域名下所有其他 SPF 记录——多个 SPF 记录并存会导致解析结果无法预测。

**补充建议：**考虑通过发布 DMARC 记录来获取认证报告，从而验证所有合法发件方是否都已被 SPF 正确认证。DMARC 的聚合报告可以反馈 SPF 认证通过率及未认证来源，是 SPF 运维闭环的关键工具。详见我们之前的文章 [DMARC 完全指南](/kb/dmarc-guide.html)。

## 四、典型记录示例

以下是从最严格到最常见配置的 SPF 记录示例：

| 描述 | SPF 记录 |
| --- | --- |
| 从不发信的域 | `"v=spf1 -all"` |
| 单个 IP 授权 | `"v=spf1 ip4:192.0.2.50 -all"` |
| CIDR 网段授权 | `"v=spf1 ip4:192.0.2.50/29 -all"` |
| IPv6 网段授权 | `"v=spf1 ip6:1080::8:800:200C:417A/121 -all"` |
| 单一第三方 include | `"v=spf1 include:_spf.example.com -all"` |
| 多第三方 include（~all） | `"v=spf1 include:_spf.example.com include:example.net ~all"` |
| 混合多网段 + include | `"v=spf1 ip4:192.0.2.0/24 ip4:198.51.100.17 include:_spf.example.com ~all"` |

## 五、常见问题详解

### 5.1 语法问题

* **多条 SPF 记录同时存在：**同一个域在 DNS 中发布了多条 SPF 记录，导致接收方解析行为不一致。
* **不可解析的主机名：**`include:` 或 `a:`/`mx:` 中引用的域名无法在 DNS 中解析。
* **DNS 查询超限：**`include`、`a` 和 `mx` 指令各计入一次 DNS 查询。SPF 标准限制不超过 **10 次 DNS 查询**。超出该限制的记录将产生 `PermError`（永久错误），导致 SPF 验证直接失败。
* **`all` 指令出现在记录中间：**`all` 应该总是最后一个机制，前置的 `all` 会使后续所有规则失效。
* **DNS 语法错误：**SPF 记录中包含无效字符或错误的引号格式。
* **错误使用 SPF RR 类型：**SPF 记录应使用 **TXT 记录类型**，而非已被废弃的 DNS SPF 资源记录类型（RR type 99）。
* **`Redirect` 指令使用不当：**`redirect=` 若放在 `all` 之前，可能意外覆盖整条策略。

**关于 10 次 DNS 查询限制：**这是国内企业最常踩的坑之一。每添加一个 `include:`，就计入一次查询；如果被 `include` 的记录本身又包含多个 `include`，这些嵌套查询也计入总数。我们见过多个知名 SaaS 的 `include` 链加起来超过 10 次，导致 SPF `PermError`。详见我们的 [SPF PermError 诊断指南](/kb/spf-permerror-diagnostic.html)。

### 5.2 过度授权

* **使用 `+all`：**等价于不设防，允许任何 IP 发送邮件。在 2026 年的邮件生态中，这等于主动欢迎伪造邮件。
* **授权大段 IP 范围：**使用 `/16` 甚至更宽的子网掩码，一次性授权意味着授权了数万个 IP。这不仅极大降低 SPF 的信誉价值，还可能在运营商 IP 地址重新分配后产生盲区。
* **使用未经过审查的第三方 `include`：**直接将外部服务商的 SPF 记录不加审查地包含进来。如果该服务商被攻破或其策略过于宽松，等于为攻击者敞开大门。

### 5.3 其他混淆点

* **SPF 验证的域是 Return-Path 地址：**SPF 验证的是 RFC5321 中的 `MAIL FROM`（即信封发件人/Return-Path），而非邮件头部的 `From:` 字段。两者常被混淆——即便 SPF 检验通过，攻击者仍可伪造头部 `From:`。这就是为什么需要 DMARC 的 SPF Alignment 来将两者关联。
* **SenderID 已废弃：**微软提出的 SenderID（基于 PRA 验证）已被业界弃用，不应再作为认证手段。
* **循环引用：**SPF 记录中不应出现循环包含（A include B，B include A），否则会导致解析失败。
* **不再推荐使用 `a` 和 `mx` 指令：**这两个指令各自计入一次 DNS 查询（加上可能的额外 A/AAAA 查询），消耗查询配额。如果发件 IP 与域名 A 记录或 MX 记录关联不一致，可能导致认证失败。建议尽可能使用具体的 `ip4`/`ip6` 替代。
* **`a` 和 `mx` 指令的 DNS 查询计数：**它们不仅指令本身计入 10 次查询，还可能需要额外解析 A 或 AAAA 记录。

## 六、实施建议

### 6.1 实施要点

1. **只授权实际发信的 IP 或 IP 段。**不要为了方便而盲目添加"整个办公室段"。每个授权的 IP 都应是经过确认的邮件发送源。
2. **保护不发信的域名。**对于不需要发送邮件的域名（如品牌保护域、公司官网域等），发布 `"v=spf1 -all"`。这将明确告知接收方：此域名从不发送邮件，任何以该域名义发出的邮件必为伪造。详见 [M3AAWG 停放域名最佳实践](/kb/m3aawg-parked-domains-bcp.html)。
3. **除非绝对必要，避免使用 `a` 或 `mx` 指令。**优先使用具体的 IP 地址范围。
4. **不要使用 `ptr` 指令。**`ptr` 机制已被 RFC 7208 标记为废弃（DEPRECATED），因为它依赖反向 DNS 查询，既不可靠又产生大量额外 DNS 查询开销，且已被所有主流邮箱服务商弃用。
5. **谨慎对待 SPF 宏和 `exists` 指令。**SPF 宏（如 `%{i}`、`%{s}`、`%{d}`）和 `exists` 机制增加了 SPF 的复杂度和安全风险。滥用宏展开可能导致意外的授权范围扩张。

### 6.2 持续监控

1. **定期审计 SPF 记录。**确保记录内容与当前发件架构保持一致。当新增发件服务器、更换邮件服务商或 IP 重分配时，应及时更新 SPF 记录。
2. **利用 DMARC 聚合报告检测 SPF 错误和伪造行为。**DMARC 聚合报告（RUA 报告）会展示哪些 IP 通过了 SPF 检查、哪些未通过，是发现 SPF 配置错误和及时发现伪造邮件的最佳手段。详见 [DMARC 聚合报告解析完全指南](/kb/dmarc-aggregate-reporting.html)。

## 七、国内场景补充

在中国企业的实际部署中，我们发现以下 SPF 配置问题尤为突出，值得额外注意：

* **10 次 DNS 查询限制频发：**国内企业在使用阿里企业邮箱、腾讯企业邮、网易企业邮、SendCloud 等多家邮件发送服务时，常通过 `include:` 堆叠多个服务商的 SPF 记录。每个 `include` 引入一次查询；如果被包含的服务商记录本身又包含其他 `include`，嵌套查询极易耗尽 10 次配额。建议使用 SPF 扁平化工具（如 `spf-tools`）将嵌套的 `include` 展开为具体的 `ip4`/`ip6` 列表。详见 [SPF PermError 诊断指南](/kb/spf-permerror-diagnostic.html) 和 [SPF 排错指南](/kb/spf-troubleshooting.html)。
* **长期未使用 `-all`：**大量企业仍在 SPF 记录末尾使用 `?all`（中性）甚至省略 `all`，事实上等同于对未授权发信不设限制。Gmail、Outlook 等主流邮箱已在 2024 年起加强了对 SPF 策略的遵循——使用 `?all` 的域名 IP 将面临更高的垃圾邮件评分。建议至少升级为 `~all`，并在确认无遗留问题后切换为 `-all`。参考 [SPF/DKIM/DMARC 部署检查清单](/kb/spf-dkim-dmarc-checklist.html)。
* **DMARC 报告未充分利用：**许多国内企业仅配置了 SPF 记录，却没有配套部署 DMARC 并启用聚合报告。这导致无法发现 SPF 配置中的漏洞——比如遗漏了某个合法的第三方发件服务。缺少报告的 SPF 运维就像没有仪表盘的驾驶。详见 [DMARC 聚合报告解析方法](/kb/dmarc-aggregate-report-parsing.html)。
* **混合部署场景的 SPF 管理：**在从 Exchange 迁移至国产邮件系统的过程中，新旧系统并存期间容易出现 SPF 记录遗漏。建议在邮件迁移前，先梳理所有发件源 IP，发布完整的 SPF 记录并设置 `~all` 监控一段时间，再切换为 `-all`。详见 [Exchange 迁移规划框架](/kb/exchange-migration-planning-framework.html)。

## 八、总结

SPF 是邮件认证体系的三大支柱之一（与 DKIM、DMARC 并列），但其配置的正确性直接影响域名的邮件安全与送达率。一个精心构建的 SPF 记录应当：以 `v=spf1` 开头，只列出实际发信源，使用 `~all` 或 `-all` 收尾，严格控制在 10 次 DNS 查询以内，并定期通过 DMARC 聚合报告进行验证。

M3AAWG 的核心建议可以用一句话概括：**只授权你信任的，拒绝你之外的。**

### 相关文章

* [SPF 发件人策略框架深度解析 — RFC 7208](/kb/spf-guide.html)：从语法到运维的完整指南
* [SPF PermError 诊断指南](/kb/spf-permerror-diagnostic.html)：超出 10 次 DNS 查询限制的解决方案
* [SPF 排错指南](/kb/spf-troubleshooting.html)：常见 SPF 问题与排查步骤
* [SPF/DKIM/DMARC 部署检查清单](/kb/spf-dkim-dmarc-checklist.html)
* [DMARC 聚合报告解析完全指南](/kb/dmarc-aggregate-reporting.html)
* [M3AAWG 邮件认证推荐最佳实践：SPF/DKIM/DMARC/ARC 落地清单](/kb/m3aawg-email-auth-best-practices.html)
* [M3AAWG 停放域名最佳实践](/kb/m3aawg-parked-domains-bcp.html)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/m3aawg-managing-spf-records.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
