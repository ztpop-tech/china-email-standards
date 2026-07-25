---
title: "SPF 宏机制详解 — RFC 7208 §7：macro 展开、变量替换与 DNS 查询优化"
source: "https://ztpop.net/kb/spf-macros-guide.html"
license: CC-BY 4.0
---

# SPF 宏机制详解 — RFC 7208 §7：macro 展开、变量替换与 DNS 查询优化

## 一、SPF 宏机制的定位

SPF 记录的常规配置——
`v=spf1 ip4:203.0.113.0/24 -all`
或
`include:_spf.example.com`
——覆盖了 90% 的部署场景。但某些复杂场景下，静态 SPF 记录显得力不从心：

* 发件 IP 地址分散在不同子网中，且子网编号与域名相关（如每台服务器使用对应子域的独立 IP 段）
* SMTP 客户端 IP 在返回路径中携带域名信息，自定义 SPF 记录需要根据发送方 IP 动态响应
* 大型托管服务商（MSP）的 SPF 记录需要模块化地引用子客户域的信息

RFC 7208 第 7 节为此设计了 SPF
**宏机制**
（macro expansion）。宏允许 SPF 记录中包含占位符，由接收方 MTA 在评估 SPF 时根据当前邮件上下文（发送域、SMTP 客户端 IP、HELO 主机名等）动态展开为具体值。这使得单条 SPF 记录可以覆盖成千上万个不同子域的发送场景。

昆仑邮件系统在大型企业多域托管场景中，可以利用 SPF 宏机制大幅减少 DNS TXT 记录数量和 include 链深度，避免触及 RFC 7208 第 4.6.4 节规定的 10 次 DNS 查询硬限制。

**前提声明：**

SPF 宏是进阶特性。90% 的域不需要宏。只有在 IP 段与子域存在结构化关系、或 DNS 查询次数逼近 10 次上限时，才有必要引入宏。滥用宏会降低 SPF 可读性并增加调试难度。

## 二、RFC 7208 §7 定义的 11 个宏字母

SPF 宏以
`%{字母}`
或
`%{字母数字}`
的形式出现在 SPF 记录的
`exists`
、
`exp`
和
`redirect`
修饰符的目标域中。核心宏字母如下：

二、RFC 7208 §7 定义的 11 个宏字母

| 宏字母 | 展开值 | 示例（假设 example.com 发往 receiver.org） |
| `s` | SMTP MAIL FROM 的邮箱地址（完整 sender） | `user@example.com` |
| `l` | MAIL FROM 的 local-part（@ 之前部分） | `user` |
| `o` | MAIL FROM 的 domain（@ 之后部分） | `example.com` |
| `d` | 当前 SPF 评估的域（与 o 可能不同——在 include 链中，d 始终是发件域） | `example.com` |
| `i` | SMTP 客户端 IP 地址 | `203.0.113.45` |
| `p` | 经过 PTR 验证的域名（RFC 7208 第 5.5 节，不推荐使用） | `mail.example.com` 或无值 |
| `v` | IP 版本字符串（"in-addr" 或 "ip6"） | `in-addr` （IPv4） |
| `h` | SMTP EHLO/HELO 中声明的域名 | `mx1.example.com` |
| `c` | SMTP 客户端 IP（格式化为可打印字符串） | `203.0.113.45` |
| `r` | 正在执行 SPF 评估的接收方域名 | `receiver.org` |
| `t` | 当前 UNIX 时间戳（十进制） | `1720000000` |

RFC 7208 第 7.1 节强调：
**s/l/o 来自 SMTP 信封的 MAIL FROM，而非 5322.From 头部**
。这与 SPF 的基本设计一致——SPF 验证的是信封，DKIM 才验证头部。当 MAIL FROM 为空（bounce 邮件）时，s、l、o 均展开为空字符串。

RFC 7208 第 7.2 节进一步指出，参与宏展开的 DNS 查询也计入 10 次 DNS 查询限制。特定宏字母（如 p 的 PTR 查询和 exists 机制的目标域）会触发额外的 DNS 查询，在宏嵌套时必须审慎计数。

## 三、四大转换器（Transformer）

宏字母后面可以缀接转换器（transformer），用数字参数或特殊字符控制输出格式。RFC 7208 第 7.3 节定义了以下四类转换器：

### 3.1 数字截断（Digit Truncation）

格式：
`%{字母数字}`
，其中数字是正整数。效果：从
**右侧**
截取指定数量的标签段（以点号分隔）。

```
%{d1}   → 域 "mail.example.com" 展开为 "com"
%{d2}   → 域 "mail.example.com" 展开为 "example.com"
%{d3}   → 域 "mail.example.com" 展开为 "mail.example.com"
%{d4}   → 域 "mail.example.com" 仍为 "mail.example.com"（不够不截断）
```

数字反转（负数或零）：数字
**负数**
表示从
**左侧**
截取。

```
%{d-1}  → "mail.example.com" → "mail"
%{d-2}  → "mail.example.com" → "mail.example"
```

这一特性在托管服务商场景中极其实用。假设托管商为每个客户分配子域
`customer123.mail-svc.com`
，配置
`exists:%{d-1}._spf.mail-svc.com`
即可为每个客户指定独立的 SPF 策略。

### 3.2 r —— 反向（Reverse）

格式：
`%{字母r}`
或
`%{字母数字r}`
。效果：将截断后的域名字段按点号
**反向拼接**
。

```
%{dr}   → "example.com" → "com.example"
%{d1r}  → "mail.example.com" → "com"
%{d2r}  → "mail.example.com" → "com.example"
%{ir}   → "203.0.113.45" → "45.113.0.203"
```

反向转换的核心用例是匹配 DNS 反向区域格式。IPv4 地址反向后正好是
**in-addr.arpa**
的前半段。

### 3.3 u —— URL 转义（URL-escape）

格式：
`%{字母u}`
。效果：将展开值中的非 ASCII 字符和不安全字符（
`%`
、
`@`
、冒号等）进行百分号编码（percent-encoding），确保结果可以用作 URL 的 path 或 query 组件。

```
%{su} → "alice+tag@example.com" → "alice%2Btag%40example.com"
```

实际应用中，u 转换器主要用于
`exp=`
修饰符——需要构造包含 sender 地址的 HTTP(S) URL 来返回解释文本时。

### 3.4 分隔符（Delimiter）

RFC 7208 第 7.4 节允许为反向展开指定分隔符：
`%{字母数字r分隔符}`
。

```
%{ir.}    → "203.0.113.45" 反向并用点分隔 → "45.113.0.203"
%{ir-}    → "203.0.113.45" 反向并用短横线分隔 → "45-113-0-203"
```

默认分隔符是点（
`.`
）。通过指定不同分隔符，可以生成灵活的子域名模式。

## 四、实战模式：%{ir}.%{v}.spf.example.com

SPF 宏最经典的实战模式之一是利用客户端 IP 动态查询 DNS：

```
v=spf1 exists:%{ir}.%{v}.spf.example.com -all
```

展开过程（假设客户端 IP 为 203.0.113.45，IPv4）：

1. `%{ir}`
   →
   `45.113.0.203`
   （IP 反向）
2. `%{v}`
   →
   `in-addr`
   （IPv4）
3. 最终 DNS 查询：
   `45.113.0.203.in-addr.spf.example.com`
   的 A 记录

接收方 MTA 查询这个动态构造的域名：

* 如果存在 A 记录（任意 IP 均可）→ SPF Pass
* 如果返回 NXDOMAIN → SPF Fail（被
  `-all`
  最终终结）

这种模式的优势在于：不需要在 SPF 记录中列举所有 IP 地址（即不需要
`ip4:`
机制），而是通过 DNS 动态应答。当 IP 段发生变化时，只需更新 DNS 区域的 A 记录，SPF 记录本身不必修改。大型 ISP 和邮件服务商广泛使用此模式来管理动态 IP 池。

### 4.1 IPv6 版本

```
v=spf1 exists:%{ir}.%{v}.spf.example.com -all
```

同一行对 IPv6 同样生效：
`%{v}`
会自动展开为
`ip6`
，
`%{ir}`
会将 128 位地址逐 nibble 反向（用点分隔）。

例如客户端 IPv6 地址
`2001:db8::1`
，展开为：

```
1.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.8.b.d.0.1.0.0.2.ip6.spf.example.com
```

RFC 7208 第 7.3 节明确规定对 IPv6 地址的展开：将完整 32 个 nibble 全部写出，不做压缩。这导致展开后的域名极端冗长（> 80 字符），
**运维上可以通过 is 截断（如 %{i32r}）来限制长度**
。

### 4.2 使用截断控制 DNS 查询爆炸

大型运营商面临的关键问题是 DNS 查询次数。如果为每个客户端 IP 都发送一条 exists DNS 查询，查询量随 IP 池规模线性增长。通过引入
`i`
数字截断，可以将 IP 按子网聚合：

```
v=spf1 exists:%{i24r}.%{v}._spf.example.com -all
```

这里
`%{i24r}`
的作用：取 IP 的
**前 24 位标签**
（即 IPv4 的 /24 子网的第一部分），然后反向。对于
`203.0.113.45`
，
`%{i24}`
先得到
`203.0.113`
（右截断 3 段），再反向得到
`113.0.203`
。

这样整个 /24 子网（256 个 IP）共享一条 DNS A 记录——将 DNS 查询量压缩到 1/256。实际部署中可以根据 IP 池结构和授权粒度调节截断位数。

## 五、常见陷阱

### 5.1 过度 DNS 查询

RFC 7208 第 4.6.4 节规定单次 SPF 评估的总 DNS 查询次数
**不超过 10 次**
。宏机制并不豁免这条限制——每一条由宏展开触发的
`exists:`
、
`include:`
、
`a:`
、
`mx:`
、
`ptr:`
查询都计入计数。

典型反模式：在
`include:`
链中嵌套宏展开，导致每层 include 触发新查询。

```
# 危险模式——每条 include 触发宏展开 + 目标域查询 = 2 次，多链迅速超标
v=spf1 include:%{d}._spf.provider.com include:%{d}._spf2.provider.com ~all
```

每个
`include:`
本身计为 1 次查询，加上宏展开可能触发的额外查询，6~7 条 include 就会触及 10 次上限。解决方法是使用
`exists:`
取代
`include:`
，或在 DNS 层面预先聚合。

### 5.2 宏展开不可逆导致的调试困境

SPF 宏在接收方 MTA 本地展开，且展开结果严重依赖当前 SMTP 会话的上下文（IP、HELO、MAIL FROM）。发送方管理员无法在本地环境中精确复现接收方的展开过程。

调试工具：

```
# spfquery 支持模拟宏展开
spfquery -ip 203.0.113.45 -sender user@example.com   -helo mx1.example.com -spf "v=spf1 exists:%{ir}._spf.example.com -all"
```

另一个实践建议：在所有宏化 SPF 记录的末尾添加注释（通过 TXT 记录中除 TXT 外单独留一条带注释的 TXT 记录），记录原始语意，方便人工审计。

### 5.3 邮件转发与 MAIL FROM 重写下的 l/o 失效

当邮件经过转发服务器且转发器使用 SRS（Sender Rewriting Scheme）重写 MAIL FROM 时，
`%{l}`
和
`%{o}`
的展开值变为转发器的域而非原始发件域。RFC 7208 第 7.2 节对此有明确记录——这正是 SPF 依赖信封的根本局限。

应对措施：优先使用
`%{d}`
（当前评估域）而非
`%{o}`
（MAIL FROM 域），因为
`d`
在 include 链中指向原始域。同时，在转发场景中 DKIM 才是真正的身份锚点——SPF 宏只是优化工具。

### 5.4 PTR 宏 p 的性能与安全风险

RFC 7208 第 5.5 节强烈建议
**不使用**
`ptr`
机制。同理，
`%{p}`
宏展开会触发 PTR 反向 DNS 查询，随后还可能触发对应的 A/AAAA 正向校验（Forward Confirmed Reverse DNS, FCrDNS）。双重查询的性能开销远高于 A 查询，且在 DNSSEC 缺失的环境下容易被投毒。

任何使用
`%{p}`
的 SPF 记录都应视为安全审核重点。

## 六、总结

SPF 宏机制是 SPF 协议中复杂度最高但功能最灵活的部分。RFC 7208 第 7 节为 11 个宏字母提供了精确的语义定义，而四大转换器（数字截断、反向、URL 转义、分隔符）使输出格式可以适配各类 DNS 区域设计。

运维层面的三个关键决策：

* **是否需要宏？**
  ——90% 的部署不需要。引入宏前确认静态 SPF 已无法满足需求。
* **截断位数如何选择？**
  ——基于 IP 池结构（/24、/32 或 /48 /64 for IPv6）确定最粗的聚合粒度，用最少 DNS 查询覆盖最多 IP。
* **采用 exists 还是 include？**
  ——
  `exists:`
  优先，它的 DNS 查询次数更可控，且不引入外部域的 SPF 策略。

对于运维超过 100 个域的大型组织，昆仑邮件系统的 SPF 宏策略可以将上千条静态记录合并为数十条动态宏记录，显著降低 DNS 运维成本。

**参考文献：**
  
[1] IETF RFC 7208 — Sender Policy Framework (SPF) for Authorizing Use of Domains in Email, Version 1, April 2014
  
[2] IETF RFC 7489 — Domain-based Message Authentication, Reporting, and Conformance (DMARC), March 2015
  
[3] IETF RFC 6376 — DomainKeys Identified Mail (DKIM) Signatures, September 2011
  
[4] IETF RFC 5321 — Simple Mail Transfer Protocol, October 2008
  
[5] NIST SP 800-177 Rev.1 — Trustworthy Email, February 2019
  
[6] GB/T 30282-2013 — 信息安全技术 反垃圾邮件产品技术要求和测试评价方法

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/spf-macros-guide.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
