---
title: "Google Workspace 的邮件路由与内容合规规则怎么设计？"
source: "https://ztpop.net/kb/google-workspace-mail-routing-compliance.html"
license: CC-BY 4.0
---

# Google Workspace 的邮件路由与内容合规规则怎么设计？

1
Google Workspace 的邮件路由与内容合规规则怎么设计？
▼

**两级路由：Default routing 与 Routing**

Google 官方文档给出两个主要路由设置，职责分工明确：**Default routing** 用于设定组织的默认投递方式，例如把全部或多数邮件同时送到多个收件箱（双投递）；**Routing** 用于在默认之上创建更具体的投递规则，或覆盖默认行为，例如把某位高管的全部邮件抄送一份给其助理。理解这个层级关系是排查「为什么这封邮件走了意料之外的路径」的前提。文档另提示：若与遗留路由控制项存在冲突，当前的路由设置会覆盖遗留设置。

**常见入站路由方案**

官方列出的入站方案各有适用场景：**Split delivery（分割投递）**按指定收件人把邮件分投到同一域下的两套邮件系统，适合部分用户用 Gmail、部分用户用其他系统的过渡期，也适合迁移时先用小范围人群验证投递；**Dual delivery（双投递）**把同一封邮件送进两个及以上收件箱，例如同时进 Gmail 与本地服务器；**Catch-all 邮箱**接收本域下地址错误或收件人不存在的邮件；**Address maps（地址映射）**把某用户的入站邮件自动重定向或转发给其他用户。若组织有本地邮件服务器，Gmail 先做垃圾与问题邮件过滤，再把邮件送到本地服务器。

**出站路由与 TLS 强制**

出站侧有两条路径：**Outbound gateway（出站网关服务器）**让外发邮件先经网关处理（如统一追加公司页脚）再投递；**SMTP relay service**让非 Gmail 服务器（如本地 Microsoft 服务器或某个 SMTP 服务）的外发邮件经 Gmail 服务器中转，从而在投递给外部收件人前先过一遍垃圾与病毒过滤，并让管理控制台中的邮件安全设置作用于这些外发邮件。合规维度上，**TLS compliance** 可要求发往或来自指定域与地址的邮件必须走 TLS——需注意其后果是硬性的：若指定的对端域不支持 TLS，入站邮件将被拒收、出站邮件不会发出，因此配置前务必确认对端能力。

**Content compliance 的四类表达式**

内容合规规则位于管理控制台的 Gmail 合规区域，每条规则需至少 1 个、最多 10 个表达式。**Simple content match** 的行为类似 Gmail 搜索，输入「a word」会命中包含这些词的各种字符串，因而匹配面偏宽。**Advanced content match** 要求精确匹配，需先选 Location（邮件头与正文、全部头、正文、主题、发件人头、收件人头、信封发件人、任意信封收件人、原始邮件），再选 Match type（开头是、结尾是、包含、不包含、等于、为空、匹配正则、不匹配正则、匹配任意词、匹配全部词），单条正则上限 10000 字符并可设最小匹配次数。**Metadata match** 匹配邮件属性，可用项包括消息认证结果、源 IP（在范围内/外）、是否安全传输 TLS、S/MIME 加密与签名、邮件大小、Gmail 保密模式、以及安全沙箱检出恶意软件等。**Predefined content match** 使用信用卡号、社会保障号等预定义检测器，可设触发所需出现次数与置信阈值，但并非所有版本可用。

**三类动作与匹配后的行为差异**

命中后的动作有三类，行为差异需要注意。**Reject message** 在到达收件人前拒收，可填写给发件人的说明理由，Gmail 会自动附加 SMTP 拒绝码；关键在于——**被拒收的邮件不会再应用其他路由或合规规则**，因此拒收类规则的相对顺序需要谨慎设计。**Quarantine message** 送入管理员隔离区待审，仅对用户类账号可用，可勾选「隔离时通知发件人」。**Modify message** 提供一组控件：添加自定义头、给主题加前缀、更改路由与是否同时改投垃圾邮件、更改信封收件人、添加更多收件人、移除附件、跳过垃圾过滤器、加密（仅限继续投递场景）等。内容合规同时支持扫描文本附件与 .docx、.xlsx、.pdf 等常见类型，适用于正文的规则同样适用于从附件中提取的文本。

**投递失败时的重试行为**

排障时容易误判的一点是重试窗口。官方说明：当邮件从 Google 服务器路由到外部收件服务器而连接建立失败（超时、拒绝或 400 系错误）时，Gmail 会保留邮件并**每隔几分钟重试一次、最长持续 7 天**，7 天后退回发件人；若返回的是 500 系错误则立即拒收。还有一个易踩的坑：在 Gmail 仍在重试期间新增了服务器，该邮件仍会被路由到原服务器而非新服务器。

参考：Google Workspace 管理员帮助官方文档《Email routing and delivery options for Google Workspace》与《Set up rules for advanced email content filtering》（Content compliance），https://support.google.com/a/answer/2685650 、 https://support.google.com/a/answer/1346934

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/google-workspace-mail-routing-compliance.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
