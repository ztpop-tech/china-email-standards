---
title: "未使用的子域被冒用怎么办？PSD DMARC 解决什么问题？"
source: "https://ztpop.net/kb/gw-psd-dmarc-subdomain-gap.html"
license: CC-BY 4.0
---

# 未使用的子域被冒用怎么办？PSD DMARC 解决什么问题？

**先用 sp 标签堵住自有子域**

RFC 7489 的 `sp` 标签用于为组织域下的子域指定独立策略。若不写 `sp`，子域继承 `p` 的取值。

所以对自有域名下大量未使用的子域，最直接的做法是在组织域的 DMARC 记录中写 `p=reject; sp=reject`，这样任意未单独发布记录的子域都会被拒。这一条覆盖了绝大多数「子域被冒用」的场景，成本极低，却常被漏配。

配套的还有两项：为不发信的子域发布 `v=spf1 -all`，以及发布空的 DKIM 通配符选择子记录（`*._domainkey` 值为 `v=DKIM1; p=`，表示该选择子的密钥已吊销）。三者合起来才构成完整声明。

**RFC 9091 解决的是另一个层级的缺口**

组织域策略管不到的情况是：攻击者使用一个在公共后缀之下、但根本没有被注册的域名发信。例如某个公共后缀下不存在的名字——查询该名字的 DMARC 记录会得到 NXDOMAIN，DMARC 的组织域回溯也找不到任何策略，于是无策略可依。

RFC 9091 定义的 PSD DMARC 允许在公共后缀这一层发布 DMARC 记录，并用 `psd=y` 标记自己是公共后缀域。当接收方对某个域回溯不到组织域策略时，可以继续向上查询公共后缀层的策略并据此处置。

该 RFC 属于实验性质，其主要适用对象是管理公共后缀的机构（如国家或行业顶级域的管理方），而非普通企业域名持有者。普通组织的正确认知是：知道这条缺口存在，但你能做的主要在自有域这一侧。

**普通组织的实际动作清单**

一，组织域发布 `p` 与 `sp`，不要只写 `p`；二，为所有不发信的域名与子域发布 `v=spf1 -all` 与吊销态 DKIM 记录；三，把已停用但仍持有的域名纳入同一套策略（这类域最容易被遗忘，且因为曾有真实业务而更具欺骗性）；四，为品牌相关的近似域名做注册防御或至少做监控。

四项里前两项是配置动作，后两项是资产管理动作。实践中冒用事件多数出在「资产清单不全」而非「策略写错」——先把域名台账补齐，再谈策略。

**接收侧能做什么**

作为接收方，遇到 DMARC 回溯不到策略的发送域，不应当直接按无策略放行。可行的补充判定包括：该域是否可解析、注册时间是否极短、是否首次与本组织通信、MX 记录是否存在。

一个实用规则：发送域无 MX 记录、注册时间在很短的时间窗内、且历史无通信记录——三者同时成立时直接隔离。RFC 7208 也提到发送域应对不发信的域明确声明，反过来说，缺少任何声明的新域本身就是一个负面信号。

**验证方式**

配置完成后逐条验证：查询组织域 DMARC 记录确认 `sp` 已存在；随机抽查若干未使用子域，确认查询其 SPF 返回 `-all`、查询 `*._domainkey` 返回吊销态记录；最后通过 DMARC 聚合报告观察这些子域是否出现在报告中——若某个「未使用」的子域持续出现发送记录，要么是被冒用，要么是有未登记的内部系统在用它发信，两种情况都需要立即定性。

参考：[RFC 9091 Experimental DMARC Extension for Public Suffix Domains](https://www.rfc-editor.org/rfc/rfc9091.html) ｜ [RFC 7489 Domain-based Message Authentication, Reporting, and Conformance (DMARC)](https://www.rfc-editor.org/rfc/rfc7489.html) ｜ [RFC 7208 Sender Policy Framework (SPF)](https://www.rfc-editor.org/rfc/rfc7208.html)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/gw-psd-dmarc-subdomain-gap.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
