---
title: "DMARC 失败报告（ruf）与聚合报告有什么区别？取证时该怎么用？"
source: "https://ztpop.net/kb/ir-dmarc-failure-report-arf-2026.html"
license: CC-BY 4.0
---

# DMARC 失败报告（ruf）与聚合报告有什么区别？取证时该怎么用？

1
DMARC 失败报告（ruf）与聚合报告有什么区别？取证时该怎么用？
▼

**两类报告解决的问题不同**

聚合报告（rua）是周期性统计，回答「整体上有多少认证失败、来自哪些 IP」，用于治理；失败报告（ruf）是逐封生成的即时样本，回答「这一封具体为什么失败」，用于取证。前者看趋势，后者看个案，不能互相替代。

**失败报告的格式基础**

RFC 6591《Authentication Failure Reporting Using the Abuse Reporting Format》定义了认证失败报告，它建立在 RFC 5965《An Extensible Format for Email Feedback Reports》所定义的 ARF 之上。RFC 5965 第 3 节定义了 message/feedback-report 内容类型，其第 3.1 节（Required Fields）规定 Feedback-Type 字段用于标明报告类型，使解析器能够区分不同种类的反馈报告。认证失败报告通过该机制标识自身类型，并扩展了用于描述认证失败细节的字段。

**取证时重点读哪些信息**

关注：失败发生在哪个机制（SPF 还是 DKIM）、所涉及的标识符（信封发件人域、DKIM 签名域、From 域）、以及原始邮件的头部信息。把这些与本方发送清单比对，即可判断是自有系统配置缺陷，还是外部仿冒。失败报告因含单封邮件信息，其价值在于能直接看到攻击者构造的头部形态。

**隐私与合规约束，决定了它不总是可得**

失败报告包含单封邮件的内容或头部，涉及个人数据，因此相关规范对报告内容的裁剪与发送有明确的隐私考量，实践中大量接收方出于隐私与合规原因根本不发送失败报告，或只发送高度删减的版本。这意味着：不能把 ruf 作为主要监测手段，它是补充而非依赖。治理主干必须建立在聚合报告之上。

**配置注意事项**

ruf 地址若位于 DMARC 记录所属域之外，需要目标域按规范给出外部目的地授权，否则报告不会被发送。另外应为报告接收地址单独规划邮箱与保留策略，避免报告涌入导致主业务邮箱不可用，并注意报告本身也可能被伪造，处理前需校验来源。

参考：[RFC 6591](https://www.rfc-editor.org/rfc/rfc6591.html) ／ [RFC 5965](https://www.rfc-editor.org/rfc/rfc5965.html)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/ir-dmarc-failure-report-arf-2026.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
