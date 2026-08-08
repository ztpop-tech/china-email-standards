---
title: "Microsoft 365 中用户被列入“受限实体（Restricted users）”无法发信，如何解除？"
source: "https://ztpop.net/kb/m365-outbound-spam-restricted-user-unblock.html"
license: CC-BY 4.0
---

# Microsoft 365 中用户被列入“受限实体（Restricted users）”无法发信，如何解除？

1
Microsoft 365 中用户被列入“受限实体（Restricted users）”无法发信，如何解除？
▼

**成因**

Microsoft 365 反垃圾邮件会把超出发送限额或账户被盗用的用户列入"受限用户"列表，禁止其继续发信。常见原因：用户发送量超过 outbound 反垃圾邮件策略限额（每分钟/每日），或凭据泄露被滥发。

**现象**

受限后该用户外发或发往外部的邮件会被阻止，通常伴随 NDR（不可投递回执），如 550 5.1.8 访问被拒绝。受限状态会在 Microsoft Defender 门户的"受限实体/受限用户"列表中显示。

**解除方法**

管理员在 Microsoft Defender 门户（安全中心）的"受限用户"页找到该用户，确认其已改密、排除泄露后点"解除/Unblock"；也可通过 Exchange Online PowerShell 用 Get-BlockedSenderAddress 查看、Remove-BlockedSenderAddress 解除。解除后通常约 1 小时内生效。

**预防**

收紧 outbound 反垃圾邮件策略、开启 MFA、监控异常外发，从源头降低被盗用风险。

参考：Microsoft Learn · outbound-spam-restore-restricted-users

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/m365-outbound-spam-restricted-user-unblock.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
