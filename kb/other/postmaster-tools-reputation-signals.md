---
title: "发件人信誉由哪些信号构成，官方 Postmaster 工具能看到什么？"
source: "https://ztpop.net/kb/postmaster-tools-reputation-signals.html"
license: CC-BY 4.0
---

# 发件人信誉由哪些信号构成，官方 Postmaster 工具能看到什么？

1
发件人信誉由哪些信号构成，官方 Postmaster 工具能看到什么？
▼

**信誉挂载在两个独立的标识上**

「发件人信誉」不是一个单一分值，而是接收方对若干**标识**分别维护的历史评价。实践中最重要的两类标识是：

* **IP 信誉**——绑定发送出口的公网地址。它随出口更换而重置，也会被同一出口上的其他发送行为影响。
* **域名信誉**——绑定 From 头中的域、DKIM 签名的 `d=` 域，以及信封回退路径的域。它**可以跨服务商迁移**，是发送方真正的长期资产。

两者独立累积：换 IP 不会清空域名历史，换域名也不会清空 IP 历史。接收方通常同时参考二者，并在其中一个不足时用另一个补足判断。这直接决定了一条战略选择——即便使用服务商提供的共享出口，也应坚持使用**自有发送域与自有 DKIM 域**，否则等于把长期资产寄存在别人的 IP 上。

**构成信誉的可观测信号**

综合各服务商官方文档与 M3AAWG Senders BCP，被明确提及、且发送方可自行观测的信号包括：

* **用户举报为垃圾邮件的比例**——公认权重最高的负面信号，来源于用户主动动作，难以通过技术手段美化。
* **认证通过率**——SPF、DKIM、DMARC 的实际通过比例，而非「是否配置了记录」。
* **加密传输比例**——使用 TLS 完成投递的占比。
* **投递错误与拒绝率**——尤其是指向无效地址的永久性拒绝比例，它反映列表质量。
* **发送量与波动**——绝对量本身不是问题，突变才是。
* **垃圾陷阱命中**——直接指向地址获取方式或列表老化。
* **被公共拦截名单收录**。
* **基础设施卫生**——M3AAWG Senders BCP 另行强调 rDNS 正反解一致、HELO 使用 FQDN、信封回退地址可实际收信、abuse@ 与 postmaster@ 角色地址有人处理。这些不产生「分数」，但缺失会使发送方在任何争议中失去申诉基础。

**Google Postmaster Tools**

Google 的官方入口是 `postmaster.google.com`，以经过验证的域（通常对应 DKIM 的 `d=` 域）为单位授权与呈现，提供的面板涵盖垃圾邮件率、IP 信誉、域名信誉、认证成功率（SPF/DKIM/DMARC 分列）、加密传输比例、投递错误分布与反馈环路数据。

Google 是目前少数**公开了明确数值门槛**的服务商，其官方发件人指南的表述为：Postmaster Tools 所报告的垃圾邮件率应保持在 **0.10% 以下**，并避免任何时候达到 **0.30% 或更高**。这两个数字有官方出处，可以直接作为运维红线。

需要留意面板的粒度限制：数据按验证域聚合，若交易邮件与营销邮件共用同一个 DKIM 域，面板上看到的是两者混合后的曲线，无法归因。这本身就是「按发送流分域」的一个强理由。

**Microsoft 与 Yahoo 的官方通道**

**Microsoft** 提供两套互补的工具，入口均在 `sendersupport.olc.protection.outlook.com`：

* **SNDS**（Smart Network Data Services）——面向 **IP**。需按 IP 段申请并完成归属验证，之后可查看该段 IP 的流量与状态信息。它是 IP 维度的观测面，与 Google 按域聚合的视角正好互补。
* **JMRP**（Junk Email Reporting Program）——Outlook.com 的投诉反馈环路，把用户的举报回送到注册的接收地址。其申请与验证逻辑与 RFC 6449 所描述的一致：以 IP 归属作为授权依据。

**Yahoo** 通过 `senders.yahooinc.com` 发布发件人最佳实践，并提供投诉反馈环路的申请入口。

重要提示：**Microsoft 与 Yahoo 均未公开与 Google 等价的数值门槛**。SNDS 以状态分级而非具体百分比呈现结果。因此凡是给出「Outlook 投诉率须低于某个百分比」之类具体数字的说法，都不应作为运维依据——本文亦不提供此类数字。

**监测体系的三条工程要求**

把信誉从「偶尔看看面板」变成可运营的能力，需要三件事：

1. **按发送流切分**。交易、通知、营销分别使用不同子域（及不同 DKIM 选择器，条件允许时再分出口 IP）。不切分，则任何面板数据都是混合信号，既无法归因也无法止损。
2. **对齐口径**。如 RFC 6449 所指出的，邮箱提供商与发送方对投诉率的分子分母定义常常不同（提供商多以投递到收件箱的量为分母，发送方多以总发送量为分母），二者可相差一个数量级。看到面板数字与自算数字不符时，先核对口径，再谈优化。
3. **三路数据归一到同一主键**。把 Postmaster/SNDS 面板的聚合指标、FBL 送回的 ARF 报告、以及 DSN 退信解析结果，全部映射到「收件人 + 发送流 + 活动」这一组主键上。做不到这一点，就只能看到总体曲线的涨落，永远定位不到是哪一批地址或哪一次投放引发了下滑。

**关于阈值的纪律**

除 Google 公布的垃圾邮件率 0.10% / 0.30% 之外，主流邮箱服务商基本**不公开**信誉判定的具体阈值，且这些判定通常是多信号联合、随时间与整体态势动态调整的，不存在固定分界线。

因此运维上应建立的是**自身基线与趋势告警**——记录各发送流在正常时期的指标分布，对偏离自身基线的变化告警，而不是去对齐某个来路不明的行业数字。任何声称「投诉率低于 X%、退信率低于 Y% 就安全」的表述，若给不出服务商官方页面出处，就不应写进运维手册。

参考：Google [Postmaster Tools](https://postmaster.google.com/) 与 [Email sender guidelines](https://support.google.com/a/answer/81126)；Microsoft [Smart Network Data Services](https://sendersupport.olc.protection.outlook.com/snds/)、[Junk Email Reporting Program](https://sendersupport.olc.protection.outlook.com/jmrp/) 与 [Postmaster Services](https://sendersupport.olc.protection.outlook.com/pm/services.aspx)；Yahoo [Yahoo Sender Hub](https://senders.yahooinc.com/)；M3AAWG [Sender BCP v3](https://www.m3aawg.org/sites/maawg/files/news/M3AAWG_Senders_BCP_Ver3-2015-02.pdf)；投诉率口径见 [RFC 6449](https://www.rfc-editor.org/rfc/rfc6449.txt)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/postmaster-tools-reputation-signals.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
