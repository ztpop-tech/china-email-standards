---
title: "用 IMAP 迁移旧邮件系统，能迁走什么、迁不走什么？"
source: "https://ztpop.net/kb/legacy-mailbox-imap-migration-scope.html"
license: CC-BY 4.0
---

# 用 IMAP 迁移旧邮件系统，能迁走什么、迁不走什么？

1
用 IMAP 迁移旧邮件系统，能迁走什么、迁不走什么？
▼

**IMAP 迁移的能力边界**

Microsoft 官方迁移文档写得很清楚：可以使用 IMAP 从支持该协议的邮件系统迁移用户邮件，但**通过 IMAP 迁移时只会迁走用户收件箱或其他邮件文件夹中的项目；联系人、日历项与任务无法通过 IMAP 迁移**，用户需要自行手工迁移这部分数据。这一限制适用于所有以 IMAP 作为通道的旧系统替换项目，不因源端产品不同而改变。

**为什么协议层面注定如此**

回到标准即可理解：RFC 9051（Internet Message Access Protocol - Version 4rev2，2021 年 8 月发布，废弃 RFC 3501）所建模的对象只有邮箱与消息——第 5.1.1 节定义邮箱层级命名，第 2.3.1.1 节定义消息的唯一标识 UID，第 2.3.2 节定义 \Seen、\Deleted 等系统标志，第 6.4.4 节定义 FETCH、第 6.4.8 节定义 MOVE、第 6.4.9 节定义 UID 命令。**协议中没有日历与联系人的数据模型**，因此这类数据只能另走导出与导入通道。

**两个容易踩的运维前提**

同一份 Microsoft 文档还给出两条前提：其一，IMAP 迁移**不会在目标端创建邮箱**，必须先为每个用户建好邮箱再迁；其二，迁移完成后，**后续发往源邮箱的新邮件不会被继续迁移**。这意味着必须规划好 MX 切换与迁移窗口的先后顺序，否则会出现切换之后仍有邮件落在旧系统的尾巴。

**保真度检查项**

基于 RFC 9051 的模型，验收时至少核对四项：文件夹层级是否完整还原（第 5.1.1 节的层级分隔符在源与目标可能不同）；已读与未读等标志是否保留（第 2.3.2 节）；邮件本体是否逐字节保真（用 RFC 5322 第 3.6.4 节定义的 Message-ID 做抽样比对）；以及大附件与超长文件夹的迁移是否被源端或目标端的限额截断。

**路径选择建议**

若源端支持原生的高保真迁移接口，优先使用原生方式；仅在源端只暴露 IMAP 时才走 IMAP 通道，并同步安排日历与联系人的独立导出计划。Microsoft 文档也列出了其他并行路径：使用导入服务迁移 PST 文件，或由用户自行导入其邮件与联系人。

参考：https://learn.microsoft.com/en-us/exchange/mailbox-migration/mailbox-migration 与 https://www.rfc-editor.org/rfc/rfc9051.txt

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/legacy-mailbox-imap-migration-scope.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
