---
title: "反向散射退信（Backscatter）怎么产生？如何在网关侧治理？"
source: "https://ztpop.net/kb/gw-backscatter-prevention.html"
license: CC-BY 4.0
---

# 反向散射退信（Backscatter）怎么产生？如何在网关侧治理？

**根因是「先收下再退回」**

反向散射指：垃圾邮件伪造了某个无辜者的地址作为 MAIL FROM，你的服务器先在 SMTP 会话中接收了这封邮件（返回 250），之后才发现收件人不存在或内容被拒，于是生成一封退信发给那个被伪造的无辜地址。结果是你的服务器在向第三方发送未经请求的邮件。

危害是双向的：无辜方收到大量莫名退信，而你的出口 IP 因为持续发送无人期待的邮件而被降级信誉。BACKSCATTER\_README 把治理的第一原则总结得很清楚——尽可能在 SMTP 会话内拒绝，而不是收下之后再退。

**第一步：无效收件人必须在 RCPT 阶段拒绝**

这是消除反向散射最有效的单项措施。网关必须掌握全部有效收件人清单，在 RCPT TO 阶段就返回 5xx。Postfix 侧：本地投递用 `local_recipient_maps`，虚拟别名域用 `virtual_alias_maps`，虚拟邮箱域用 `virtual_mailbox_maps`，中继域用 `relay_recipient_maps`。

中继场景最容易出问题：网关不知道下游邮件系统有哪些账号，只能全收再转，下游拒收后由网关生成退信。解决办法是把下游的有效地址清单同步到 `relay_recipient_maps`（定期从目录服务导出），或使用地址验证机制在会话内向下游探询。前者更稳定，后者会对下游产生额外查询压力。

**第二步：内容判定也尽量前移**

凡是能在会话内完成的判定（连接信誉、认证结果、收件人有效性、大小限制），都应在会话内以 5xx 拒绝。只有确实需要收下才能完成的深度分析（如需要完整正文的内容分析），才允许收后处置——而这类的处置动作应当是隔离，不是退信。

换句话说：会话内拒绝 → 发送方自己生成退信，责任与流量都在发送方；收下后退信 → 你替伪造者向无辜者发信。两者的外部影响完全不同。

**第三步：约束自动回复**

外出自动回复、休假回复、工单自动确认都可能变成反向散射源。RFC 3834 对自动回复提出了明确要求：应基于 Return-Path 而非头部 From 决定回复对象，Return-Path 为空（`<>`）时必须不回复，且自动回复自身应带 `Auto-Submitted` 头以避免回复风暴。

网关侧的加固：对认证失败或 DMARC 不对齐的入站邮件禁止触发自动回复；对同一发件地址的自动回复设置频次上限；对邮件列表类邮件（含 `List-Id` 等头）不回复。

**第四步：收敛已产生的退信**

无法完全消除的退信要做两件事。其一，限制退信正文中回传的原始内容量——Postfix 用 `bounce_size_limit` 控制，减小退信体积可显著降低被用作放大转发的价值。

其二，对明显是伪造场景产生的退信做过滤。BACKSCATTER\_README 给出的思路是利用头部特征识别那些「本机从未发出过」的原始消息所对应的退信并丢弃。更稳健的做法是给出站邮件的 Return-Path 加上可验证的签名（地址中嵌入带时效的校验值），入站退信时校验该签名，校验不过即判定为反向散射直接拒收——代价是需要改造出站地址生成与入站校验两侧，上线前要确认所有出站路径都已覆盖，否则会误拒真实退信。

参考：[Postfix BACKSCATTER\_README](https://www.postfix.org/BACKSCATTER_README.html) ｜ [RFC 3834 Recommendations for Automatic Responses to Electronic Mail](https://www.rfc-editor.org/rfc/rfc3834.html) ｜ [RFC 5321 Simple Mail Transfer Protocol](https://www.rfc-editor.org/rfc/rfc5321.html)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/gw-backscatter-prevention.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
