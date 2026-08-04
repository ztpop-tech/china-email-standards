---
title: "不收邮件的域名应该怎么配置？Null MX 的作用与部署要点是什么？"
source: "https://ztpop.net/kb/rfc7505-null-mx-nonmail-domain-hardening.html"
license: CC-BY 4.0
---

# 不收邮件的域名应该怎么配置？Null MX 的作用与部署要点是什么？

1
不收邮件的域名应该怎么配置？Null MX 的作用与部署要点是什么？
▼

**问题的根源：没有 MX 时的 A/AAAA 回退**

按 SMTP 的收件人域解析规则，发送方先查目标域的 MX 记录；若不存在 MX，则回退使用该域的 A/AAAA 记录，把该地址当作邮件服务器。这一回退规则带来一个长期困扰：**一个从未打算收邮件的域名，只要它有 A/AAAA 记录（例如只跑网站、只做跳转、只用于 SPF 声明），就会被发送方当成可投递目标**。

后果是双向的。对发送方而言，邮件会进入队列并反复重试，直到超时才产生退信，延迟数小时甚至数天；对域名持有者而言，其 Web 服务器的 25 端口要么被反复叩门，要么因为端口不通而让发送方长时间挂起。RFC 7505 正是为了给出一个明确的「本域不收邮件」声明机制而制定的，它把此前靠约定实现的做法形式化，使域名无需提供任何邮件服务器即可宣告不接收邮件。

**Null MX 的记录写法**

RFC 7505 规定：域名要表明不接收邮件，就发布**单条 MX 记录**，其 RDATA 部分由 **preference 数值 0** 与**一个零长度标签**组成——在区文件中零长度标签写作单个点号 `.`，表示「该域不存在邮件交换器」。

```
; 区文件写法
example.com.   IN  MX  0  .
```

三条约束需要牢记：

* **必须是唯一一条 MX**：Null MX 与真实 MX 不能并存于同一域名。若同时存在，语义自相矛盾，不同实现的处理不一致。
* **preference 必须为 0**：这是规范给出的取值，不要写成其他优先级。
* **exchange 为根标签**：即单个点号，不是空字符串、不是本域名、也不是 `localhost`。写成后两者会造成投递环路或指向错误主机。

注意区分层次：Null MX 声明的是「本域不*接收*邮件」，它不涉及本域是否*发送*邮件，也不影响该域的 Web 服务。

**发送方应当如何响应**

RFC 7505 明确了发送侧行为：提交服务器或 SMTP 中继服务器在因目标域的 Null MX 记录而拒绝某个信封收件人时，**应当（SHOULD）使用 556 回复码**（含义为「请求的操作未执行：该域不接受邮件」，该回复码由 RFC 7504 定义）**并附 5.1.10 增强状态码**（永久失败：收件人地址具有 null MX）。

RFC 7505 同时把 X.1.10 登记进了 SMTP 增强状态码注册表的枚举状态码子注册表，示例文本为「Recipient address has null MX」，关联基础状态码为 556。

这一设计的价值在于**把不可投递的判定提前到解析阶段并转为永久失败**：发送方不再入队、不再重试，用户立刻拿到明确退信。排错时若看到 556 / 5.1.10，含义非常确定——不是网络不通，不是被反垃圾拦截，而是对方域名主动声明了不收邮件，重发无意义，应核对收件地址是否写错了域名。

**在什么域名上部署**

Null MX 的典型适用对象包括：

* **防御性注册的相似域名**：为防仿冒而囤积的拼写变体域、品牌变体域。这类域名通常有解析但从不收信，是被冒用发信与被误投的高发对象。
* **纯站点域与营销落地域**：只承载网页、只做 301 跳转的域名。
* **基础设施子域**：如仅用于 CDN、API、静态资源的子域。
* **已停用的历史域名**：业务下线后仍保留注册以防被抢注的域名。

反之，**凡是可能接收退信（DSN）、订阅确认、告警回执或人工回复的域名，都不应设 Null MX**。一个常见的自伤场景是：某域名仅用于发送系统通知，管理员认为「反正不用收信」而设了 Null MX，结果所有退信与投诉反馈无处可去，投递问题彻底失去可观测性。发信域至少应保留可达的 postmaster 与 abuse 收件能力。

**与 SPF、DMARC 的配套：三件套一起做**

Null MX 只解决「不收」，不解决「不被冒用发」。未使用域名的完整收敛需要三条记录同时到位：

* **Null MX**：声明不接收邮件（见上）。
* **SPF 硬失败**：发布 `v=spf1 -all`，依据 RFC 7208，该记录表示没有任何主机被授权代表本域发信，接收方对声称来自本域的邮件应判定为 fail。
* **DMARC 拒绝策略**：发布策略为 reject 的 DMARC 记录，使对齐失败的邮件被直接拒绝。DMARC 规范目前由 RFC 9989 承载，它连同 RFC 9990、RFC 9991 取代了此前的 RFC 7489。

```
example.com.        IN  MX   0 .
example.com.        IN  TXT  "v=spf1 -all"
_dmarc.example.com. IN  TXT  "v=DMARC1; p=reject; rua=mailto:dmarc@yourdomain.example"
```

三点实施提醒：**其一，子域不会自动继承**——MX 与 SPF 都是按具体名字查询的，父域的 Null MX 不会保护子域，需要为实际可能被冒用的子域单独发布，或依赖 DMARC 的子域策略；**其二，rua 地址要放在一个真正能收信的域上**，否则报告本身会因为 Null MX 而被拒；**其三，上线前先查现状**，用 `dig MX example.com` 与 `dig TXT example.com` 确认没有正在使用的邮件流，再变更，避免误伤仍在收信的域名。

参考：RFC 7505《A "Null MX" No Service Resource Record for Domains That Accept No Mail》，J. Levine、M. Delany，2015 年 6 月，Proposed Standard，DOI 10.17487/RFC7505，https://www.rfc-editor.org/rfc/rfc7505.html ；RFC 7504《SMTP 521 and 556 Reply Codes》，J. Klensin，2015 年 6 月，DOI 10.17487/RFC7504，https://www.rfc-editor.org/rfc/rfc7504.html ；RFC 5321《Simple Mail Transfer Protocol》，J. Klensin，2008 年 10 月，https://www.rfc-editor.org/rfc/rfc5321.html ；RFC 1034《Domain names - concepts and facilities》，P. Mockapetris，1987 年 11 月，STD 13，https://www.rfc-editor.org/rfc/rfc1034.html ；RFC 7208《Sender Policy Framework (SPF) for Authorizing Use of Domains in Email, Version 1》，S. Kitterman，2014 年 4 月，https://www.rfc-editor.org/rfc/rfc7208.html ；RFC 9989《Domain-Based Message Authentication, Reporting, and Conformance (DMARC)》，T. Herr、J. Levine 编，2026 年 5 月，https://www.rfc-editor.org/rfc/rfc9989.html

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/rfc7505-null-mx-nonmail-domain-hardening.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
