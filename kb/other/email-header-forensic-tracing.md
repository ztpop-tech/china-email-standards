---
title: "邮件头溯源到底该怎么读？哪些字段是标准规定可信的？"
source: "https://ztpop.net/kb/email-header-forensic-tracing.html"
license: CC-BY 4.0
---

# 邮件头溯源到底该怎么读？哪些字段是标准规定可信的？

1
邮件头溯源到底该怎么读？哪些字段是标准规定可信的？
▼

**Received 行由谁写、写在哪里**

RFC 5321 第 4.4 节（Trace Information）规定了追踪信息的语法与语义。写入时机在第 4.1.1.4 节（DATA 命令）说明：当 SMTP 服务器接受一封邮件用于中继或最终投递时，它会在邮件数据的**顶部**插入一条追踪记录（即 Received 行），经过多跳中继的邮件因此会有多条时间戳行。第 3.7.2 节进一步规定：网关在把邮件转入或转出互联网环境时，必须在最前面添加 Received 行，且**不得以任何方式改动已存在的 Received 行**。

**邮件格式侧的对应规定**

RFC 5322 第 3.6.7 节（Trace Fields）给出 trace 字段的语法：trace = [return] 1\*received，其中 return 即 Return-Path 字段、received 即 Received 字段。第 3.6 节（Field Definitions）作出关键约束：追踪字段与 Resent 字段**不得被重新排序**，且应以整块形式前置追加到邮件中。这条约束正是自上而下阅读 Received 即为逆时序路径的规范依据。

**会话串联字段**

RFC 5322 第 3.6.4 节（Identification Fields）定义 Message-ID、In-Reply-To、References 三个字段。溯源时它们的价值在于：Message-ID 是跨主机日志关联同一封邮件的天然主键；In-Reply-To 与 References 可还原会话树，用于判断一封续在真实会话里的邮件是否存在断链——这对识别线程劫持类攻击尤其关键。此外第 3.6.6 节定义 Resent 字段，并说明每组新的 Resent 字段是前置追加的，即最近一组出现在更靠前的位置。

**认证结果字段怎么看**

RFC 8601 定义 Authentication-Results 头字段：第 2.2 节给出形式化 ABNF 语法；第 2.5 节定义认证服务标识符 authserv-id 及其唯一性要求；第 2.7 节给出各方法与结果值——2.7.1 为 DKIM（none/pass/fail/policy/neutral/temperror/permerror）、2.7.2 为 SPF、2.7.3 为 iprev（其机制另在第 3 节详述）。**读这个字段的第一件事是核对 authserv-id 是否为本组织的认证服务标识**，否则该字段可能来自信任边界之外。

**防伪造：必须删除的头**

RFC 8601 第 5 节（Removing Existing Header Fields）规定：符合规范的 MTA 必须删除那些声称由本信任边界内添加、但实际并非来自受信 MTA 的 Authentication-Results 头字段。第 7.1 节（Forged Header Fields）补充了对应的风险讨论。**如果边界上没有做这一步剥离，攻击者只需自行伪造一行 pass，下游的所有判定都会被污染。**

参考：https://www.rfc-editor.org/rfc/rfc5321.txt 、https://www.rfc-editor.org/rfc/rfc5322.txt 、https://www.rfc-editor.org/rfc/rfc8601.txt

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-header-forensic-tracing.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
