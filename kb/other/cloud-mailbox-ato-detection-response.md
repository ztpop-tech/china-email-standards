---
title: "云邮箱账号被接管后应按什么顺序处置？"
source: "https://ztpop.net/kb/cloud-mailbox-ato-detection-response.html"
license: CC-BY 4.0
---

# 云邮箱账号被接管后应按什么顺序处置？

1
云邮箱账号被接管后应按什么顺序处置？
▼

**可据以识别的典型症状**

官方列出的常见症状可作为检测规则的直接输入：邮箱被阻止发送邮件（通常意味着已被判定为发垃圾邮件源）；出现可疑活动，如邮件丢失或被删除；出现可疑的收件箱规则，尤其是**自动转发到未知地址**的规则，以及把邮件移入「便笺」「垃圾邮件」「RSS 订阅」等冷门文件夹的规则；「已发送邮件」或「已删除邮件」中出现可疑内容（官方举的例子是「我困在伦敦，请汇钱」这类求助诈骗）；全局地址列表中该用户的联系人信息被改动；频繁改密或无法解释的账号锁定；**近期新增的外部邮件转发**；以及可疑的邮件签名。把邮件移入冷门文件夹这一手法值得特别注意——其目的是让受害者看不到银行或系统的告警通知，从而延长攻击者的可用时间。

**第一步：切断访问，而不是先改密码**

处置顺序上有一个反直觉但正确的要点：官方的首选动作是**禁用账号**，只有在无法禁用时才退而重置密码。禁用账号可通过 Microsoft Graph PowerShell 完成，先 `Connect-MgGraph -Scopes "User.ReadWrite.All"`，再用 `Get-MgUser` 定位用户后执行 `Update-MgUser -UserId $user.Id -AccountEnabled $false`。重置密码的要求包括：使用强密码；**不要通过邮件发送新密码**（攻击者仍可能在读邮件）；不与最近 5 次密码重复；与 AD 同步的账号需在本地重置两次；联合身份账号需在本地改密并通知管理员；同时更新应用专用密码。

**第二步：撤销会话令牌——最容易被漏掉的一环**

只改密码而不撤销令牌，是账号接管处置中最常见的失误：攻击者手中已签发的刷新令牌在有效期内仍可继续访问，改密码并不会即时使其失效。这在中间人钓鱼（窃取会话 Cookie 而非密码）场景下尤为致命。官方给出的命令是通过 Microsoft Graph PowerShell 连接时申请 `User.RevokeSessions.All` 权限，再执行 `Revoke-MgUserSignInSession -UserId <UPN>`。这一步应当紧随禁用或改密之后立即执行，不应留到最后。

**第三步：清理攻击者留下的持久化**

攻击者即便失去凭据，也可能已留下持续获取邮件的通道，必须逐项排查。**审查 MFA 注册设备**：在 Microsoft Entra 管理中心检查该用户的身份验证方式，移除攻击者自行注册的设备或方法——这是最隐蔽的持久化手段，因为它让攻击者在密码重置后仍能通过 MFA。**审查邮件转发**：用 `Get-Mailbox -Identity <Identity> | Format-List Forwarding*Address,DeliverTo*` 检查邮箱级转发设置。**审查收件箱规则**：用 `Get-InboxRule -Mailbox <Identity> -IncludeHidden | Format-List Name,Enabled,RedirectTo,Forward*,Identity` 检查规则，`-IncludeHidden` 参数是关键，因为攻击者创建的规则可能是隐藏的。此外还应审查该账号授予过的应用许可与管理员角色。

**第四步：调查取证与收尾**

调查阶段可用的官方工具包括：Microsoft Entra 管理中心的登录日志、审核日志与风险报告；Azure 审计日志；以及 Microsoft Defender 门户中的审计日志搜索与邮件跟踪（Message Trace）。邮件跟踪用于确认攻击者以该账号对内对外发出了哪些邮件——这一步决定了是否需要向其他收件人发出告警。收尾动作是：确认调查完成后，从 Microsoft Defender 门户的**受限实体（Restricted entities）页面**把该用户移出，恢复其发信能力。顺序不能颠倒——在持久化未清理干净前解除封锁，等同于把通道重新交还给攻击者。

参考：Microsoft Learn 官方文档《Respond to a compromised cloud email account》，https://learn.microsoft.com/en-us/defender-office-365/responding-to-a-compromised-email-account

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/cloud-mailbox-ato-detection-response.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
