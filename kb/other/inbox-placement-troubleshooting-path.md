---
title: "邮件进入垃圾箱时，系统性的排查路径应该是怎样的？"
source: "https://ztpop.net/kb/inbox-placement-troubleshooting-path.html"
license: CC-BY 4.0
---

# 邮件进入垃圾箱时，系统性的排查路径应该是怎样的？

1
邮件进入垃圾箱时，系统性的排查路径应该是怎样的？
▼

**第 0 步：先分清「被拒绝」与「被分类」**

这两种现象的排查路径完全不同，混为一谈会浪费大量时间：

* **被拒绝**——对端在 SMTP 事务中返回 4xx 或 5xx，你的 MTA 日志里查得到，通常还会产生 RFC 3464 格式的 DSN。这条路上有确切的错误码与诊断文本可依据，属于「有证据」的故障。
* **被分类到垃圾箱**——对端返回了 250，邮件已被接受，只是被投放到了垃圾目录。**不会产生任何退信**。只能通过种子帐号测试、用户主动反馈、或官方 Postmaster 面板的投递数据间接发现。

所以第一个动作永远是查 MTA 日志：有拒绝记录就走退信码分析分支（按 RFC 3463 的 class 与 subject 定位，其中 `X.7.x` 明确指向策略与认证问题）；没有拒绝记录才进入下面的分层排查。

**第 1 层：传输与身份基础设施**

这一层不通过，后面所有内容优化都是徒劳，因为接收方在判定内容之前就已经把你归入低信任类别。逐项核对：

* **PTR 与正向确认**：出口 IP 有 PTR 记录解析到主机名，且该主机名的 A/AAAA 记录解析回同一 IP。Google 明确要求发送 IP 必须与 PTR 中主机名的 IP 一致。
* **HELO/EHLO**：使用可解析的 FQDN，且与 PTR 主机名一致。
* **TLS**：Google 已将其列为发件人要求。
* **SPF**：记录是否覆盖了**实际使用的全部出口**（含第三方发送平台），以及是否触及 DNS 查询次数上限导致 permerror。
* **DKIM**：签名是否真的验证通过（不是「配了记录」）、`d=` 域是否与 From 域对齐、密钥长度是否达标（Google 要求发往个人 Gmail 帐号至少 1024 位，建议 2048 位）、选择器是否可解析。
* **DMARC**：记录是否存在，SPF 与 DKIM 是否至少有一项在组织级别与 From 域对齐并通过。

验证方式应当是**看接收侧的实际结果**：读取收到邮件的 Authentication-Results 头，以及 Postmaster Tools 中的认证通过率曲线，而不是只在自己这边跑一遍配置检查工具。

**第 2 层：信誉**

基础设施合格但仍进垃圾箱，下一步看信誉：

* 查 Google Postmaster Tools 的**域名信誉与 IP 信誉**评级，以及垃圾邮件率曲线。Google 公布的门槛是应保持在 0.10% 以下、避免达到 0.30% 或更高。
* 查 Microsoft SNDS 中该 IP 段的状态；查 Outlook.com 的 JMRP 反馈是否有异常增长。
* 确认是否被公共拦截名单收录。
* 核对**近期发送量曲线**。Google 明确提示：在没有大量发送历史的情况下突然翻倍，可能触发限速或信誉下降。很多「莫名其妙进垃圾箱」的案例，根因只是上周做了一次超出常规量级的群发。
* 若近期更换过出口 IP、DKIM 域或发送平台，则应当按新标识的预热逻辑处理，而不是当作故障排查。

**第 3 层：列表与许可**

信誉指标的恶化，源头几乎总在列表：

* **地址来源**：是否全部为收件人主动订阅？M3AAWG Senders BCP 反对使用购买、租用或抓取而来的名单——这类名单必然包含垃圾陷阱与大量无效地址。
* **垃圾陷阱命中**：长期无人使用的地址会被回收改造为陷阱，因此「历史遗留的老名单」风险最高。
* **长期零互动地址**：持续向从不打开的地址发送，会显著拉低整体参与度信号。应做再确认或停发。
* **退订是否即时生效**：用户点了退订仍继续收到邮件时，下一步动作通常就是「举报垃圾邮件」。退订链路的任何延迟或失效，都会被直接转换成投诉率。
* **投诉与退信是否当日闭环**：FBL 报告与 5.x.x 永久退信必须自动进入抑制列表，人工处理必然滞后。

**第 4 层：内容与格式**

前三层都合格才轮到内容。优先核对客观的格式合规，而非主观的文案风格：

* 是否符合 RFC 5322。Google 明确要求：每封邮件包含**有效的 Message-ID**；From、To、Subject、Date 这类**单实例头字段只能出现一次**。重复的单实例头是模板拼装类系统的高发缺陷，且会引发解析分歧。
* 链接是否有效、是否存在多级跳转、短链域是否与品牌无关、落地域是否与发送域一致。
* 是否为纯图片邮件而缺少可读文本；HTML 是否结构完整、可被正常解析。
* 附件类型与声明是否一致。

内容层的调整应当最后进行，因为它主观性最强、可验证性最弱，容易掩盖真实根因。

**第 5 层：发送流隔离与收敛方法**

**隔离**：把交易类与营销类拆到不同子域、不同 DKIM 域，条件允许时再拆到不同出口 IP。混流的后果是营销邮件的投诉会拖垮密码重置、订单通知这类必达邮件——而后者的失败代价远高于前者。任何隔离变更都相当于启用新标识，需按预热节奏重新爬坡，不能直接切量。

**收敛方法**：一次只改一个变量，并留出足够的观察期让信誉数据反映变化；使用固定的一批种子地址做前后对照；把每一次变更的时间点标注到 Postmaster 曲线上。如果同时修改认证配置、内容模板与发送节奏，即便情况好转也无法归因，下一次故障仍会束手无策。可送达性排障的核心能力不是「知道很多技巧」，而是**保持变量可控**。

参考：Google [Email sender guidelines](https://support.google.com/a/answer/81126) 与 [Postmaster Tools](https://postmaster.google.com/)；Microsoft [SNDS](https://sendersupport.olc.protection.outlook.com/snds/) 与 [Postmaster Services](https://sendersupport.olc.protection.outlook.com/pm/services.aspx)；Yahoo [Sender Best Practices](https://senders.yahooinc.com/best-practices/)；M3AAWG [Sender BCP v3](https://www.m3aawg.org/sites/maawg/files/news/M3AAWG_Senders_BCP_Ver3-2015-02.pdf)；退信语义见 [RFC 3463](https://www.rfc-editor.org/rfc/rfc3463.txt) 与 [RFC 3464](https://www.rfc-editor.org/rfc/rfc3464.txt)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/inbox-placement-troubleshooting-path.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
