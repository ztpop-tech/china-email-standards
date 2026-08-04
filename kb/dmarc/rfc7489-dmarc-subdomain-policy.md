---
title: "DMARC（RFC 7489）子域策略 sp 与对齐如何配置？"
source: "https://ztpop.net/kb/rfc7489-dmarc-subdomain-policy.html"
license: CC-BY 4.0
---

# DMARC（RFC 7489）子域策略 sp 与对齐如何配置？

1
DMARC（RFC 7489）子域策略 sp 与对齐如何配置？
▼

**p 与 sp 的作用域**

§6.3：`p` 为策略记录必选项，作用于被查询域**及其所有子域**；`sp` 为可选项，仅作用于子域、不影响域名本身，**若缺失则子域继承 p 的策略**。注意 §6.6.3：`sp` 在“发布于组织域子域”的记录中被忽略——即子域自己的 DMARC 记录里的 sp 不生效。因此组织域设 `p=reject` 且不发 sp 时，所有子域已等效 reject。

**对齐模式 adkim / aspf**

§3.1.1 与 §3.1.2：`adkim` 与 `aspf` 均**默认 `r`（relaxed）**。relaxed 下 DKIM 的 `d=` 或 SPF 认证域只需与 From 域具有相同组织域即对齐；strict（`s`）则要求完全匹配的 FQDN/域。严格模式更抗伪造但易误伤转发与代发。

**渐进执行与报告**

`pct`（§6.6.4）取值 0–100、默认 100，表示对多少比例的邮件执行策略，用于灰度上线；未命中部分按本地常规分类处理。`rua`（聚合报告）与 `ruf`（失败报告，依赖 `fo`）为可选项，接收方 MUST 支持 `mailto:` URI，并可带大小上限如 `reports@example.com!50m`。外部报告目的地需经 §7.1 的授权校验防报告洪水。

**策略取值与边界**

策略值仅 `none`/`quarantine`/`reject` 三者；§10.3 建议 reject 应在 SMTP 事务内拒绝。关键继承逻辑：由于 sp 缺失即继承 p，配置子域放宽（如 `sp=none`）才需显式声明；若需全域强隔离，组织域 `p=reject` 已足以覆盖子域，不必重复设置 sp。

参考：RFC 7489（DMARC），https://www.rfc-editor.org/rfc/rfc7489 —— 章节 6.3 / 3.1.1 / 3.1.2 / 6.6.4 / 6.2 / 10.3 / 6.6.3

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/rfc7489-dmarc-subdomain-policy.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
