---
title: "云邮箱的审计日志如何用于邮件取证调查？"
source: "https://ztpop.net/kb/cloud-mailbox-audit-log-forensics.html"
license: CC-BY 4.0
---

# 云邮箱的审计日志如何用于邮件取证调查？

1
云邮箱的审计日志如何用于邮件取证调查？
▼

**为什么需要访问级审计而不只是登录日志**

官方文档给出了取证的基本立场：调查被入侵邮箱时，应当**假设被泄露的邮件数据比追踪到的攻击者实际活动痕迹所显示的更多**。原因是监管责任的举证方向是反的——若无法证明敏感信息未被暴露，组织可能面临罚款，文档举例受 HIPAA 监管的机构在有证据表明患者健康信息被暴露时会面临可观罚金。因此登录成功/失败日志远远不够，必须有到「哪一封邮件被访问过」这一粒度的记录。`MailItemsAccessed` 正是为此设计：即便没有任何迹象表明邮件被真正阅读过，只要攻击者获得了对某封邮件的访问，Exchange Online 就会记录该事件。

**覆盖范围与授权前提**

`MailItemsAccessed` 属于审计（标准版）功能，是 Exchange 邮箱审计的一部分，官方说明对分配了 Office 365 E3/E5 或 Microsoft 365 E3/E5 许可的用户**默认启用**。协议覆盖面是完整的：POP、IMAP、MAPI、EWS、Exchange ActiveSync 与 REST 全部在内。这一点在排查中很关键——很多入侵借助 IMAP 或 EWS 等易被忽视的协议进行，若审计只覆盖 Web 与桌面客户端，攻击面会出现盲区。取证的第一步应当是确认目标邮箱在事发时间窗内的审计确实处于启用状态，否则后续所有结论都建立在不完整数据上。

**sync 与 bind：两种访问类型的取证含义完全不同**

这是该审计动作最核心的设计。**bind** 指对单封邮件的独立访问，审计记录中会记下该邮件的 `InternetMessageId`；为控制数据量，2 分钟内发生的 bind 操作会被聚合进一条审计记录，聚合的操作数记在 `OperationCount` 字段，涉及的邮件列在 `Folders` 字段中。**sync** 指客户端批量下载邮件，官方说明 sync 仅在使用 Windows 或 Mac 桌面版 Outlook 客户端访问邮箱时才会被记录；由于同步的数据量极大，系统不为每封邮件生成记录，而是**为包含被同步项的邮件文件夹生成一条事件，并假定该文件夹内的所有邮件均已被泄露**。这条「假定全部泄露」的规则，正是判定泄露范围时最保守也最必要的前提。

**标准调查流程与关键字段**

官方给出的调查顺序是：先确定被入侵的邮箱集合，再确定攻击者拥有访问权的时间窗，然后用 `Search-UnifiedAuditLog` 检索对应记录。**第一步先查 sync**——如果攻击者用邮件客户端把邮件下载到本地，之后即可断网离线阅读，服务端无法再审计到任何动作；判断某次 sync 是否属于攻击者，依据是**上下文**，即客户端 IP 地址与邮件协议。用于比对上下文的字段有：`ClientInfoString`（协议与客户端及版本）、`ClientIPAddress`（客户端 IP）、`SessionId`（用于把攻击者动作与用户日常活动区分开）、`UserId`（读取邮件者的 UPN）。若有 sync 发生在与攻击者相同的上下文中，则应认定**整个邮箱已泄露**。**第二步再查 bind**，此时可用 `InternetMessageId` 精确取回被访问的邮件，逐封判断是否含敏感信息；反向也可用某组敏感邮件的 Message-ID 去反查审计记录，适用于只关心少数几封邮件的场景。

**去重规则带来的记录数陷阱**

取证时若直接用记录条数估算访问量会严重低估。官方说明系统会**过滤掉一小时内针对同一 bind 操作的重复记录，sync 操作同样按一小时间隔去重**。但去重存在例外：对同一 `InternetMessageId`，只要 `ClientIPAddress`、`ClientInfoString`、`ParentFolder`（被访问邮件的完整文件夹路径）、`Logon_type`（登录类型，Owner 为 0、Admin 为 1、Delegate 为 2）、`MailAccessType`、`MailboxUPN`、`User`、`SessionId` 中任一项不同，系统就会生成一条新记录。反过来利用这一点：`Logon_type` 的取值可直接区分邮箱所有者本人、管理员与委派访问者，是识别越权访问的直接线索；而 `MailboxUPN` 与 `User` 不一致，本身就意味着有人在读别人的邮箱。

参考：Microsoft Learn 官方文档《Use MailItemsAccessed to investigate compromised accounts》，https://learn.microsoft.com/en-us/purview/audit-log-investigate-accounts

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/cloud-mailbox-audit-log-forensics.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
