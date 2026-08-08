---
title: "Exchange 邮箱迁移有哪几种官方方式？各自适用多大规模？"
source: "https://ztpop.net/kb/exchange-mailbox-migration-methods.html"
license: CC-BY 4.0
---

# Exchange 邮箱迁移有哪几种官方方式？各自适用多大规模？

1
Exchange 邮箱迁移有哪几种官方方式？各自适用多大规模？
▼

**三类来自 Exchange 服务器的迁移**

Microsoft 官方文档《Ways to migrate multiple email accounts to Microsoft 365 or Office 365》把从既有 Exchange 服务器出发的迁移分为三类：一次性全量迁移（cutover migration）与快捷迁移（Express migration）；分批迁移（staged migration）；以及混合部署迁移（hybrid）。三类的选择依据是**源端版本与邮箱数量**，不是偏好问题。

**一次性全量迁移的边界**

适用于源端为 Exchange 2003/2007/2010/2013 且邮箱数少于 2000 的场景，可从 Exchange 管理中心（EAC）发起。文档同时给出一条重要提醒：虽然一次性迁移在技术上最多可迁 2000 个邮箱，但由于创建与迁移 2000 个用户耗时过长，**实际更合理的规模是 150 个用户以内**。

**分批与混合的适用条件**

分批迁移适用于源端为 Exchange 2003 或 2007 且邮箱数超过 2000 的场景。混合部署迁移适用于三种情况：源端为 Exchange 2010 且邮箱数在 150 到 2000 之间；源端为 Exchange 2010 且希望长期分小批迁移；或源端为 Exchange 2013 及更高版本。混合模式的特点是**同时保留本地与在线邮箱**，可逐步迁移。

**方向不是单向的**

该文档的用户预配表格明确列出了混合下线（Hybrid offboarding）这一方向：源为在线 Exchange（混合组织 A）、目标为本地 Exchange（混合组织 B），目标端收件人形态为带 ExchangeGuid 的邮件用户或远程邮箱。同表还列出混合上线、跨租户迁移、一次性迁移、Gmail 迁移与 IMAP 迁移各自的源、目标与收件人预配要求。**做由在线回到本地的反向规划时，这张表是判断预配前提的依据。**

**另外两条路径**

其一是使用导入服务迁移 PST 文件，适用于存在大量大体积 PST 的组织，可通过网络上传或邮寄硬盘两种方式；其二是让用户自行导入自己的邮件与联系人。文档还提示：迁移开始前应先查阅 Exchange Online 的限制与最佳实践，以确保迁移后的性能与行为符合预期。

参考：https://learn.microsoft.com/en-us/exchange/mailbox-migration/mailbox-migration

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/exchange-mailbox-migration-methods.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
