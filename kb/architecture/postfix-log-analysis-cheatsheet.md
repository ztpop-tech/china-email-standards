---
title: "Postfix 日志该怎么读？排障时最常用的字段与判断路径有哪些？"
source: "https://ztpop.net/kb/postfix-log-analysis-cheatsheet.html"
license: CC-BY 4.0
---

# Postfix 日志该怎么读？排障时最常用的字段与判断路径有哪些？

1
Postfix 日志该怎么读？排障时最常用的字段与判断路径有哪些？
▼

**最重要的一条：一封邮件是「多行同一个队列 ID」，不是一行**

新手读 Postfix 日志最大的障碍是试图从单独一行里读出完整结论。实际上 Postfix 是多组件架构，**一封邮件在处理过程中会经过多个进程，每个进程各自写自己的日志行。**把它们串起来的是**队列 ID**。

因此排障的第一个动作永远是：**拿到队列 ID，然后把该 ID 的所有行按时间取出来，作为一个整体来读。**只看到 `deferred` 就下结论「投递失败了」，往往会漏掉后面几小时里成功重试的那一行。

典型的组件与它们各自负责的部分：

* **smtpd**：处理入站 SMTP 会话。记录客户端连接、认证、以及会话内的拒绝。
* **cleanup**：报文进入队列前的规范化处理。**这里会记录报文的 `Message-ID`，是把队列 ID 与 RFC 5322 报文标识关联起来的关键一行。**
* **qmgr**：队列管理。记录信封发件人、报文大小与收件人数量。
* **smtp / lmtp / local / pipe**：各类投递代理。记录每个收件人的最终投递结果。
* **bounce**：生成投递状态通知。
* **postscreen / tlsproxy** 等：视配置而定，处理连接前置检查与 TLS 相关工作。

完整的组件列表与各自职责见 [Postfix 官方文档索引](https://www.postfix.org/documentation.html)。**不要凭经验猜测某条日志由哪个组件产生——组件名就写在行里，直接看。**

**投递结果行：status 三态与各字段的语义**

投递代理产生的行是排障中最常看的一类，它对应「某一个收件人的一次投递尝试」。**注意是「一个收件人的一次尝试」——一封邮件多个收件人会产生多行，一个收件人多次重试也会产生多行。**

关键字段：

* **`to=`**：本次投递的收件人。
* **`relay=`**：本次投递交给了谁。**这个字段在排障中价值极高**——它直接告诉你邮件走向了哪里。如果它指向了一个意料之外的主机，说明路由配置有问题，而不是对方的问题。
* **`dsn=`**：RFC 3463 定义的增强状态码。第一位数字表示类别（成功、持久失败、临时失败），后面的部分表示更精确的原因分类。**它比自由文本更适合用来做自动化统计。**
* **`status=`**：三态之一，见下。
* **状态后的括号内容**：通常是对方服务器返回的原始响应文本。**排障时这段文本往往是唯一真正有信息量的部分，要完整读，不要只看状态。**

**status 的三态必须严格区分：**

1. **`sent`**：已交付给下一跳并被接受。**注意它只意味着「下一跳接受了」，不意味着「用户看到了」**——邮件可能被对方判为垃圾邮件。这是一个极常见的理解错误。
2. **`deferred`**：**临时失败，仍在队列中，会按退避策略重试。**这不是失败，看到它不必立即处置。真正需要关注的是「持续 deferred 且重试时间越来越长」的情况。
3. **`bounced`**：永久失败，已放弃，通常会生成退信。RFC 3464 定义了投递状态通知的报文格式。

**delays 四段拆解：定位慢在哪一段的最快方法**

投递行中还有两个与时间有关的字段，它们是性能排障中最有价值的信息，但经常被忽略。

**`delay=`** 是本次投递的总耗时。**`delays=`** 则把总耗时拆成四段，按 Postfix 官方文档的定义依次为：

1. **第一段：报文接收前的时间。**从收到请求到报文完全接收进入队列。**这一段异常大，通常意味着入站会话本身慢**——可能是发送方慢，也可能是本机在会话中执行的检查慢（例如 DNS 查询超时）。
2. **第二段：在队列管理器中的时间。****这一段大意味着排队等待**，通常是并发投递槽位不足，或者队列中积压了大量邮件。
3. **第三段：建立连接的时间。****这一段大几乎总是网络或 DNS 问题**——目标主机解析慢、连接超时后重试其他 MX、或者被中间设备限速。
4. **第四段：报文传输的时间。****这一段大通常是对方处理慢或报文很大**，也可能是对方在做同步的内容检查。

**这个拆解的实用价值在于它能立刻把问题从「邮件慢」收敛到具体环节。**四段中哪一段占了绝大部分，排查方向就完全确定了，不需要盲目地从头查起。字段的准确定义与取值含义应以 [Postfix 官方文档索引](https://www.postfix.org/documentation.html) 为准。

队列积压的整体形态则应当用 [Postfix QSHAPE\_README 官方文档](https://www.postfix.org/QSHAPE_README.html) 描述的方法来观察——它按域和年龄给出队列分布，**能直接看出是「所有投递都慢」还是「某一个域拖住了整个队列」**，后者是极常见的情形。

**常见排障路径：从症状直接跳到应查的地方**

**症状：某个域的邮件发不出去。**

* 按队列 ID 取全部行，看 `relay=` 指向哪里、`status=` 与括号内的原始响应文本。
* 如果响应文本是对方给的 5xx，那是对方的策略拒绝，**解决路径在对方或在你的发送信誉上，改本机配置没用。**
* 如果是连接超时，看 delays 的第三段，走网络与 DNS 方向。

**症状：外部邮件进不来，对方说被拒。**

* 查 smtpd 的会话行，找到拒绝发生在会话的哪个阶段。[Postfix SMTPD\_ACCESS\_README 官方文档](https://www.postfix.org/SMTPD_ACCESS_README.html) 说明了访问控制在 SMTP 会话各阶段的作用位置，**知道拒绝发生在哪个阶段，就知道是哪一类规则触发的。**
* RFC 5321 规定了响应码的语义，4xx 与 5xx 的区别决定了对方会不会重试。

**症状：TLS 相关问题。**

* [Postfix TLS\_README 官方文档](https://www.postfix.org/TLS_README.html) 说明了各项 TLS 参数与日志级别的对应关系。**提高 TLS 日志级别可以看到握手细节，但要注意这会显著增加日志量，排查完应当调回。**
* 结合 RFC 3207 的机会性 TLS 语义判断：投递成功但未加密，与投递失败，是两类不同的问题。

**症状：认证相关问题。**

* 查 smtpd 行中与 SASL 相关的字段，区分「认证机制不被支持」与「凭据错误」——**这两者的处置方向完全不同，前者是配置问题，后者是账号问题。**

**症状：邮件被投递到了意外的位置。**

* 看 `relay=` 与地址重写相关的行。**地址重写是 Postfix 中最容易产生意外的部分**，因为多个重写机制会依次作用。

**两个必须养成的习惯：查有效配置，谨慎开调试**

**习惯一：用 postconf 查有效配置，不要读配置文件。**

直接阅读主配置文件会漏掉两类信息：**一是未显式设置的参数所使用的默认值，二是被其他机制覆盖的值。**[Postfix postconf(5) 官方配置参数手册](https://www.postfix.org/postconf.5.html) 是参数的权威手册，而查询当前实际生效值应当用 postconf 工具。**「配置文件里没写」不等于「该功能未启用」**——很多参数有非空的默认值。

排障时一个高效的做法是：**只列出与默认值不同的参数。**这份差异清单通常很短，且几乎必然包含问题所在——因为问题总是出在有人改过的地方。

**习惯二：调试要有针对性，用完立即关闭。**

[Postfix DEBUG\_README 官方文档](https://www.postfix.org/DEBUG_README.html) 给出了 Postfix 的调试方法，其中包括针对特定对端提高日志详细程度的机制。使用时要注意：

* **范围要尽可能小。**只针对出问题的那个对端开启，而不是全局提高日志级别。
* **调试日志可能包含敏感信息**，包括会话内容与认证过程的细节。**开启前要考虑日志的访问控制，排查后要及时关闭并清理。**
* **调试日志量极大**，长时间开启可能撑满磁盘，进而造成比原问题严重得多的故障。

**取证与跨主机关联时的注意事项**

日常排障之外，当日志需要用于事件取证时，还有几点必须注意：

* **队列 ID 不能跨主机使用。**邮件从一台主机转到下一台时，会获得新的队列 ID。**跨主机串联必须靠 `Message-ID`（RFC 5322），而它由 cleanup 组件记录，是把两台主机的日志接起来的唯一可靠桥梁。**排障时养成同时记录队列 ID 与 `Message-ID` 的习惯。
* **队列 ID 存在被复用的可能。**Postfix 提供了长格式队列 ID 的选项以缓解这一问题，具体参数与行为见 [Postfix postconf(5) 官方配置参数手册](https://www.postfix.org/postconf.5.html)。**在跨越较长时间范围检索时，只用队列 ID 匹配可能会取到不相关的记录**，应当同时限定时间范围。
* **日志轮转会静默地删掉关键时段。**取证的第一动作应当是先把相关时段的日志复制到独立位置并计算摘要值，**再开始分析**。[NIST SP 800-86《Guide to Integrating Forensic Techniques into Incident Response》](https://csrc.nist.gov/pubs/sp/800/86/final) 强调收集阶段的完整性决定后续一切。
* **集中化是前提。**RFC 5424 定义的 syslog 协议是把多台主机日志汇聚的通用手段。[NIST SP 800-92《Guide to Computer Security Log Management》](https://csrc.nist.gov/pubs/sp/800/92/final) 给出了日志管理的系统化做法，其中留存期设置尤其关键——**留存期必须覆盖典型的发现延迟，否则等到发现时日志已经不在了。**
* **时间基准要统一。**多台主机的时钟必须同步，且要明确日志记录的是本地时间还是 UTC。**时间不齐，跨主机时间线就是错的。**
* **不要以日志替代原始报文。**日志能重建路径与结果，但回答不了「邮件内容是什么」。涉及内容的问题必须依赖归档的完整原始报文。

参考：[Postfix 官方文档索引](https://www.postfix.org/documentation.html) ；[Postfix postconf(5) 官方配置参数手册](https://www.postfix.org/postconf.5.html) ；[Postfix TLS\_README 官方文档](https://www.postfix.org/TLS_README.html) ；[Postfix DEBUG\_README 官方文档](https://www.postfix.org/DEBUG_README.html) ；[Postfix QSHAPE\_README 官方文档](https://www.postfix.org/QSHAPE_README.html) ；[Postfix SMTPD\_ACCESS\_README 官方文档](https://www.postfix.org/SMTPD_ACCESS_README.html) ；[RFC 3463《Enhanced Mail System Status Codes》](https://www.rfc-editor.org/rfc/rfc3463.html)，G. Vaudreuil，2003 年 1 月 ；[RFC 3464《An Extensible Message Format for Delivery Status Notifications》](https://www.rfc-editor.org/rfc/rfc3464.html)，K. Moore、G. Vaudreuil，2003 年 1 月 ；[RFC 5321《Simple Mail Transfer Protocol》](https://www.rfc-editor.org/rfc/rfc5321.html)，J. Klensin，2008 年 10 月 ；[RFC 5322《Internet Message Format》](https://www.rfc-editor.org/rfc/rfc5322.html)，P. Resnick 编，2008 年 10 月 ；[RFC 5424《The Syslog Protocol》](https://www.rfc-editor.org/rfc/rfc5424.html)，R. Gerhards，2009 年 3 月 ；[RFC 3207《SMTP Service Extension for Secure SMTP over Transport Layer Security》](https://www.rfc-editor.org/rfc/rfc3207.html)，P. Hoffman，2002 年 2 月 ；[NIST SP 800-92《Guide to Computer Security Log Management》](https://csrc.nist.gov/pubs/sp/800/92/final) ；[NIST SP 800-86《Guide to Integrating Forensic Techniques into Incident Response》](https://csrc.nist.gov/pubs/sp/800/86/final)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/postfix-log-analysis-cheatsheet.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
