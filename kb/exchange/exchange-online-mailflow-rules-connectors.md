---
title: "Exchange Online 的邮件流规则与连接器该如何配置？"
source: "https://ztpop.net/kb/exchange-online-mailflow-rules-connectors.html"
license: CC-BY 4.0
---

# Exchange Online 的邮件流规则与连接器该如何配置？

1
Exchange Online 的邮件流规则与连接器该如何配置？
▼

**邮件流规则的四个组成部分**

微软官方文档把邮件流规则（mail flow rules，旧称 transport rules）拆为四部分：**条件**用于识别要处理的邮件，可检查收发人字段等邮件头，也可检查主题、正文、附件、邮件大小、邮件分类等属性，多数条件需指定比较运算符与匹配值；**例外**使用与条件相同的标识符，一旦命中即阻止动作施加，其优先级高于条件；**动作**规定命中后做什么，涵盖拒绝、删除、重定向、追加收件人、给主题加前缀、在正文插入免责声明等；**属性**则是既非条件也非动作的其余设置。文档特别警示：不设条件与例外的规则会作用于全部邮件，若动作是删除，可能导致全组织收发邮件被清空。

**多值与多规则的布尔逻辑**

组合逻辑需要精确记住，否则极易写出与预期相反的规则。官方给出的规则是：**多个条件之间是 AND**，邮件必须全部满足；若要「满足其一即可」，只能拆成多条规则。**同一条件的多个取值之间是 OR**，命中任意一个值即算满足。**多个例外之间是 OR**，命中任一例外即豁免。**多个动作之间是 AND**，命中的邮件会被施加全部动作。需注意部分动作具有终止性——例如「不通知任何人直接删除邮件」会阻止后续规则继续处理，而「转发邮件」类动作则不允许再附加其他动作。

**关键属性与灰度上线方式**

官方属性表中与运维直接相关的几项：`Priority` 决定规则应用顺序，PowerShell 中 **0 为最高优先级**，EAC 中通过上下拖动调整，默认按创建时间排序（旧规则优先级更高）。`Mode` 支持立即生效、仅测试、以及测试并显示 Policy Tips 三种模式，后两者可在不影响投递的前提下先验证匹配面。`ActivationDate` 与 `ExpiryDate` 设定规则生效时间窗。`SetAuditSeverity` 设定事件报告与邮件跟踪日志的严重级别，取值为 DoNotAudit、Low、Medium、High。`StopRuleProcessing` 在 EAC 中形似属性、实为动作，用于命中后终止后续规则。`SenderAddressLocation` 决定发件人地址取自邮件头、信封还是两者兼查——这一项在反伪造场景下尤其关键，因为攻击者常让信封发件人与显示发件人不一致。`RuleErrorAction` 决定规则处理未完成时的行为，默认忽略该规则，也可选择重新提交邮件。

**连接器：多数组织其实不需要**

官方文档的第一句结论就是：大多数 Microsoft 365 组织在常规邮件流中**不需要连接器**，Exchange Online 默认即可直接与互联网收发。真正需要手工建连接器的场景有三类：一是组织自有本地邮件服务器（含非微软 SMTP 服务器）与云端并存且未走混合部署向导；二是与合作伙伴组织之间需要施加额外安全限制；三是打印机、扫描仪、业务应用等非邮箱实体的 SMTP 中继（此场景为可选）。已运行混合配置向导（Hybrid Configuration wizard）的组织，连接器由向导自动创建，无需手工再建。伙伴连接器可强制双向 TLS、限定发件域或源 IP 段，不满足条件的邮件将被拒绝。文档给出两条明确约束：**不要在同一个伙伴连接器里同时配置 IP 与证书**，应拆成不同连接器；当存在按 IP 或证书限制的连接器时，无法再用按发件域放行的连接器，限制型连接器会优先生效。

**生效延迟与其他注意点**

官方明确：新建或修改邮件流规则后，**最长可能需要 30 分钟**才应用到邮件上，排障时不要在几分钟内就断定规则失效。系统生成的邮件（Exchange 自身产生的 NDR、发往仲裁邮箱的审批通知、日记报告）不会被邮件流规则处理。加密邮件方面：S/MIME 加密邮件的规则只能读取信封头，涉及内容检查或内容改写的规则无法执行；RMS 保护邮件需先确认传输解密已启用。文档另提醒规则历史与变更不被保留，无法回滚到先前状态，因此变更前应自行导出留档。最后一条常见误用是为内部发件设备整体绕过邮件保护过滤——官方建议只针对确有必要的可信来源开口，不要对全部内部邮件放行，否则被入侵的账号即可借该通道投递恶意内容。

参考：Microsoft Learn 官方文档《Mail flow rules (transport rules) in Exchange Online》与《Configure mail flow using connectors in Exchange Online》，https://learn.microsoft.com/en-us/exchange/security-and-compliance/mail-flow-rules/mail-flow-rules 、 https://learn.microsoft.com/en-us/exchange/mail-flow-best-practices/use-connectors-to-configure-mail-flow/use-connectors-to-configure-mail-flow

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/exchange-online-mailflow-rules-connectors.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
