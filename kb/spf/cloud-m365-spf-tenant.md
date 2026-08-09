---
title: "Microsoft 365 租户配置 SPF 时，如何避免 10 次 DNS 查询上限导致 permerror？"
source: "https://ztpop.net/kb/cloud-m365-spf-tenant.html"
license: CC-BY 4.0
---

# Microsoft 365 租户配置 SPF 时，如何避免 10 次 DNS 查询上限导致 permerror？

**先把「谁在代你发信」列全**

SPF 授权的是**信封发件人域（RFC 5321 的 MAIL FROM）**所对应的发送 IP。在只用 Exchange Online 的租户里，出站 IP 由微软的包含机制展开覆盖；但绝大多数组织同时还有工单系统、营销平台、监控告警、扫描仪直发、ERP 通知等旁路发送源。

**动作：**配置前先出一张发送源清单，逐项标注「发信用的是哪个域、走哪条出口」。清单不全，后面所有调整都是在猜。

**一个域只能有一条 SPF 记录**

同一域名下发布两条以上 `v=spf1` 开头的 TXT 记录，校验方会直接得到 **permerror**，而不是取其一或合并。这是运维中最高频的一类事故：不同团队各加一条，谁都没删旧的。

**判定方法：**查询该域的全部 TXT 记录，统计以 `v=spf1` 开头的条数，必须恰好为 1。多个发送源要合并进同一条记录，而不是各发一条。

**10 次查询预算：哪些机制计数，哪些不计数**

RFC 7208 规定校验过程中触发 DNS 查询的机制存在数量上限，超出即 permerror。运维上按这样记忆：

* **计数：**`include`、`a`、`mx`、`ptr`、`exists`，以及重定向修饰符 `redirect`。`include` 是递归的——被包含记录里的机制同样计入总预算。
* **不计数：**`ip4`、`ip6`、`all`。

危险点在于 include 的**递归深度不可控**：你只写了 3 个 include，对方各自又 include 了 2~4 层，总数可能在你毫不知情的情况下越界，且会随第三方调整而突然越界。

**压缩记录的三个可执行手段**

* **删除历史遗留：**清单里已停用的服务，其 include 一并删掉。这是收益最大、风险最低的一步。
* **用 ip4/ip6 替代深层 include：**对 IP 段稳定、且会书面公告变更的自建出口，直接写网段可把若干次查询降为 0 次。**但不要对第三方 SaaS 这么做**——对方换 IP 你不会收到通知，会造成静默的送达失败。
* **避免 ptr 与裸 mx：**`ptr` 机制已被明确不建议使用；`mx` 在收发分离的架构下往往授权了一批根本不发信的主机，属于无谓消耗。

**permerror 会连带影响 DMARC**

SPF 一旦 permerror，该封邮件的 SPF 侧就无法产生 pass，DMARC 只能依赖 DKIM 对齐。如果此时 DKIM 也未正确配置，DMARC 判定失败，而策略若已是 `p=reject`，结果就是**合法邮件被对端直接拒收**。

这解释了一个常见现象：SPF 记录「看起来没动过」，但因为某个第三方悄悄加深了自己的 include 层级，送达率在某天突然塌方。

**结尾用 ~all 还是 -all**

`~all`（softfail）表示「未列出的来源可疑但不强制拒绝」，`-all`（fail）表示「未列出即非法」。

**推进节奏：**发送源清单尚未确认完整时用 `~all`；确认清单完整、且 DMARC 已稳定运行在 quarantine 或 reject 之后，再收紧到 `-all`。反过来先收紧 SPF 再摸清发送源，一定会误伤。

**上线前的核对清单**

* 该域 `v=spf1` 记录条数 = 1。
* 逐层展开 include，统计计数机制总数 < 10，并留出余量应对第三方变动。
* 清单中每个发送源都能在记录里找到对应授权项。
* 变更后抽样检查外发邮件的 Authentication-Results 是否为 `spf=pass`。
* 把「SPF 跳数」纳入季度复核项——它会被别人的变更悄悄改变。

参考：[Microsoft Learn：Set up SPF to identify valid email sources](https://learn.microsoft.com/en-us/defender-office-365/email-authentication-spf-configure)、[RFC 7208：Sender Policy Framework (SPF), Version 1](https://www.rfc-editor.org/rfc/rfc7208.html)、[Microsoft Learn：Email authentication in Microsoft 365](https://learn.microsoft.com/en-us/defender-office-365/email-authentication-about)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/cloud-m365-spf-tenant.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
