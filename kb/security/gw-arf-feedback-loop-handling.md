---
title: "ARF 投诉反馈环（FBL）怎么接？收到投诉后该做什么处置？"
source: "https://ztpop.net/kb/gw-arf-feedback-loop-handling.html"
license: CC-BY 4.0
---

# ARF 投诉反馈环（FBL）怎么接？收到投诉后该做什么处置？

**ARF 是什么、和退信有什么区别**

RFC 5965 定义了 ARF（Abuse Reporting Format），是 `multipart/report; report-type=feedback-report` 结构，用于接收方向发送方回传用户投诉。它与 RFC 3464 的 DSN 是两回事：DSN 说的是「送不到」，ARF 说的是「送到了但用户点了举报」。

两者的处置也不同：DSN 硬退要清理无效地址，ARF 投诉要执行退订。把 ARF 当退信处理（只删地址不退订）会导致同一用户在其他列表上继续收到邮件并继续投诉。

**报文里能拿到什么**

ARF 报文分三段：人类可读说明、`message/feedback-report` 结构化字段、以及原始邮件（可能是完整原文，也可能只有头部）。

结构化段中值得入库的字段：`Feedback-Type`（abuse、fraud、virus 等，abuse 最常见）、`User-Agent`、`Version`、`Original-Mail-From`、`Arrival-Date`、`Source-IP`、`Reported-Domain`。

关键现实约束：多数接收方在回传时会对收件人地址做脱敏或移除，因此不能指望从 ARF 里直接读到投诉者地址。定位办法是在出站邮件中植入可回溯的标识——通常是唯一的消息标识或在 Return-Path 中嵌入编码后的收件人索引，收到投诉时从原始邮件头中反查。这一设计必须在发信侧提前做好，事后无法补。

**接入流程**

FBL 通常需要向各接收方按其流程申请，以发送 IP 或域名为单位注册一个接收投诉的地址。落地要点：使用独立的收件邮箱而非人工邮箱；该地址本身必须能稳定收信，且不要被自己的反垃圾规则拦掉（投诉报文常携带完整的垃圾邮件原文，极易被本方引擎判为垃圾并隔离）——这是接入后「收不到投诉」的最常见原因。

M3AAWG 的公开文档中包含了发送方最佳实践与投诉反馈环相关的行业材料，可作为流程设计的参考。

**投诉率的判定与基线**

投诉率 = 投诉数 / 送达数，应按发送 IP、按发送域、按邮件类别（营销、通知、事务）分别统计，不要只看总体。事务性邮件的投诉率天然远低于营销邮件，混在一起统计会掩盖问题。

判定方式建议用自身基线的相对变化而非固定绝对值：为每个类别建立历史基线，投诉率环比显著跃升即触发排查。相对基线比行业通用阈值更早发现问题，也避免了不同业务形态之间的不可比。

**处置流程**

一，自动退订：收到 abuse 类投诉，立即把对应收件人从相关发送列表移除，且退订应跨列表生效（除非该用户明确单独订阅）。这是 FBL 最基本的义务，做不到就不该接入。

二，来源定位：按消息标识反查该邮件属于哪次发送任务、哪个业务方、哪个模板。投诉集中在单一模板或单一任务时，问题在内容或收件人来源，而不在发送基础设施。

三，源头治理：若某批收件人来源的投诉率显著高于基线，应暂停该来源的发送并核查其获取方式是否为真实订阅。

四，信誉修复：投诉率抬升往往伴随投递率下降。修复期内应降低发送量、优先发送高互动收件人，并持续观察投诉率回落到基线后再逐步恢复量级。

参考：[RFC 5965 An Extensible Format for Email Feedback Reports](https://www.rfc-editor.org/rfc/rfc5965.html) ｜ [M3AAWG Published Documents](https://www.m3aawg.org/published-documents) ｜ [RFC 3464 An Extensible Message Format for Delivery Status Notifications](https://www.rfc-editor.org/rfc/rfc3464.html)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/gw-arf-feedback-loop-handling.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
