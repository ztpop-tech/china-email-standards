---
title: "RFC 4021 邮件与 MIME 信头字段注册表包含哪些字段？注册模板怎么读？"
source: "https://ztpop.net/kb/rfc4021-mail-header-field-registry.html"
license: CC-BY 4.0
---

# RFC 4021 邮件与 MIME 信头字段注册表包含哪些字段？注册模板怎么读？

1
RFC 4021 邮件与 MIME 信头字段注册表包含哪些字段？注册模板怎么读？
▼

**文档定位与结构（§1、§1.1）**

RFC 4021 的作用是：**按「消息头字段注册流程」为一批邮件消息头字段与 MIME 头字段建立 IANA 注册**。它本身不发明新字段，而是把散落在 RFC 822/2822、MIME 系列等文档中的既有字段统一登记造册，使 IANA 注册表成为查询头字段权威定义的单一入口。文档结构上，**§2.1 收录邮件消息头字段的初始注册模板，§2.2 收录 MIME 头字段的初始注册模板**。值得一提的是，正文主体是**由 RDF/N3 数据自动生成**的。

**注册模板的五个字段（以 Date 为例，§2.1.1）**

每个头字段的注册项采用统一模板，读懂模板即可读懂整张注册表：

* **Description（描述）**：一句话说明用途。如 `Date` 为 “Message date and time”。
* **Applicable protocol（适用协议）**：标明是 Mail 还是 MIME。
* **Status（状态）**：如 `standard`（标准）。注册表中还存在 informational、experimental、obsoleted 等其他状态取值。
* **Author/change controller（作者/变更控制方）**：对本文登记的这批字段为 **IETF（iesg@ietf.org）**，即后续修改需经 IETF 流程。
* **Specification document(s)（规范文档）**：给出定义该字段的 RFC 与具体章节。`Date` 指向 RFC 2822 §3.6.1。
* **Related information（相关信息）**：补充语义说明。如 `Date` 表示**邮件创建者认定该邮件已完成、可进入投递系统的日期时间**，并注明其早在 RFC 822 中即被定为标准。

**永久邮件头字段注册表概览（§2.1）**

§2.1 以表格汇总永久注册项，按功能可分为几组：

* **源与目的地**：`From`（邮件作者的邮箱）、`Sender`（邮件发送者的邮箱）、`Reply-To`（回复用邮箱）、`To`（主收件人邮箱）、`Cc`（抄送）、`Bcc`（密送）。**注意 From 与 Sender 在注册表中是语义分明的两个字段**——这正是 DMARC 等认证机制强调「以 From 域对齐」的规范源头。
* **标识与会话线索**：`Message-ID`（邮件标识符）、`In-Reply-To`（标识被回复的邮件）、`References`（相关邮件标识符）、`Original-Message-ID`（原始邮件标识符）。这组字段是邮件客户端串起会话线程的依据。
* **内容描述**：`Subject`（主题）、`Comments`（附加注释）、`Keywords`（关键词或短语）。
* **转发（Resent-\*）族**：`Resent-Date`、`Resent-From`、`Resent-Sender`、`Resent-To`、`Resent-Cc`、`Resent-Bcc`、`Resent-Reply-To`、`Resent-Message-ID`，完整镜像了原始字段族，用于记录邮件被重新分发时的信息。
* **传输与追踪**：`Return-Path`（邮件返回路径）、**`Received`（邮件传输追踪信息）**、`Encrypted`（邮件加密信息）。`Received` 正是邮件头取证分析中最核心的字段。
* **回执与语言**：`Disposition-Notification-To`（送达处置通知的接收邮箱）、`Disposition-Notification-Options`（处置通知选项）、`Accept-Language`（自动回复所用语言）。
* **邮件列表（List-\*）族**：`List-Archive`（归档 URL）、`List-Help`（列表信息 URL）、`List-ID`（列表标识符）、`List-Owner`（列表管理者邮箱 URL）、`List-Post`（投递 URL）、`List-Subscribe`（订阅 URL）、`List-Unsubscribe`（退订 URL）。这组字段是邮件列表可管理性与合规退订的基础。
* 另有 `PICS-Label`（PICS 分级标签）、`Encoding`（邮件编码及其他信息）等历史字段。

**工程用途**

对邮件系统实现者而言，RFC 4021 的价值在于提供一份**权威、可机读、可追溯到具体 RFC 章节的字段清单**。解析器可据此判断某个头字段是否为已注册标准字段、其规范定义出自哪份文档的哪一节，从而在遇到非注册字段（如各类 `X-` 前缀私有头）时采取不同的信任与处理策略；安全审计时也可据此判断某封邮件是否携带了本不该出现或被重复插入的标准字段。

参考：RFC 4021《Registration of Mail and MIME Header Fields》，https://www.rfc-editor.org/rfc/rfc4021 —— 章节 1 / 1.1 / 2 / 2.1 / 2.1.1 / 2.2

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/rfc4021-mail-header-field-registry.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
