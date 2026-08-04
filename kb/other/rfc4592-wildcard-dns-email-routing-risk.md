---
title: "通配符 DNS 记录会对邮件路由和反垃圾造成什么影响？"
source: "https://ztpop.net/kb/rfc4592-wildcard-dns-email-routing-risk.html"
license: CC-BY 4.0
---

# 通配符 DNS 记录会对邮件路由和反垃圾造成什么影响？

1
通配符 DNS 记录会对邮件路由和反垃圾造成什么影响？
▼

**通配符的合成规则常被误解**

通配符记录（形如 `*.example.com`）的行为比多数人以为的复杂。RFC 4592（2006 年 7 月）正是为澄清这些语义而制定，它更新了 RFC 1034 中关于通配符的描述。几条最常被误解的规则：

* **通配符只在没有匹配名字时才合成**：若查询名在区中已经存在（哪怕只存在其他类型的记录），通配符**不会**为该名字合成应答。这一点极其关键，是下文「保护失效」的根源。
* **合成是按类型进行的**：`*.example.com IN MX ...` 只对 MX 查询合成应答，对该名字的 A 查询不产生 MX 之外的结果。
* **星号只能是最左标签**：只有出现在名字最左端的 `*` 才具有通配符语义；出现在中间位置的星号是一个普通字面标签。
* **不跨越已存在的名字向下延伸**：若 `a.example.com` 存在，则 `x.a.example.com` 不会由 `*.example.com` 合成——包括仅作为「空非终端」存在的中间名字，也会阻断通配符的覆盖。

这些规则合在一起，导致通配符的实际覆盖范围往往**既比管理员预期的大（覆盖了所有未预料的名字），又比预期的小（在已存在名字的分支下失效）**。这种双向偏差正是配置事故的温床。

**通配符 MX 带来的具体风险**

发布 `*.example.com IN MX 10 mail.example.com.` 意味着：**任意一个不存在的子域，在邮件语义上都是「可收信」的。**由此产生几类问题：

* **无限的收件域面**：`anything.example.com`、`login-verify.example.com`、`随机串.example.com` 全部指向本方邮件服务器。垃圾发送方可以用无穷多的子域作为收件目标，制造回散射与投递噪声。
* **子域伪造的落点**：攻击者伪造一个看起来属于本组织的子域地址用于社工。虽然发信侧的合法性由 SPF / DKIM / DMARC 决定，但「这个子域确实能收信」会让伪造更可信，也让受害者的回信真的进入本方系统。
* **放大目录探测的代价**：由于任何子域都接受连接，攻击者可以在子域维度而非仅在本地部分维度做探测。
* **掩盖配置错误**：拼错的子域不会报错，而是被静默接收。真正的故障因此被推迟到很久以后才暴露，且难以定位。
* **与 Null MX 直接冲突**：通配符 MX 使得「本域的这些子域不收邮件」这一声明无从表达。RFC 7505 提供的明确否定语义，被通配符的兜底肯定语义完全覆盖。

**与 SPF、DMARC 的相互作用**

**SPF 侧**：SPF 记录按 RFC 7208 是对具体域名的 TXT 查询。若发布 `*.example.com IN TXT "v=spf1 -all"`，看似为所有子域提供了保护，实则存在一个致命缺口——**凡是在区中已经存在的子域名字，通配符都不会为其合成 SPF 记录。**于是 `www.example.com`（有 A 记录）、`api.example.com`（有 CNAME）这些真实存在的名字反而*没有* SPF 记录，而它们恰恰是最容易被拿来冒用的名字。

**DMARC 侧**：DMARC 策略（规范现由 RFC 9989 承载）通过 `_dmarc` 前缀查询，并提供子域策略机制，使组织域可以为子域统一指定处理策略。**相比给 SPF 加通配符，为组织域配置明确的子域策略是更可靠的收敛手段**，因为它不依赖通配符的合成条件。

结论：**不要指望用通配符 TXT 来做「一劳永逸」的 SPF 保护。**正确做法是为真实使用的名字显式发布记录，并用 DMARC 的子域策略兜底。

**排错：怎么确认自己是否踩了坑**

通配符问题的隐蔽之处在于，**直接查询真实存在的名字往往一切正常**，问题只在查询不存在的名字时才显现。诊断方法是刻意构造一个绝不可能存在的随机名字：

```
# 用随机串验证是否存在通配符合成
dig +short MX  zzq7x4-nonexistent.example.com
dig +short TXT zzq7x4-nonexistent.example.com
dig +short A   zzq7x4-nonexistent.example.com

# 对照：查询真实存在的子域，观察通配符是否被阻断
dig +short TXT www.example.com
```

判读要点：

* 随机名字返回了 MX ⇒ 存在通配符 MX，全部不存在的子域均可收信。
* 随机名字返回了 SPF TXT，但 `www` 等真实子域**没有**返回 ⇒ 正是上一节所述的缺口，最需要被冒用保护的名字反而裸奔。
* 随机名字返回 NXDOMAIN ⇒ 无通配符，符合预期。

同时应检查**是否存在通配符 A/AAAA 记录**：即使没有通配符 MX，只要有通配符 A 记录，按 SMTP 的解析回退规则，不存在的子域同样会被当作可投递目标——这是一条更隐蔽的路径，常被完全忽略。

**推荐做法**

1. **默认不使用通配符 MX**。为每个真实收信的子域发布显式 MX 记录。
2. **用 Null MX 明确否定**：对确定不收邮件的子域，按 RFC 7505 发布 `MX 0 .`，使发送方立即得到永久失败而非进入队列。
3. **审视通配符 A/AAAA**：如业务确需通配符 A（如多租户站点），则必须同时为相应范围提供明确的邮件语义声明，避免 A 记录被当作 MX 回退目标。
4. **SPF 显式化**：为每个真实存在且可能被冒用的名字单独发布 SPF 记录，不依赖通配符合成。
5. **DMARC 子域策略兜底**：在组织域的 DMARC 记录中明确子域策略，覆盖未预料到的子域。
6. **定期做随机名探测**：把上一节的随机名字查询做成周期性巡检项。DNS 配置常由多方共同维护，通配符往往是某次临时需求遗留下来的，需要靠巡检发现而非靠记忆。
7. **变更前评估影响面**：删除既有通配符可能中断依赖它的业务。应先把随机名与真实名的解析差异摸清，识别出实际依赖方，再分步收敛。

参考：RFC 4592《The Role of Wildcards in the Domain Name System》，E. Lewis，2006 年 7 月，Proposed Standard（更新 RFC 1034、RFC 2672），DOI 10.17487/RFC4592，https://www.rfc-editor.org/rfc/rfc4592.html ；RFC 1034《Domain names - concepts and facilities》，P. Mockapetris，1987 年 11 月，STD 13，https://www.rfc-editor.org/rfc/rfc1034.html ；RFC 7505《A "Null MX" No Service Resource Record for Domains That Accept No Mail》，J. Levine、M. Delany，2015 年 6 月，https://www.rfc-editor.org/rfc/rfc7505.html ；RFC 5321《Simple Mail Transfer Protocol》，J. Klensin，2008 年 10 月，https://www.rfc-editor.org/rfc/rfc5321.html ；RFC 7208《Sender Policy Framework (SPF) for Authorizing Use of Domains in Email, Version 1》，S. Kitterman，2014 年 4 月，https://www.rfc-editor.org/rfc/rfc7208.html ；RFC 9989《Domain-Based Message Authentication, Reporting, and Conformance (DMARC)》，2026 年 5 月，https://www.rfc-editor.org/rfc/rfc9989.html

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/rfc4592-wildcard-dns-email-routing-risk.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
