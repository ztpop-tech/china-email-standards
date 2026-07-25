---
title: "SPF 发件人策略框架深度解析 — RFC 7208：从 SPF Classic 到 DMARC 基石 · ztpop 邮件技术知识库"
source: "https://ztpop.net/kb/spf-guide.html"
license: CC-BY 4.0
---

# SPF 发件人策略框架深度解析 — RFC 7208：从 SPF Classic 到 DMARC 基石 · ztpop 邮件技术知识库

SPF 发件人策略框架深度解析 — RFC 7208：从 SPF Classic 到 DMARC 基石

#### 📑 目录

1. [信封发件人与头域发件人：SPF 验证的对象到底是什么](#s1)
2. [从 SPF Classic (RFC 4408) 到 RFC 7208](#s2)
3. [八种机制逐项解析](#s3)
4. [四种限定符：-all / ~all / +all / ?all](#s4)
5. [SPF 宏展开机制](#s5)
6. [10 次 DNS 查询上限与展开审计](#s6)
7. [SPF 与 DMARC 协同：Identifier Alignment](#s7)
8. [常见配置模板](#s8)
9. [运维诊断：dig / spfquery / check\_host()](#s9)

## 一、信封发件人与头域发件人：SPF 验证的对象到底是什么

理解 SPF 的第一步，是先搞清楚它保护的是
**谁**
。SPF 不关心中文邮件客户端里显示的"发件人"字段，它只验证 SMTP 会话层上的信封发件人地址——也就是
`MAIL FROM`
（或称 Return-Path）。这是很多人第一次接触 SPF 时最容易绕进去的概念陷阱。

邮件协议栈里有两层"发件人"概念，它们分别来自两个不同的 RFC：

一、信封发件人与头域发件人：SPF 验证的对象到底是什么

| 层次 | 所在协议 | 典型字段 | 谁验证它 |
| --- | --- | --- | --- |
| SMTP 信封 | RFC 5321 | `MAIL FROM:` （Return-Path） | **SPF** |
| 邮件头域 | RFC 5322 | `From: User Name` | **DKIM** （通过签名验证） |

SPF 的设计目标很明确：
**让接收方 MTA 能够验证发起 SMTP 连接的 IP 是否有权代表某个域发送邮件**
（RFC 7208, Section 1）。这个"代表某个域"的域，就是
`MAIL FROM`
中
`@`
后面的部分——SPF 称之为
`MAIL FROM`
域。举个例子：

```
# SMTP 会话中的实际流程
S: 220 mx.receiver.com ESMTP Ready
C: EHLO mail.sender.com
S: 250-STARTTLS
S: 250 OK
C: MAIL FROM:    ← SPF 验证的就是这个域
S: 250 OK
C: RCPT TO:
S: 250 OK
C: DATA
S: 354 Start mail input
C: From: "ACME Newsletter"      ← SPF 不碰这个
C: To: recipient@receiver.com
C: Subject: Weekly Update
C: ...
```

这里
`MAIL FROM`
是
`marketing.example.com`
，而邮件头中
`From:`
是
`acme.com`
。SPF 检查的是前者。这意味着即使 SPF PASS，头域里的
`From:`
地址仍然可能被伪造——这正是 DMARC 要解决的问题（详见
[第七节](#s7)
）。

### 1.1 Return-Path 的"反弹路径"属性

`MAIL FROM`
还有一个重要身份：它是
**退信（bounce）的接收地址**
。当邮件投递失败时，MTA 会向这个地址发送 DSN（Delivery Status Notification）。SPF 同时保护了两件事：阻止伪造域发信，以及阻止攻击者利用你的域名作为退信攻击的受害目标（backscatter）。RFC 7208, Section 2.3 明确指出，SPF 检查的是
`MAIL FROM`
身份和
`HELO`
身份，不涉及任何邮件头域。

**常见误解：**

"我设了 SPF -all，为什么垃圾邮件还能伪造我的 From: 地址？"——因为 SPF 根本不检查 From: 头。没有 DKIM 和 DMARC 搭配的 SPF 只能防止信封域伪造，挡不了头域伪造。

## 二、从 SPF Classic (RFC 4408) 到 RFC 7208

SPF 的历史在邮件协议演进里算得上曲折。最早的 SPF 实验性规范出现在 2003 年前后，2006 年由 IETF 正式发布为 RFC 4408（SPF Classic，也称 Sender ID 的前身之一）。经过近十年的部署实践和社区反馈，IETF 于 2014 年发布了 RFC 7208，将 SPF 从"实验性"提升为"建议标准"（Proposed Standard），同时对多处语义做了收紧和明确。

### 2.1 RFC 4408 → RFC 7208 的关键变更

2.1 RFC 4408 → RFC 7208 的关键变更

| 方面 | RFC 4408 (2006) | RFC 7208 (2014) |
| --- | --- | --- |
| 地位 | 实验性（Experimental） | 建议标准（Proposed Standard） |
| `ptr` 机制 | 推荐但不强制弃用 | **明确不推荐使用** （Section 5.5） |
| DNS 查询限制 | 10 次，含所有机制 | 10 次，明确 `redirect=` 也计入 |
| 宏展开 | 8 个宏变量 | 增加 `%{v}` （收件人域）等，更完整的转义规则（Section 7） |
| `exists` 机制 | 定义模糊 | 明确为 DNS A 查询，返回任意 A 记录即匹配（Section 5.7） |
| 国际化邮件 | 未涉及 | 增加对 EAI（SMTPUTF8）的兼容说明 |

RFC 7208 最值得关注的改变之一是对
`ptr`
机制的明确弃用立场。在 SPF Classic 时代，
`ptr`
是一个看似精妙的设计——允许域管理员说"任何 PTR 记录指向我所在域的主机都可以替我发信"。但实际部署中，PTR 记录的维护质量参差不齐，反向 DNS 的可靠性远低于正向 DNS，并且
`ptr`
会触发不可预测的额外 DNS 查询链。RFC 7208, Section 5.5 的原文措辞相当严厉：
*"The use of this mechanism is strongly discouraged. It is slow, it is not as reliable as other mechanisms, and its use is declining."*

### 2.2 SPF 记录的位置与格式

SPF 策略以 DNS TXT 记录的形式发布在域的权威 DNS 服务器上。RFC 7208, Section 3 规定格式以
`v=spf1`
开头，后跟若干
`机制`
+
`限定符机制`
的组合，以
`all`
机制收尾：

```
# 典型的 SPF 记录（DNS TXT 类型）
example.com.  IN  TXT  "v=spf1 mx ip4:192.0.2.1 include:_spf.thirdparty.com ~all"
```

注意
`all`
必须出现在记录末尾——标准要求
`all`
之后不能再有任何机制（RFC 7208, Section 5.1）。如果记录中出现了
`all`
但不是最后一项，结果定义为
`PermError`
。

此外，RFC 7208 明确指出，SPF 同时支持 TXT 和 SPF 类型的 DNS 记录（Section 3.1），但 SPF 类型已被废弃。实际上几乎所有的 SPF 部署都使用 TXT 记录，因为历史上有太多 DNS 提供商不支持 SPF 类型的记录。

## 三、八种机制逐项解析

SPF 的核心是一套匹配引擎。当一个 SMTP 客户端连接到接收方 MTA 时，check\_host() 函数（RFC 7208, Section 4）会解析 SPF 记录中从左到右列出的每一项机制，找到第一个匹配就停止并返回结果。以下是八种机制的逐一拆解。

### 3.1 ip4 / ip6 — 最基础的 IP 范围授权

`ip4`
和
`ip6`
是最常用、性能最优的机制。它们不触发任何 DNS 查询，直接做 CIDR 匹配：

```
# 授权单个 IPv4
v=spf1 ip4:192.0.2.10 -all

# 授权整个 /24 子网
v=spf1 ip4:192.0.2.0/24 -all

# IPv6 同样支持 CIDR
v=spf1 ip6:2001:db8::/32 -all
```

如果没有指定 CIDR 掩码长度，
`ip4`
默认为
`/32`
，
`ip6`
默认为
`/128`
——即精确匹配单个地址（RFC 7208, Section 5.6）。

### 3.2 a — 按域名的 A/AAAA 记录匹配

`a`
机制查询指定域名的 A 或 AAAA 记录，将其解析出的 IP 地址与连接 IP 做匹配。如果不指定域名，默认是当前域（即 SPF 记录所在的域）：

```
# 匹配 example.com 的 A/AAAA 记录
v=spf1 a -all

# 匹配 mail.example.com 的 A/AAAA 记录（/28 子网内的任何地址）
v=spf1 a:mail.example.com/28 -all
```

`a`
机制至少触发 1 次 DNS 查询（A 记录），如果同时支持 IPv6 则为 2 次（A + AAAA）。它占 1 次机制计数，但 DNS 查询次数取决于实现（RFC 7208, Section 5.3）。

### 3.3 mx — 按 MX 记录引出的主机授权

`mx`
机制比
`a`
多一层间接引用：它先查域的 MX 记录，得到一组主机名，然后对每个主机名再查 A/AAAA 记录，将所有这些 IP 与连接 IP 做匹配。如果不指定域，默认为当前域：

```
# example.com 的所有 MX 主机，及其 /24 子网内的地址均可发信
v=spf1 mx/24 -all
```

**风险提示：**
`mx`
可能引发大量 DNS 查询。如果 MX 记录指向 3 台主机，每台同时有 A 和 AAAA 记录，那么
`mx`
机制可能触发 3 × 2 = 6 次额外 DNS 查询（RFC 7208, Section 5.4）。对于邮件网关和托管邮件服务场景，直接使用
`ip4`
列出具体 IP 往往比
`mx`
更可控。

### 3.4 include — 递归引用另一个域的 SPF 策略

`include`
是解决"第三方服务商替我发信"场景的核心机制。它的语义是：
**暂停当前记录的评估，跳转到目标域的 SPF 记录，从头开始评估**
；如果目标域返回 Pass，那么当前
`include`
也视为匹配（RFC 7208, Section 5.2）。

```
# 将 _spf.example-esp.com 域下所有授权 IP 纳入本域信任范围
v=spf1 mx include:_spf.example-esp.com -all
```

重要细节：

* `include`
  不改变
  参数——被包含的 SPF 记录仍然以原始
  `MAIL FROM`
  地址为验证目标
* 被包含域的 DNS 查询
  **全部计入 10 次限制**
* 如果被包含域没有 SPF 记录或返回错误，整个
  `include`
  机制算作不匹配，继续评估下一条

### 3.5 exists — DNS A 查询断言

`exists`
是一个特殊的"断言式"机制：它构造一个域名，对该域名执行 DNS A 查询。如果返回任意 A 记录（无论 IP 值是多少），匹配成功；如果返回 NXDOMAIN，不匹配（RFC 7208, Section 5.7）。

```
# exists 常与宏结合使用——详细信息见第五节
v=spf1 exists:%{i}._spf.%{d} -all
```

`exists`
最常见的应用场景是配合 SPF 宏做
**动态白名单**
：先预置一个 DNS 区域，按连接 IP 或发件域生成子域名，当 exists 查询到该子域名有 A 记录时放行。这种方法允许运维人员在不修改 SPF TXT 记录的情况下动态调整授权——只需增删 DNS 子域。

### 3.6 ptr — 已被弃用的反向 DNS 匹配

`ptr`
机制检查连接 IP 的反向 DNS（PTR 记录），看其对应的主机名是否属于指定域（RFC 7208, Section 5.5）。RFC 7208 明确声明不推荐使用，保留它仅为了向后兼容。原因包括：

* PTR 记录的维护通常不在发件域管理员控制之下（由 ISP 管理）
* 会触发多次 DNS 查询（先查 PTR，再对结果做正向 A 查询验证）
* 查询结果不可靠，大量邮件系统未配置或配置错误的 PTR 记录

**建议：如果你还在维护一条包含
`ptr`
的 SPF 记录，应该尽快用
`ip4`
/
`a`
替代它。**

### 3.7 redirect — 替代 ALL 的"代理"机制

`redirect=`
不是一个普通机制，而是一个修饰符（modifier）。当它出现时，当前 SPF 记录的评估结果被完全替换为目标域 SPF 记录的评估结果（RFC 7208, Section 6.1）。它与
`include`
的关键区别：

3.7 redirect — 替代 ALL 的"代理"机制

| 特性 | `include` | `redirect=` |
| --- | --- | --- |
| 触发时机 | 作为机制被逐一评估 | **替代整个 SPF 评估结果** |
| 如果目标域没有 SPF 记录 | 不匹配，继续 | 返回 PermError |
| 典型用途 | 扩展信任源 | 子域将 SPF 托管到父域 |

```
# 子域不维护独立的 SPF 记录，直接将评估代理到父域
subdomain.example.com.  IN  TXT  "v=spf1 redirect=example.com"
```

### 3.8 all — 兜底机制

`all`
永远匹配任何 IP，它是 SPF 记录的"默认分支"。
`all`
必须前面带有限定符（见下一节），并且必须是记录的
**最后一项**
（RFC 7208, Section 5.1）。

## 四、四种限定符：-all / ~all / +all / ?all

SPF 中每个机制前面都可以加一个限定符（qualifier），决定匹配后的返回值（RFC 7208, Section 4.6）：

四、四种限定符：-all / ~all / +all / ?all

| 限定符 | 符号 | 结果 | 语义 |
| --- | --- | --- | --- |
| `-` | Fail | 硬拒绝 | "这个 IP 明确无权代表本域发信，请拒绝" |
| `~` | SoftFail | 软拒绝 | "这个 IP 可能无权，建议谨慎处理但不强制拒绝" |
| `+` | Pass | 放行 | "这个 IP 授权代表本域发信" |
| `?` | Neutral | 中性 | "不做任何断言，接收方自行判断" |

`+`
是默认限定符，不写符号就等同于
`+`
。在
`all`
机制上的限定符选择直接决定了域的 SPF 策略强度：

```
# 硬拒绝 — 最高安全级别，任何不在列表中的 IP 一律 Fail
v=spf1 ip4:192.0.2.0/24 -all

# 软拒绝 — 过渡期/低风险域常用，相当于"建议垃圾邮件文件夹"
v=spf1 ip4:192.0.2.0/24 ~all

# 完全不设防 — 本域不参与 SPF 判断（几乎等同于没有 SPF）
v=spf1 +all

# 中性 — 不做断言，等同于"SPF 未配置"
v=spf1 ?all
```

### 4.1 -all vs ~all 的实战决策

这个问题在邮件运维社区里被反复争论。核心矛盾在于：
```` -all
能更有效地防止域名被滥用，但如果 SPF 记录本身有遗漏（比如新上了一个发信服务但忘了加
include
），合法的邮件会被硬拒绝。以下是决策框架：

* 选
  -all
  ：
  发信源完全可控（自建 MTA + 已知的第三方 ESP）、已部署 DMARC 且
  p=reject
  、对域名声誉有严格要求
* 选
  ~all
  ：
  发信源可能动态变化、处于 SPF 部署初期/过渡期、不想冒合法邮件被拒的风险

RFC 7208, Section 4.6 并不强制推荐任何一种——它把选择权留给域管理员。

## 五、SPF 宏展开机制

SPF 宏（macro）是 SPF 中最被低估但也最强大的特性。它允许 SPF 记录中包含变量占位符，check_host() 在评估时用实际值替换这些变量（RFC 7208, Section 7）。

### 5.1 核心宏变量

5.1 核心宏变量

| 宏 | 替换为 | 示例（发件人 user@example.com，IP 192.0.2.10） |
| --- | --- | --- |
| %{s} | 发件人本地部分（localpart） | user |
| %{l} | 发件人本地部分（同上，保留大小写） | user |
| %{o} | 发件人域（MAIL FROM 域的域名部分） | example.com |
| %{d} | 当前评估域（通常是 SPF 记录所在域） | example.com |
| %{i} | 连接 IP（点分十进制或冒号分隔的 IPv6） | 192.0.2.10 |
| %{h} | HELO/EHLO 声明的域名 | mail.example.com |
| %{v} | 收件人域（RCPT TO 之后的域） | receiver.com |

### 5.2 宏的实用场景：动态 exists 白名单

以下是一条使用宏的真实 SPF 记录模式（RFC 7208, Section 7.3 的示例模式）：

```
# 为每个发件地址动态查询 DNS，实现精细粒度的授权
v=spf1 exists:%{l}._spf.%{d} -all
```

当
user@example.com
通过 IP
192.0.2.10
发信时，这条记录会展开为：

```
# check_host() 实际执行的 DNS 查询
dig A user._spf.example.com
```

如果该域名有 A 记录，
exists
匹配成功，返回 Pass。DNS 运维人员可以通过增删
user._spf.example.com
的 A 记录来动态控制权限——无需触碰 SPF TXT 记录本身。

### 5.3 转义与限定符

宏变量支持转义：在
%{
和
}
之间、变量名之后可以加数字限定符表示截取前 n 个字节，再加
r
表示反转（reverse）——这些在构建复杂
exists
域名时非常有用（RFC 7208, Section 7.2）。

```
# 取 IP 的前 3 个字节（网络部分），反转后再拼接
%{ir3}  → 对于 192.0.2.10 → ur: 10.2.0.192 → 截取前3字节 → 10.2.0
```

## 六、10 次 DNS 查询上限与展开审计

SPF 最容易被忽视但又最容易踩坑的约束是
10 次 DNS 查询限制
。RFC 7208, Section 4.6.4 明确规定：
"SPF implementations MUST limit the total number of mechanisms and modifiers that cause DNS lookups to at most 10 per SPF check, including any lookups caused by the use of the 'include' mechanism or the 'redirect' modifier."
超过 10 次，结果直接返回
PermError
。

这个限制的动机是防止 SPF 评估本身成为 DoS 攻击向量——如果攻击者构造一条会造成无限递归或大量 DNS 查询的 SPF 记录，接收方 MTA 资源可能被耗尽。

### 6.1 哪些操作计入 10 次限制

6.1 哪些操作计入 10 次限制

| 机制 | 计入次数 | 备注 |
| --- | --- | --- |
| a | 1 | 每次触发至少 1 次（A 查询），可能触发 AAAA 查询但不额外计数 |
| mx | 1（机制） + N（MX 结果数） | 每台 MX 主机至少 1 次 A 查询 |
| include | 1（机制） + 被包含域的所有查询 | 被包含域的完整查询计入 |
| exists | 1 | 一次 A 查询 |
| ptr | 1 | 但实际触发多次（PTR + 正向验证） |
| redirect= | 0（自身）+ 目标域所有查询 | 目标域的完整查询计入 |
| ip4 / ip6 | 0 | 不触发 DNS |

### 6.2 审计 SPF 记录的 DNS 查询量

手动审计一条 SPF 记录的 DNS 展开量：

```
# 示例：一条看似简单但实际超限的 SPF 记录
v=spf1 include:esp1.com include:esp2.com include:esp3.com include:esp4.com include:esp5.com include:esp6.com include:esp7.com include:esp8.com include:esp9.com include:esp10.com include:esp11.com -all
```

这里仅
include
本身就已经 11 次了，再加上每个被包含域内部的机制查询，这条记录几乎一定会返回 PermError。很多邮件发送失败的原因不是配置错误，而是 SPF 记录"太膨胀"了。

审计工具链：

```
# 用 dig 手动解析 include 链
dig TXT _spf.esp1.com +short

# 用 spfquery 查看完整评估路径（输出中包含 DNS 查询计数）
spfquery --scope mfrom --id user@example.com --ip 192.0.2.10 \
  --helo mail.example.com --debug

# 在线工具（在浏览器中访问）
# 搜索 "SPF record checker" 使用任意公开的工具，关注 "DNS lookups" 计数
```

### 6.3 减少 DNS 查询的实战技巧

* 展开再折叠：
  用
  ip4
  替代
  a
  和
  mx
  可以减少查询次数
* 合并 include：
  如果有多个第三方 ESP 但它们的出站 IP 范围已知且稳定，可以直接写
  ip4
  CIDR 而不使用
  include
* 自建扁平化记录：
  对于大型组织，可以维护一个内部的 IP 范围列表，生成一条不含任何 include 的扁平 SPF 记录
* 子域隔离：
  将不同的发信功能拆分到不同子域（newsletter.example.com、transactional.example.com），每个子域只维护自己的小范围 SPF

## 七、SPF 与 DMARC 协同：Identifier Alignment

前面第一节提到，SPF 只验证
MAIL FROM
域（RFC 5321 信封域），而终端用户看到的是邮件头中的
From:
域（RFC 5322 头域）。如果这两个域不一致，SPF Pass 对用户没有意义——攻击者可以设置一个攻击者自己控制的
MAIL FROM
域并通过 SPF，同时让
From:
显示为受害者的域名。

DMARC（RFC 7489）正是为了解决这个"域对齐"问题而设计的。它的核心概念是
Identifier Alignment
：SPF 认证的域和 DKIM 签名的域，至少有一个必须与
From:
头域"对齐"。

### 7.1 SPF Alignment 的两种模式

DMARC 为 SPF 对齐定义了两种模式（RFC 7489, Section 3.1.1）：

7.1 SPF Alignment 的两种模式

| 模式 | 匹配规则 | 示例（MAIL FROM 域 vs From 头域） |
| --- | --- | --- |
| Relaxed | 组织域相同即可（匹配注册域部分） | mail.example.com ↔ example.com ✅ 匹配 |
| Strict | 必须完全相同（全字符串匹配） | mail.example.com ↔ example.com ❌ 不匹配 |

Relaxed 模式更实用——它允许你在
MAIL FROM
使用子域（如
bounces.example.com
），同时
From:
头域显示
example.com
。Strict 模式要求两个域逐字符相同，虽然更安全但灵活性低。

### 7.2 DMARC 记录中的 sp= 标签

```
# 针对 example.com 的 DMARC 记录
_dmarc.example.com.  IN  TXT  "v=DMARC1; p=reject; sp=reject; rua=mailto:dmarc@example.com; ruf=mailto:forensic@example.com; aspf=r"
```

上面这条记录中：

* p=reject
  ：主域策略——SPF 或 DKIM 未对齐时拒绝邮件
* sp=reject
  ：子域策略——同上
* aspf=r
  ：SPF 对齐模式为 Relaxed（
  s
  则为 Strict）
* rua
  /
  ruf
  ：聚合/取证报告接收地址

### 7.3 完整的邮件认证链路

一条邮件经过完整的认证流程，大致如下：

```
SMTP 连接建立
  │
  ├─ SPF check_host()
  │   ├─ MAIL FROM 域 = example.com
  │   ├─ 连接 IP = 203.0.113.45
  │   ├─ 评估 SPF 记录 → include 匹配 → Pass
  │   └─ 返回: Pass
  │
  ├─ DKIM 验证
  │   ├─ 提取 DKIM-Signature 头
  │   ├─ 查询 d=example.com 的 DKIM 公钥
  │   ├─ 重新计算哈希 → 匹配
  │   └─ 返回: Pass (d=example.com)
  │
  ├─ DMARC 评估
  │   ├─ From: 头域 = example.com
  │   ├─ SPF 域 = example.com → ✅ 对齐 (Relaxed)
  │   ├─ DKIM 域 = example.com → ✅ 对齐
  │   ├─ 至少一个对齐 + Pass → DMARC Pass
  │   └─ 策略 p=reject → 若未对齐则拒绝，此处 Pass
  │
  └─ 投递到收件箱 ✓
```

关键认知：
SPF 独自使用只能防止 MAIL FROM 域冒充；要防止 From: 头域冒充，必须 SPF + DMARC（或 DKIM + DMARC）协同工作。任何单一认证协议都不足以应对现代邮件欺诈的复杂度。

## 八、常见配置模板

### 8.1 简单域 — 单一 MTA 自建发信

```
# 仅自己服务器发信，MTA 在 mx.example.com（IP: 198.51.100.10）
# 同时允许 IPv6 地址（如果启用）
example.com.  IN  TXT  "v=spf1 ip4:198.51.100.10 ip6:2001:db8::10 mx -all"
```

### 8.2 多云多邮发域 — 自建 + 第三方 ESP

```
# 场景：
#   - 自建 MTA（192.0.2.0/24）
#   - 营销邮件通过 ESP-A 发送
#   - 事务邮件通过 ESP-B 发送
# DNS 查询：include×2 + a×1 + mx×1(2台MX) = 约 6 次（在 10 次限制内）
example.com.  IN  TXT  "v=spf1 ip4:192.0.2.0/24 a include:_spf.esp-a.com include:_spf.esp-b.com -all"
```

### 8.3 使用子域隔离 — 推荐模式

```
# 主域：不允许任何发信（所有发信通过子域）
example.com.  IN  TXT  "v=spf1 -all"

# 营销子域：由 ESP-A 独家发信
newsletter.example.com.  IN  TXT  "v=spf1 include:_spf.esp-a.com -all"

# 事务子域：由 ESP-B 独家发信
transactional.example.com.  IN  TXT  "v=spf1 include:_spf.esp-b.com -all"

# 企业邮件子域：自建 MTA
corp.example.com.  IN  TXT  "v=spf1 ip4:192.0.2.0/24 mx -all"
```

这种模式的优点是：每个子域的 SPF 记录极短，DNS 查询量可控，一种发信通道出问题不影响其他通道。

### 8.4 完全不发信的域 — 防御性 SPF

```
# 对于纯 Web 域、API 域等从不发送邮件的域
example.com.  IN  TXT  "v=spf1 -all"
```

这条"零授权"记录的意义在于明确声明"本域不发送任何邮件"——防止攻击者伪造该域发信（RFC 7208, Section 4.6）。即便该域没有邮件服务器，也应该设置这条记录。

## 九、运维诊断：dig / spfquery / check_host()

SPF 配置完成后需要在真实环境中验证。以下是三个层次的诊断工具。

### 9.1 dig — 最基本的手动查询

```
# 查询 SPF 记录（TXT 类型）
dig TXT example.com +short

# 追踪 include 链中的某一层
dig TXT _spf.esp-a.com +short

# 查询 MX 记录（用于理解 mx 机制的展开范围）
dig MX example.com +short

# 查询 A 记录（用于理解 a 机制的展开范围）
dig A mail.example.com +short

# 模拟 exists 机制查询
dig A 192.0.2.10._spf.example.com +short
```

### 9.2 spfquery — SPF 官方验证工具

spfquery
是 libspf2 提供的命令行工具，可以完整模拟 check_host() 流程：

```
# 安装（Debian/Ubuntu）
apt install libspf2-2 spf-tools-perl

# 以 MAIL FROM 身份验证（--scope mfrom）
spfquery --scope mfrom \
  --id user@example.com \
  --ip 203.0.113.45 \
  --helo mail.sender.com

# 输出示例：
# spfquery: domain of example.com designates 203.0.113.45 as permitted sender
# Received-SPF: pass (example.com: ...)
# 
# 带调试输出（查看 DNS 查询次数和评估路径）
spfquery --scope mfrom --id user@example.com --ip 203.0.113.45 --debug 2>&1
```

### 9.3 check_host() 流程的 Python 实现

以下是用 Python 实现的简化版 check_host()，展示 SPF 评估的核心逻辑（RFC 7208, Section 4 的流程骨架）：

```
#!/usr/bin/env python3
"""
check_host() — RFC 7208 Section 4 的简化实现
用于理解 SPF 评估流程，非生产级代码
"""

import dns.resolver
import ipaddress
import re
import sys

DNS_QUERY_LIMIT = 10

def get_spf_record(domain: str, dns_count: list) -> str | None:
    """查询域的 SPF TXT 记录，返回第一条以 v=spf1 开头的记录"""
    if dns_count[0] >= DNS_QUERY_LIMIT:
        return None
    dns_count[0] += 1
    try:
        answers = dns.resolver.resolve(domain, 'TXT')
        for rdata in answers:
            text = ''.join(s.decode() for s in rdata.strings)
            if text.startswith('v=spf1'):
                return text
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers):
        pass
    return None

def resolve_a(hostname: str, dns_count: list) -> list[str]:
    """解析 A 记录，返回 IP 列表"""
    if dns_count[0] >= DNS_QUERY_LIMIT:
        return []
    dns_count[0] += 1
    try:
        return [str(r) for r in dns.resolver.resolve(hostname, 'A')]
    except Exception:
        return []

def resolve_mx(domain: str, dns_count: list) -> list[str]:
    """解析 MX 记录，返回所有 MX 主机的 IP 列表"""
    if dns_count[0] >= DNS_QUERY_LIMIT:
        return []
    dns_count[0] += 1
    ips = []
    try:
        answers = dns.resolver.resolve(domain, 'MX')
        for mx in sorted(answers, key=lambda r: r.preference):
            ips.extend(resolve_a(str(mx.exchange), dns_count))
    except Exception:
        pass
    return ips

def evaluate_mechanism(
    mechanism: str,
    domain: str,
    sender: str,
    client_ip: str,
    dns_count: list
) -> str | None:
    """
    评估单个 SPF 机制，返回结果字符串或 None（不匹配）
    结果: "pass" | "fail" | "softfail" | "neutral" | "permerror"
    """
    client_ip_obj = ipaddress.ip_address(client_ip)
    prefix = mechanism[0] if mechanism[0] in '+-~?' else '+'
    mech = mechanism if prefix in '+-~?' and mechanism[0] in '+-~?' else mechanism
    if mechanism[0] in '+-~?':
        mech = mechanism[1:]
    else:
        mech = mechanism

    result_map = {'+': 'pass', '-': 'fail', '~': 'softfail', '?': 'neutral'}

    # ip4
    if mech.startswith('ip4:'):
        cidr = mech[4:]
        if '/' not in cidr:
            cidr += '/32'
        if isinstance(client_ip_obj, ipaddress.IPv4Address):
            if client_ip_obj in ipaddress.ip_network(cidr, strict=False):
                return result_map[prefix]

    # ip6
    elif mech.startswith('ip6:'):
        cidr = mech[4:]
        if '/' not in cidr:
            cidr += '/128'
        if isinstance(client_ip_obj, ipaddress.IPv6Address):
            if client_ip_obj in ipaddress.ip_network(cidr, strict=False):
                return result_map[prefix]

    # all
    elif mech == 'all':
        return result_map[prefix]

    # a
    elif mech.startswith('a'):
        target = domain
        cidr_suffix = '/32'
        m = re.match(r'a(?::([^/]+))?(?:/(\d+))?', mech)
        if m:
            if m.group(1):
                target = m.group(1)
            if m.group(2):
                cidr_suffix = '/' + m.group(2)
        for ip in resolve_a(target, dns_count):
            try:
                if client_ip_obj in ipaddress.ip_network(ip + cidr_suffix, strict=False):
                    return result_map[prefix]
            except ValueError:
                pass

    # mx
    elif mech.startswith('mx'):
        target = domain
        cidr_suffix = '/32'
        m = re.match(r'mx(?::([^/]+))?(?:/(\d+))?', mech)
        if m:
            if m.group(1):
                target = m.group(1)
            if m.group(2):
                cidr_suffix = '/' + m.group(2)
        for ip in resolve_mx(target, dns_count):
            try:
                if client_ip_obj in ipaddress.ip_network(ip + cidr_suffix, strict=False):
                    return result_map[prefix]
            except ValueError:
                pass

    # include
    elif mech.startswith('include:'):
        target = mech[8:]
        included_record = get_spf_record(target, dns_count)
        if included_record:
            return check_host_internal(target, sender, client_ip, dns_count, included_record)
        return None  # include 目标无 SPF 记录 → 不匹配

    # exists
    elif mech.startswith('exists:'):
        hostname = mech[7:]
        if resolve_a(hostname, dns_count):
            return result_map[prefix]

    # ptr (故意省略 — 不推荐使用)
    elif mech.startswith('ptr'):
        pass  # RFC 7208 Section 5.5: SHOULD NOT be used

    return None  # 不匹配

def check_host_internal(
    domain: str,
    sender: str,
    client_ip: str,
    dns_count: list,
    spf_record: str
) -> str:
    """内部递归评估 SPF 记录的所有机制"""
    # 解析机制列表
    mechanisms = spf_record.split()
    mechanisms = [m for m in mechanisms if not m.startswith('v=')]

    for mech in mechanisms:
        if dns_count[0] > DNS_QUERY_LIMIT:
            return 'permerror'

        # redirect= 修饰符
        if mech.startswith('redirect='):
            target = mech[9:]
            redirected_record = get_spf_record(target, dns_count)
            if redirected_record:
                return check_host_internal(target, sender, client_ip, dns_count, redirected_record)
            return 'permerror'

        result = evaluate_mechanism(mech, domain, sender, client_ip, dns_count)
        if result is not None:
            return result

    return 'neutral'

def check_host(sender: str, client_ip: str, helo: str = '') -> str:
    """
    check_host() 入口 — RFC 7208 Section 4
    返回: pass | fail | softfail | neutral | temperror | permerror | none
    """
    domain = sender.split('@')[1] if '@' in sender else sender
    dns_count = [0]

    spf_record = get_spf_record(domain, dns_count)
    if not spf_record:
        return 'none'

    return check_host_internal(domain, sender, client_ip, dns_count, spf_record)

if __name__ == '__main__':
    if len(sys.argv)
<
3:
        print(f"Usage: {sys.argv[0]}   [helo]")
        sys.exit(1)

    sender = sys.argv[1]
    client_ip = sys.argv[2]
    helo = sys.argv[3] if len(sys.argv) > 3 else ''

    result = check_host(sender, client_ip, helo)
    print(f"SPF check_host({sender!r}, {client_ip!r}) = {result}")
    sys.exit(0 if result == 'pass' else 1)
```

### 9.4 在线验证工具

除命令行工具外，操作前可以使用公开的在线 SPF 检查器（搜索 "SPF record validator" 或 "SPF check tool"），它们通常会自动展开
include
链、统计 DNS 查询次数、指出潜在的问题。对于初次部署 SPF 的域，建议先用在线工具做一次完整审计再上线。

## 结语

SPF 从 2003 年的实验性草案走到 2014 年的 RFC 7208 建议标准，已经从一项"锦上添花"的邮件认证技术变成了邮件生态的基础设施。它与 DKIM、DMARC 共同构成现代邮件认证的三支柱，三者缺一不可。SPF 保护的是 SMTP 会话的信封身份，DKIM 保护的是邮件正文和头域的完整性，DMARC 则是将两者对齐并赋予域管理员以策略执行权。

在实际运维中，SPF 的难点往往不在于理解八种机制的定义，而在于管理
include
链的复杂度、控制 DNS 查询不超 10 次限制、以及在
-all
和
~all
之间做正确的业务判断。建议用子域隔离模式组织不同发信功能、定期用自动化脚本审计 SPF 记录的 DNS 展开量、以及确保 DMARC 的
aspf
对齐模式与 SPF 的
MAIL FROM
域策略一致。

### 参考文献

1. RFC 7208 — Sender Policy Framework (SPF) for Authorizing Use of Domains in Email, Version 1 (IETF, April 2014). Section 1 Introduction, Section 2.3 MAIL FROM Identity, Section 3 SPF Records, Section 4 The check_host() Function, Section 4.6.4 DNS Lookup Limits, Section 5.1 The "all" Mechanism, Section 5.2 The "include" Mechanism, Section 5.3 The "a" Mechanism, Section 5.4 The "mx" Mechanism, Section 5.5 The "ptr" Mechanism, Section 5.6 The "ip4" and "ip6" Mechanisms, Section 5.7 The "exists" Mechanism, Section 6.1 The "redirect" Modifier, Section 7 Macros.
2. RFC 4408 — Sender Policy Framework (SPF) for Authorizing Use of Domains in E-Mail, Version 1 (IETF, April 2006). Experimental predecessor to RFC 7208.
3. RFC 7489 — Domain-based Message Authentication, Reporting, and Conformance (DMARC) (IETF, March 2015). Section 3.1.1 SPF-Authenticated Identifiers, Section 6.3 aspf Tag.
4. RFC 5321 — Simple Mail Transfer Protocol (IETF, October 2008). Section 4.1.1.2 MAIL Command, Section 4.4 Trace Information (Return-Path).
5. RFC 5322 — Internet Message Format (IETF, October 2008). Section 3.6.2 Originator Fields (From: header).
6. libspf2 — SPF implementation library (
   https://www.libspf2.org/
   ). Provides spfquery and spftest tools.
7. OpenDMARC — Open source DMARC milter (
   http://www.trusteddomain.org/opendmarc/
   ). SPF/DKIM/DMARC integration reference. ````

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/spf-guide.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
