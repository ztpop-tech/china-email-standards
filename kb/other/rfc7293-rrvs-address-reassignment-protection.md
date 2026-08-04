---
title: "邮箱地址被回收再分配给新用户后，如何避免把敏感邮件投给新主人？"
source: "https://ztpop.net/kb/rfc7293-rrvs-address-reassignment-protection.html"
license: CC-BY 4.0
---

# 邮箱地址被回收再分配给新用户后，如何避免把敏感邮件投给新主人？

1
邮箱地址被回收再分配给新用户后，如何避免把敏感邮件投给新主人？
▼

**问题的本质：地址标识符会易主，而发送方对此一无所知**

邮箱地址在现实中并不是永久绑定到某个自然人的标识符。运营商会回收长期不活跃的免费邮箱并重新开放注册；企业会在员工离职后把工号邮箱或姓名邮箱分配给新入职者；域名易主后，原有的全部本地部分也随之落入新持有者手中。

危险之处在于**发送方完全感知不到这次易主**。密码重置链接、账单、合同、内部通知仍然发往同一个字符串，SMTP 层面一切正常——地址存在、投递成功、没有退信。**真正的失败是「投递成功但收件人换了人」，这类失败在协议层是静默的，在日志里看不出任何异常。**

RFC 7293 正是为消除这种静默失败而制定的：它让发送方把「我认为这个地址自某个时间点起一直属于同一个人」这一前提**显式写进协议**，交由掌握真实所有权记录的接收方去校验。

**两种承载方式：SMTP 扩展与信头字段**

RFC 7293 提供了两条并行路径，二者语义相同但适用场景不同。

**其一是 SMTP 扩展。**扩展名为 RRVS（Require Recipient Valid Since 的缩写）。支持该扩展的服务器在 EHLO 响应中通告 RRVS 关键字，该关键字本身不带参数；客户端随后在 RCPT TO 命令上附加 `RRVS=` 参数，值为一个日期时间，并可选地以分号追加一个字符表示对端不支持时的动作。

```
C: EHLO client.example
S: 250-server.example
S: 250 RRVS
C: MAIL FROM:<sender@client.example>
C: RCPT TO:<receiver@server.example> RRVS=2020-03-01T09:00:00Z
```

**其二是信头字段。**字段名为 `Require-Recipient-Valid-Since`，其值为一个地址加分号再加一个日期时间。由于信头随报文一起走完全程，这条路径可以穿越不支持该扩展的中间跳。

```
Require-Recipient-Valid-Since: receiver@server.example; Sun, 01 Mar 2020 09:00:00 +0000
```

两者的分工很清楚：**SMTP 扩展在会话中即时生效，判定结果能同步回传给客户端；信头字段则用于扩展不可用时的兜底**，代价是判定推迟到报文被接收之后。二者可以同时使用。

**接收侧的判定与拒绝方式**

按 RFC 7293，投递代理在继续投递之前执行两步。**第一步是角色账号豁免**：若目标是 RFC 2142 所列的通用服务、角色与职能类邮箱（如 postmaster、abuse、hostmaster 等），则忽略该参数。这一豁免的道理在于角色邮箱按设计就会在人员之间流转，对其做「持续同一人持有」的校验没有意义。

**第二步是所有权连续性检查**：若该地址并非角色账号，且自参数给出的时间戳以来并未处于连续同一所有权之下，则对 RCPT 命令返回 550 错误。

RFC 7293 同时在 IANA 的 SMTP 增强状态码注册表中登记了三个枚举状态码，它们的关联基础状态码均为 5XX：

* **X.7.17（Mailbox owner has changed）**：接收系统确认目标邮箱自指定时间起并非连续同一人持有。
* **X.7.18（Domain owner has changed）**：接收系统愿意披露收件域名的所有者自指定时间起已发生变更。
* **X.7.19（RRVS test cannot be completed）**：接收系统无法完成评估，因为所需的时间戳未被记录。此时由发信方决定是否去掉 RRVS 保护后重发。

**排错时看到 550 配 5.7.17，含义非常明确：地址还在，但人换了，重发无意义，必须走业务侧的身份重新核验流程。**它与「用户不存在」「被反垃圾拦截」是完全不同的三件事。

**中继与不支持方的处理：R 与 C 两种动作**

真实链路上不可能所有跳都支持该扩展，RFC 7293 因此规定了明确的降级行为。

不做邮箱所有权检查的 MTA（例如部署在组织边界做入站接收的那一跳）**应当把 RRVS 参数继续中继给下一跳**，让真正掌握所有权记录的 MDA 去处理；中继时**必须保留客户端指定的不支持动作**。

当下一跳不通告支持该扩展时，行为取决于那个可选动作字符：

* **未指定，或指定为 R（reject）**：处理该报文的 MTA 必须拒收。具体方式为——若对引入报文的 SMTP 客户端提供的是同步服务，则对 DATA 命令返回 550 错误；否则生成投递状态通知告知原发送方投递未发生，并终止后续中继尝试。
* **指定为 C（continue）**：可在无保护的情况下继续投递。

**这个选择必须按业务风险来定，不能一刀切。**密码重置、账单、含个人信息的通知应当选择拒绝——宁可不送达，也不能送错人；营销类、纯提示类邮件则可以选择继续，避免因链路不支持而大面积失败。

**部署顺序与常见误区**

1. **先确认自己有没有那个时间戳**。整套机制的前提是接收侧记录了邮箱的创建或重新分配时间。若系统里根本没有这个字段，那么无论怎么配置，结果都只能是 X.7.19。**补齐所有权时间戳是第一步，也是最容易被跳过的一步。**
2. **发送侧的时间戳取值要保守**。RFC 7293 指出，若没有精确的记录，可以取一个「不晚于该邮箱可能被创建或重新分配的最早时刻」的值，例如所有已记录的创建与再分配时间中的最早者。**取值偏早会漏判，取值偏晚会误拒——宁可漏判也不要误拒**，因为误拒直接伤害正常业务。
3. **不要拿它当反钓鱼手段**。RRVS 解决的是「地址易主」，不解决「发件人伪造」。后者属于 SPF、DKIM、DMARC 的范畴，两类机制正交，不能互相替代。
4. **注意信息披露的分寸**。X.7.18 会告诉外界某个域名换了主人，X.7.17 会告诉外界某个邮箱换了人。这本身是一种信息披露，接收方需要按自身策略决定披露到什么程度，也可以选择只返回较粗粒度的拒绝原因。
5. **先在内部链路灰度**。在自建的提交服务与投递服务之间先跑通全流程，确认状态码、日志与告警都能正确落地，再考虑对外部收件方使用。

参考：RFC 7293《The Require-Recipient-Valid-Since Header Field and SMTP Service Extension》，W. Mills、M. Kucherawy，2014 年 7 月，Standards Track，DOI 10.17487/RFC7293，https://www.rfc-editor.org/rfc/rfc7293.html ；RFC 5321《Simple Mail Transfer Protocol》，J. Klensin，2008 年 10 月，https://www.rfc-editor.org/rfc/rfc5321.html ；RFC 5322《Internet Message Format》，P. Resnick 编，2008 年 10 月，https://www.rfc-editor.org/rfc/rfc5322.html ；RFC 2142《Mailbox Names for Common Services, Roles and Functions》，D. Crocker，1997 年 5 月，https://www.rfc-editor.org/rfc/rfc2142.html ；RFC 3463《Enhanced Mail System Status Codes》，G. Vaudreuil，2003 年 1 月，https://www.rfc-editor.org/rfc/rfc3463.html ；IANA「Simple Mail Transfer Protocol (SMTP) Enhanced Status Codes Registry」，https://www.iana.org/assignments/smtp-enhanced-status-codes/smtp-enhanced-status-codes.xhtml

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/rfc7293-rrvs-address-reassignment-protection.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
