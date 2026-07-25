---
title: "DMARC 邮件认证策略框架深度解析 — RFC 7489：从 p=none 到 p=reject 的分阶段部署 · ztpop 邮件技术知识库"
source: "https://ztpop.net/kb/dmarc-guide.html"
mirror_date: 2026-07-25
license: CC-BY 4.0
---

# DMARC 邮件认证策略框架深度解析 — RFC 7489：从 p=none 到 p=reject 的分阶段部署 · ztpop 邮件技术知识库

DMARC 邮件认证策略框架深度解析 — RFC 7489：从 p=none 到 p=reject 的分阶段部署

## 1. 问题域：为什么 SPF + DKIM 还不够

SPF（Sender Policy Framework，RFC 7208）回答的问题是：「这个 IP 有没有被授权以该域的名义发信？」。DKIM（DomainKeys Identified Mail，RFC 6376）回答的是：「这封邮件的内容在传输过程中有没有被篡改，且签名域是否可信？」。但二者各自独立运作，彼此不知道对方的存在，也没有统一的判决逻辑——SPF 通过但 DKIM 失败时怎么办？反过来呢？

更关键的是，SPF 验证的是
`RFC5321.MailFrom`
（信封发件人），DKIM 验证的是签名中的
`d=`
域，而收件人在邮件客户端里看到的是
`RFC5322.From`
（信头 From）。这三个域可以完全不同。攻击者可以注册
`evil.example`
，配好 SPF + DKIM 全部通过，然后在信头 From 里写
`admin@bank.com`
。SPF 和 DKIM 对此毫无办法——因为它们的验证对象跟用户看到的 From 地址不是一回事。

这就是 DMARC 要解决的核心问题。RFC 7489 §1 明确指出：
*"SPF and DKIM provide domain-level authentication ... However, there has been no single widely accepted or publicly available mechanism to communication of domain-specific message-handling policies for receivers, or to request reporting of authentication and disposition of received mail."*
DMARC 在上述两套协议之上叠加了三层能力：

1. **Identifier Alignment（标识符对齐）**
   ：强制要求 SPF 或 DKIM 验证通过的域与信头 From 域之间存在匹配关系（RFC 7489 §3.1）。
2. **Policy Publication（策略发布）**
   ：域所有者通过 DNS TXT 记录宣告自己对未通过验证邮件的处理期望——监控、隔离还是拒绝。
3. **Feedback Loop（反馈回路）**
   ：接收方 MTA 向域所有者发送聚合报告（rua）和失败取证报告（ruf），使发送方能够发现配置漏洞和域名滥用。

> 参考规范：RFC 7489（DMARC）、RFC 7208（SPF）、RFC 6376（DKIM）、RFC 6591（AFRF 失败报告格式）、RFC 8460（TLS-RPT，SMTP TLS 报告，补充链路层可见性）。

## 2. DMARC 协议架构（RFC 7489 §3–§4）

RFC 7489 §4.3 给出了一张逻辑流程图，整个 DMARC 评估流程可以归纳为以下步骤：

1. 接收 MTA 从信头提取
   `RFC5322.From`
   的域名，称为
   **Author Domain**
   。
2. 向 DNS 查询
   `_dmarc.`
   的 TXT 记录，若不存在则 DMARC 不介入（RFC 7489 §6.6 第1步）。
3. 对邮件执行 SPF 验证和 DKIM 验证，各自得出 pass/fail 结论。
4. 对各自 pass 的结果执行
   **Identifier Alignment**
   检查（见第4节）。
5. 如果 SPF 通过且对齐，或 DKIM 通过且对齐，则 DMARC 整体结果 =
   **pass**
   ；否则 =
   **fail**
   。
6. 根据 DMARC 记录中的 p=/sp= 策略和 pct= 百分比决定处置动作。
7. 根据 rua= 和 ruf= 标签生成和发送报告。

注意步骤 3 和 4 的顺序：SPF/DKIM 各自的验证先独立执行，Alignment 是在验证结果之上的第二道检查。RFC 7489 §6.6 将接收方处理逻辑形式化为七步流程——从 DNS 查询、到 SPF/DKIM 评估、到 Identifier Alignment、到策略应用、再到报告生成。

## 3. DNS 记录语法：逐 Tag 拆解（RFC 7489 §6.3）

DMARC 策略以 DNS TXT 记录形式发布在
`_dmarc.`
上，格式遵循 DKIM 的 tag-value 语法。RFC 7489 §6.3 对每个 tag 做了完整定义。

### 3.1 查询命令

```
# 查询主域 DMARC 记录
dig TXT _dmarc.example.com +short

# 查询子域 DMARC 记录（若存在独立策略）
dig TXT _dmarc.sub.example.com +short

# 通过公共 DNS 解析器查询
dig @8.8.8.8 TXT _dmarc.example.com +short
```

### 3.2 Tag 全量表（RFC 7489 §6.3、§6.4）

3.2 Tag 全量表（RFC 7489 §6.3、§6.4）

| Tag | 必需 | 默认值 | 含义 | RFC 7489 |
| `v` | 是 | — | 协议版本，固定为 `DMARC1` ，必须是第一个 tag | §6.3 |
| `p` | 是 | — | 组织域策略： `none` / `quarantine` / `reject` | §6.3 |
| `sp` | 否 | 继承 `p` | 子域策略。子域可显式发布自己的 `_dmarc` 记录来覆写 | §6.3 |
| `pct` | 否 | `100` | 策略应用百分比（1–100），用于灰度上线 | §6.3 |
| `rua` | 否 | 无 | 聚合报告 URI 列表（逗号分隔），前缀 `mailto:` | §6.3、§7.2 |
| `ruf` | 否 | 无 | 取证失败报告 URI 列表，前缀 `mailto:` | §6.3、§7.3 |
| `fo` | 否 | `0` | 失败报告选项（详见 §7） | §6.3 |
| `adkim` | 否 | `r` | DKIM 对齐模式： `r` （Relaxed）/ `s` （Strict） | §6.3 |
| `aspf` | 否 | `r` | SPF 对齐模式： `r` （Relaxed）/ `s` （Strict） | §6.3 |
| `rf` | 否 | `afrf` | 失败报告格式： `afrf` （RFC 6591 定义）或 `iodef` | §6.3 |
| `ri` | 否 | `86400` | 聚合报告间隔（秒），请求接收方以不高于此频率发送报告 | §6.3 |

### 3.3 记录示例

```
# 监控模式（完全观察，不干预递送）
"v=DMARC1; p=none; rua=mailto:dmarc-rua@example.com; ruf=mailto:dmarc-ruf@example.com; fo=1; ri=86400"

# 隔离模式（1% 灰度）
"v=DMARC1; p=quarantine; pct=1; rua=mailto:dmarc-rua@example.com"

# 严格拒绝模式（全量）
"v=DMARC1; p=reject; sp=reject; pct=100; adkim=s; aspf=s; rua=mailto:dmarc-rua@example.com; fo=0"
```

## 4. Identifier Alignment：SPF Alignment 与 DKIM Alignment（RFC 7489 §3.1）

这是 DMARC 整个协议中最核心也最容易理解偏差的部分。RFC 7489 §3.1 详细定义了两种对齐模式及严格/宽松两种匹配方式。

### 4.1 对齐概念

DMARC 要求以下至少一项成立：

* **SPF Alignment（SPF 对齐）**
  ：SPF 验证通过的域（即 Authserv-ID 返回的
  `smtp.mailfrom`
  域或
  `helo`
  域）必须与
  `RFC5322.From`
  中的域匹配。
* **DKIM Alignment（DKIM 对齐）**
  ：DKIM 签名中
  `d=`
  参数指定的域必须与
  `RFC5322.From`
  中的域匹配。

### 4.2 Relaxed（宽松）模式 — aspf=r / adkim=r

两者有相同的
**Organizational Domain（组织域）**
即为对齐。所谓组织域，是指从完整域名中去掉最左边子域标签后得到的父域。例如
`mail.example.com`
和
`newsletters.example.com`
的组织域都是
`example.com`
（RFC 7489 §3.2）。

```
信头 From:   sender@news.example.com
SPF 通过域:  bounce.example.com    → aspf=r → 对齐 ✓（组织域相同）
DKIM d=:     mx.example.com        → adkim=r → 对齐 ✓
```

### 4.3 Strict（严格）模式 — aspf=s / adkim=s

必须是
**完全相同的 FQDN**
。

```
信头 From:   sender@mail.example.com
SPF 通过域:  mail.example.com      → aspf=s → 对齐 ✓
DKIM d=:     mail.example.com      → adkim=s → 对齐 ✓

信头 From:   sender@mail.example.com
SPF 通过域:  bounce.example.com    → aspf=s → 不对齐 ✗（FQDN 不同）
DKIM d=:     mail.example.com      → adkim=s → 对齐 ✓（恰好相同）
```

### 4.4 对齐逻辑表

4.4 对齐逻辑表

| aspf | SPF Auth Domain vs From Domain | 条件 |
| r（宽松） | 组织域相同即可 | example.com = example.com |
| s（严格） | FQDN 必须完全相同 | mx.example.com = mx.example.com |

4.4 对齐逻辑表

| adkim | DKIM d= vs From Domain | 条件 |
| r（宽松） | 组织域相同即可 | example.com = example.com |
| s（严格） | FQDN 必须完全相同 | dkim-sig.example.com = dkim-sig.example.com |

RFC 7489 §10.4 说明：选择严格模式前一定确认所有合法邮件来源的 FQDN 与 From 域完全一致。大多数生产环境先以 aspf=r / adkim=r 起步。

## 5. 策略三级：p=none / quarantine / reject

RFC 7489 §6.3 定义了三种策略级别，对应域名所有者对未通过 DMARC 验证的邮件采取的三级递进态度。

5. 策略三级：p=none / quarantine / reject

| 策略 | 语义 | 对邮件递送的影响 | 典型阶段 |
| `p=none` | 只监控，不做处置 | 邮件正常投递，不因 DMARC 失败而改变行为 | 部署初期（1–4 周） |
| `p=quarantine` | 将失败邮件标记为可疑 | 接收方 MTA 应将邮件放入垃圾箱/隔离区；具体行为由接收方策略定义 | 逐步收紧阶段 |
| `p=reject` | 拒绝 | 接收方应在 SMTP 会话中拒绝（SMTP 550），不进入用户邮箱 | 最终收敛状态 |

`p=none`
的价值在于能够在零风险的前提下收集聚合报告，观察有多少合法邮件会失败 DMARC。RFC 7489 §6.6 明确说明
`p=none`
时 DMARC 结果（pass/fail）不应影响邮件递送决策，但报告仍照常生成（如果 rua 或 ruf 已配置）。

从
`quarantine`
到
`reject`
的跳变是最关键的决策点——关键在于
`reject`
是在 SMTP 握手阶段直接拒收（RFC 7489 §10.3），收件人甚至看不到这封邮件。这意味着任何假阳性（合法邮件被误判 fail）将导致不可恢复的邮件丢失。正式启用
`p=reject`
之前，确保：

* 聚合报告连续 ≥2 周显示合法邮件 100% 通过；
* 所有第三方邮件代发服务（ESP、市场邮件、交易邮件）已纳入 SPF/DKIM 覆盖；
* 子域策略（sp=）已明确配置。

## 6. 百分比灰度（pct=）与子域策略（sp=）

### 6.1 pct= — 百分比灰度（RFC 7489 §6.3）

`pct=`
标签允许域名所有者指定一个 1 到 100 之间的整数，表示对未通过 DMARC 的邮件中多大比例执行 p= 策略。这不是「1% 的邮件用 DMARC 检查」，而是「
*全部邮件都检查，但只有 pct% 的失败邮件被执行策略*
」。

RFC 7489 §6.3 举例说明：如果
`p=reject; pct=25`
，接收方应对 25% 的失败邮件执行 reject，对其余 75% 的失败邮件采取次一级行为（如按 quarantine 或 none 处理）。

```
# p=quarantine 灰度：从 1% 开始，逐步上调
"v=DMARC1; p=quarantine; pct=1; rua=mailto:dmarc@example.com"
"v=DMARC1; p=quarantine; pct=10; rua=mailto:dmarc@example.com"
"v=DMARC1; p=quarantine; pct=50; rua=mailto:dmarc@example.com"
"v=DMARC1; p=quarantine; pct=100; rua=mailto:dmarc@example.com"

# p=reject 灰度
"v=DMARC1; p=reject; pct=1; rua=mailto:dmarc@example.com"
# ... 逐步上调至 pct=100
```

不要跳步。每个 pct 梯度至少停留 48 小时以上并检查聚合报告，确认无异常后再上调。

### 6.2 sp= — 子域策略（RFC 7489 §6.3）

主域（Organizational Domain）的 DMARC 记录中的
`sp=`
标签为所有直接子域（非自身已在
`_dmarc`
发布记录的子域）指定默认策略。如果子域在
`_dmarc..example.com`
发布了独立的 DMARC 记录，则该记录覆写主域的 sp=。

```
# 主域 _dmarc.example.com
"v=DMARC1; p=quarantine; sp=reject"

# 这表示：
# example.com 本身 → p=quarantine
# mail.example.com → sp=reject（如果未单独发布记录）
# app.example.com → sp=reject（同上）
# shop.example.com → 如果存在 _dmarc.shop.example.com，按该独立记录执行
```

一个常见故障点：忘记为非发送子域（如
`www`
、
`static`
）配置正确的 sp= 值，导致它们继承主域的 reject 策略后被人伪造利用时也无法检测（因为这些子域本身就不会发送邮件，如果允许伪造风险反而更不可控）。

## 7. 失败报告选项：fo= 标签全量解析（RFC 7489 §6.3）

`fo=`
控制什么情况下生成 Forensic Failure Report（ruf）。格式为冒号分隔的字符列表，值域如下：

7. 失败报告选项：fo= 标签全量解析（RFC 7489 §6.3）

| 值 | 含义 | RFC 7489 |
| `0` | 默认。仅当 *所有* 验证机制（SPF 和 DKIM）均未产生 pass 结果时生成报告 | §6.3 |
| `1` | 只要 *任一* 验证机制产生非 pass 结果就生成报告。触发条件比 0 宽松得多 | §6.3 |
| `d` | DKIM 签名验证失败时生成报告（无论 SPF 结果如何） | §6.3 |
| `s` | SPF 验证失败时生成报告（无论 DKIM 结果如何） | §6.3 |

这些值可以组合。例如
`fo=1:d:s`
表示三种条件任一触发即发送。对于初期部署，
`fo=1`
提供最详尽的失败数据，但报告量也最大——一个日均百万封的域，
`fo=1`
可能导致每天数万封 ruf 报告。RFC 7489 §7.3 特别提醒：ruf 报告包含原始邮件主题甚至部分正文，有隐私泄露风险，建议 ruf 地址使用域内邮箱并对报告内容做去敏化处理。

```
# 仅在 SPF 和 DKIM 双双失败时报告
"v=DMARC1; p=none; ruf=mailto:fail@example.com; fo=0"

# 任何失败都报告，包括单独 SPF 失败或单独 DKIM 失败
"v=DMARC1; p=none; ruf=mailto:fail@example.com; fo=1"

# 仅 DKIM 失败时报告
"v=DMARC1; p=none; ruf=mailto:fail@example.com; fo=d"
```

## 8. 聚合报告（rua）：XML Schema 逐字段拆解（RFC 7489 §7.2 / Appendix C）

聚合报告是 DMARC 最重要的运营数据源。它是一个 gzip 压缩的 XML 文件，通过 email 附件（
`application/zip`
）发送到 rua 指定的地址。RFC 7489 §7.2 定义了报告格式，Appendix C 给出了完整的 XML Schema。

### 8.1 报告 XML 顶层结构

```
xml version="1.0" encoding="UTF-8"?

  
    receiver.example.net
    dmarc-noreply@receiver.example.net
    https://receiver.example.net/dmarc
    2024.07.01.00
    
      1719705600
      1719792000
    
  
  
    example.com
    r
    r

reject

quarantine
    100
  
  
    
      192.0.2.1
      47
      
        none
        pass
        pass
      
    
    
      example.com
    
    
      
        example.com
        pass
      
      
        example.com
        pass
        default
```

### 8.2 关键字段逐一解释

8.2 关键字段逐一解释

| XML 路径 | 字段 | 说明 |
| `/feedback/report_metadata` | 报告元数据 | 报告机构名称、联系邮箱、报告 ID、统计周期起止时间（Unix 时间戳） |
| `/feedback/report_metadata/org_name` | 报告机构 | 生成该报告的邮件接收方组织名称 |
| `/feedback/report_metadata/date_range` | 统计窗口 | `begin` 和 `end` 定义该报告覆盖的时间段（UTC epoch 秒） |
| `/feedback/policy_published` | 发送方策略快照 | 接收方查询到的该域名在统计周期内的 DMARC 策略（含 p、sp、pct、adkim、aspf） |
| `/feedback/policy_published/domain` | 策略域名 | 被评估的域名 |
| `/feedback/record/row` | 聚合行 | 每条 record 对应一个 source\_ip + policy\_evaluated 组合 |
| `/feedback/record/row/source_ip` | 来源 IP | SMTP 连接的对端 IP 地址。v4 和 v6 均可 |
| `/feedback/record/row/count` | 邮件数量 | 该 IP 符合相同 policy\_evaluated 结果的邮件计数 |
| `/feedback/record/row/policy_evaluated/disposition` | 实际处置 | `none` / `quarantine` / `reject` ——接收方对该批次邮件的实际处理方式 |
| `/feedback/record/row/policy_evaluated/dkim` | DKIM 综合结果 | `pass` / `fail` ——本批邮件 DKIM 的对齐后 DMARC 评估结论 |
| `/feedback/record/row/policy_evaluated/spf` | SPF 综合结果 | `pass` / `fail` ——本批邮件 SPF 的对齐后 DMARC 评估结论 |
| `/feedback/record/identifiers/header_from` | 信头 From 域 | RFC5322.From 中提取的域名。对齐验证的核心参照物 |
| `/feedback/record/auth_results/spf/domain` | SPF 验证域 | SPF 验证中实际通过的域 |
| `/feedback/record/auth_results/spf/result` | SPF 原始结果 | SPF 的原始认证结果（ `pass` / `fail` / `softfail` / `neutral` / `none` / `temperror` / `permerror` ）——注意这是对齐前的原始 SPF 结论 |
| `/feedback/record/auth_results/dkim/domain` | DKIM 签名域 | DKIM 签名中 `d=` 的域 |
| `/feedback/record/auth_results/dkim/result` | DKIM 原始结果 | DKIM 的原始认证结果，对齐前的结论 |
| `/feedback/record/auth_results/dkim/selector` | DKIM Selector | 签名中使用的 selector |

### 8.3 读报告的常见分析套路

1. 筛出
   `dkim=fail AND spf=fail`
   的 record——这是双重失败，说明要么是伪造攻击，要么是完全没配认证的合法来源。
2. 筛出
   `dkim=pass BUT auth_results/dkim/domain ≠ header_from`
   的情况——DKIM 签了但签名域不对齐（可能是第三方代发用
   `d=esp.com`
   签了自己的域）。
3. 筛出
   `spf=pass BUT auth_results/spf/domain ≠ header_from`
   ——SPF 过了但不对齐（信封域和 From 域不匹配，常见于邮件列表转发）。
4. 按
   `source_ip`
   聚合 count，发现异常高频率的 IP —— 可能是自动化发信脚本或伪造源。
5. 对比
   `policy_evaluated/disposition`
   和
   `policy_published/p`
   ——如果发布的是
   `reject`
   但实际 disposition 是
   `none`
   ，说明接收方因
   `pct`
   或其他因素未完全执行。

## 9. 失败取证报告（ruf / AFRF — RFC 6591）

RFC 7489 §7.3 指定 ruf 报告的默认格式为 AFRF（Abuse Report Format），定义于 RFC 6591。与聚合报告不同，ruf 报告包含单封邮件的详细信息（subject、部分 header），因此在发送前必须做去敏化（redaction）：去掉 message body、限制可见 header 字段。

RFC 7489 §9.1 强调：ruf 报告可能暴露收件人的个人信息甚至邮件内容。因此建议：

* ruf 地址指向域内邮箱，不使用第三方分析服务；
* 接收方 MTA 在处理 ruf 报告时对敏感 header 做截断；
* 在大流量域上谨慎使用
  `fo=1`
  ，避免产生海量报告当机 ruf 收件箱。

AFRF 报告格式（RFC 6591 §3）是纯文本或 MIME multipart/report，包含三个部分：

* **Part 1**
  ：人类可读摘要；
* **Part 2**
  ：机器可读的
  `feedback-report`
  部分（ARF header fields）；
* **Part 3**
  ：原始邮件内容（或去敏化后的消息）

```
From: dmarc-feedback@receiver.example.net
Subject: DMARC Failure Report for example.com
Content-Type: multipart/report; report-type=feedback-report; boundary="==boundary=="

--==boundary==
Content-Type: text/plain

This is a DMARC forensic report for a message that failed authentication
checks on behalf of example.com.

--==boundary==
Content-Type: message/feedback-report

Feedback-Type: auth-failure
User-Agent: Receiver-MTA/1.0
Version: 1
Original-Mail-From: sender@example.com
Original-Rcpt-To: recipient@receiver.example.net
Arrival-Date: Tue, 02 Jul 2024 14:30:00 +0000
Source-IP: 203.0.113.42
Reported-Domain: example.com
Authentication-Results: receiver.example.net;
  dkim=fail header.d=example.com;
  spf=fail smtp.mailfrom=example.com;
  dmarc=fail (p=reject) header.from=example.com

--==boundary==
Content-Type: message/rfc822

[redacted original message headers]
--==boundary==--
```

## 10. 外部报告目标验证（RFC 7489 §7.1）

rua 和 ruf 的
`mailto:`
URI 可以指向外域地址（如
`mailto:reports@third-party.example`
），但 RFC 7489 §7.1 规定了接收方必须先验证该外域是否授权接收报告。验证机制：

1. 从 DMARC 记录中提取
   `rua`
   /
   `ruf`
   的目标域名（即
   `@`
   后面的部分）。
2. 构造查询主机名：
   `._report._dmarc.`
   ，其中 source-domain 是发布 DMARC 记录的域。
3. 查询该主机名的 TXT 记录，必须返回
   `"v=DMARC1"`
   字符串。
4. 若该 TXT 记录不存在，接收方应拒绝向该外域发送报告。

```
# 场景：example.com 的 DMARC 记录中 rua=mailto:agg@analyzer.example
# 接收方需要验证 analyzer.example 是否被授权接收 example.com 的报告

dig TXT example.com._report._dmarc.analyzer.example +short
# 应返回: "v=DMARC1"
```

这个机制防止攻击者把 DMARC 控件的 rua 指向受害者地址，然后大量发送伪造邮件触发洪水报告攻击（RFC 7489 §12.2）。

## 11. 常见失败模式与对策

### 11.1 邮件列表（Mailing List）转发

邮件列表服务器通常修改邮件正文（添加 footer、修改 subject 前缀），这会破坏 DKIM 签名。同时 SPF 源 IP 是列表服务器的 IP 而非原始发送域，所以 SPF 也失败。

**对策**
：ARC（Authenticated Received Chain，RFC 8617）可在转发链中保留原始认证结果。或者配置邮件列表软件做 DMARC 友好转发（即
*From-munging*
：将原始 From 地址替换为列表地址，原始发件人移入 Reply-To）。

### 11.2 自动转发（.forward / Sieve）

用户设置邮件自动转发到 Gmail 或其它邮箱时，转发服务器是新的 SMTP 源，SPF 必然失败。DKIM 签名如果邮件未被修改也可能保留，但如果中间 MTA 修改了 subject 或添加了 header，签名也会破。

**对策**
：关闭自动转发，改用邮件拉取（POP3/IMAP fetch）或配置 SRS（Sender Rewriting Scheme）重写信封地址，使 SPF 在第一跳接收方通过。

### 11.3 多跳中继

邮件经由多台 MTA 转发，每一跳都可能改变 header 或 envelope，导致 SPF 失效。DKIM 如果中间的 MTA 没有修改签名覆盖的 header 字段，签名可以存活——但如果修改了 subject 而未在 DKIM h= 列表中列明，签名即破。

**对策**
：审计所有中继路径，确保链路中所有 MTA 的行为已知。在 DKIM 签名中覆盖 subject 字段（
`h=from:subject:date:message-id:to`
）。

### 11.4 SPF 10-DNS-Lookup 限制

RFC 7208 §4.6.4 规定 SPF 验证在单次评估中最多执行 10 次 DNS 查询（包括
`include`
、
`a`
、
`mx`
等机制触发的查询）。超过则返回
`permerror`
，DMARC 视作 fail。大量
`include:`
指令聚合的域很容易撞墙。

**对策**
：使用 SPF 扁平化工具展开所有 include 为 IP 列表，或使用
`ip4`
/
`ip6`
机制直接声明 IP 段。

11.4 SPF 10-DNS-Lookup 限制

| 失败场景 | SPF | DKIM | 是否可通过 DMARC | 补救 |
| 直连发送、全链路配置正确 | pass + 对齐 | pass + 对齐 | ✅ Pass | — |
| 邮件列表转发 | fail | fail（body 被改） | ❌ Fail | From-munging 或 ARC |
| 用户 .forward 自动转发 | fail | 可能 pass（如果未修改 header） | ⚠️ 看 DKIM | SRS 或禁用转发 |
| 第三方 ESP 代发，未授权 | fail | fail（用 ESP 的 d= 签） | ❌ Fail | 在 SPF 中 include ESP 的发送域，并让 ESP 使用客户的 d= 签名 |
| SPF DNS 查询超 10 次 | permerror | pass | ✅ 仍可 Pass（单靠 DKIM 通过） | 扁平化 SPF 记录 |
| DKIM 签名在传输中被中间件剥离 | pass | none | ✅ 仍可 Pass（单靠 SPF 通过） | 排查中间件 |

## 12. OpenDMARC 部署与配置

OpenDMARC 是 Trusted Domain Project 维护的开源 DMARC milter，集成到 Sendmail 或 Postfix 中作为邮件处理链的一环。它依赖上游 DKIM 和 SPF 验证器在
`Authentication-Results`
header 中预填好结论。

### 12.1 安装

```
# Debian/Ubuntu
apt install opendmarc

# RHEL/CentOS（需 EPEL）
yum install epel-release
yum install opendmarc

# 源码编译（当前最新稳定版 1.4.x）
git clone https://github.com/trusteddomainproject/OpenDMARC.git
cd OpenDMARC
autoreconf -vif
./configure --sysconfdir=/etc --with-milter
make && make install
```

### 12.2 核心配置 /etc/opendmarc.conf

```
# 认证服务器 ID——必须和 opendkim 的 AuthservID 一致
AuthservID mail.example.com
# 拒绝失败邮件直接回绝（仅在 MTA 层面配置了 milter reject 时有效）
RejectFailures true
# 历史文件（聚合报告数据源）
HistoryFile /var/run/opendmarc/opendmarc.dat
# TrustedAuthservIds——信任哪些 Authentication-Results 来源
TrustedAuthservIDs mail.example.com
# 隔离邮件的处理方式——留给 MTA 决定
HoldQuarantinedMessages false
# 是否需要 SPF 对齐（默认 true）
SPFIgnoreResults false
# DKIM 对齐是否必须（默认 true）
DKIMIgnoreResults false
# 忽略不满足对齐的 Authentication-Results
IgnoreHosts /etc/opendmarc/ignore.hosts
# Socket 用于 Postfix milter 通信
Socket local:/var/run/opendmarc/opendmarc.sock
# 或使用 inet socket
# Socket inet:8893@localhost
# 运行用户
UserID opendmarc:opendmarc
# PID 文件
PidFile /var/run/opendmarc/opendmarc.pid
```

### 12.3 Postfix 集成

```
# /etc/postfix/main.cf
milter_default_action = accept
milter_protocol = 6
smtpd_milters = unix:/var/run/opendkim/opendkim.sock,
                unix:/var/run/opendmarc/opendmarc.sock
non_smtpd_milters = $smtpd_milters
```

重启 Opendmarc 和 Postfix 后，通过发送测试邮件并检查邮件头中的
`Authentication-Results`
来确认 DMARC 评估正在生效：

```
# 测试邮件发送后查看 header
grep -i "authentication-results" /var/log/mail.log

# 期望看到类似：
# Authentication-Results: mail.example.com;
#   dkim=pass header.d=example.com;
#   spf=pass smtp.mailfrom=example.com;
#   dmarc=pass (p=reject) header.from=example.com
```

### 12.4 历史文件与报告导出

OpenDMARC 将每封邮件的认证结果写入 HistoryFile（
`opendmarc.dat`
），之后可用
`opendmarc-importstats`
导入 MySQL/PostgreSQL，或用
`opendmarc-reports`
脚本生成并发送聚合报告：

```
# 手动导入历史到数据库
opendmarc-importstats --dbhost=localhost --dbname=opendmarc --dbuser=opendmarc --dbpasswd=**** < /var/run/opendmarc/opendmarc.dat

# 生成并发送聚合报告（放入 cron）
opendmarc-reports --dbhost=localhost --dbname=opendmarc --dbuser=opendmarc --dbpasswd=**** --verbose
# 建议 crontab: 0 3 * * * /usr/local/bin/opendmarc-reports ...
```

## 13. Python 解析 DMARC 聚合报告 XML

以下脚本逐字段解析压缩的 DMARC 聚合报告（.xml.gz），输出结构化 JSON 并按 disposition 做统计。

```
#!/usr/bin/env python3
"""
dmarc-parser.py — 解析 DMARC 聚合报告 XML（支持 .xml 和 .xml.gz）
RFC 7489 §7.2 / Appendix C
"""
import sys, json, gzip, os
from xml.etree import ElementTree as ET
from collections import defaultdict

NS = {"f": "urn:ietf:params:xml:ns:dmarc:1.0"}

def parse_report(path):
    """解析单个 DMARC 聚合报告文件"""
    if path.endswith(".gz"):
        with gzip.open(path, "rt", encoding="utf-8") as f:
            xml_content = f.read()
    else:
        with open(path, "r", encoding="utf-8") as f:
            xml_content = f.read()

    root = ET.fromstring(xml_content)

    # 报告元数据
    meta = root.find(".//f:report_metadata", NS)
    org = meta.findtext("f:org_name", default="", namespaces=NS)
    report_id = meta.findtext("f:report_id", default="", namespaces=NS)
    begin = int(meta.findtext(".//f:begin", default="0", namespaces=NS))
    end   = int(meta.findtext(".//f:end",   default="0", namespaces=NS))

    # 域名策略
    pp = root.find(".//f:policy_published", NS)
    domain = pp.findtext("f:domain", default="", namespaces=NS)
    policy = pp.findtext("f:p", default="", namespaces=NS)
    sp     = pp.findtext("f:sp", default="", namespaces=NS)
    pct    = pp.findtext("f:pct", default="100", namespaces=NS)

    print(f"报告: {report_id} | 机构: {org} | 域: {domain} | p={policy} sp={sp} pct={pct}")

    stats = defaultdict(lambda: {"count": 0, "ips": set()})

    for record in root.findall(".//f:record", NS):
        row = record.find("f:row", NS)
        source_ip = row.findtext("f:source_ip", default="?", namespaces=NS)
        count     = int(row.findtext("f:count", default="0", namespaces=NS))

        pe = row.find("f:policy_evaluated", NS)
        disposition = pe.findtext("f:disposition", default="?", namespaces=NS)
        dkim_result = pe.findtext("f:dkim", default="?", namespaces=NS)
        spf_result  = pe.findtext("f:spf",  default="?", namespaces=NS)

        ids = record.find("f:identifiers", NS)
        hfrom = ids.findtext("f:header_from", default="?", namespaces=NS)

        key = f"{dkim_result}|{spf_result}|{disposition}"
        stats[key]["count"] += count
        stats[key]["ips"].add(source_ip)

        # 详细信息（可选输出）
        auth = record.find("f:auth_results", NS)
        if auth is not None:
            spf_auth = auth.find("f:spf", NS)
            dkim_auth = auth.find("f:dkim", NS)
            auth_spf_domain = spf_auth.findtext("f:domain", default="", namespaces=NS) if spf_auth is not None else ""
            auth_spf_result = spf_auth.findtext("f:result", default="", namespaces=NS) if spf_auth is not None else ""
            auth_dkim_domain = dkim_auth.findtext("f:domain", default="", namespaces=NS) if dkim_auth is not None else ""
            auth_dkim_result = dkim_auth.findtext("f:result", default="", namespaces=NS) if dkim_auth is not None else ""

            # 不对齐检测
            if dkim_result == "pass" and auth_dkim_domain != hfrom:
                print(f"  ⚠ DKIM 对齐异常: d={auth_dkim_domain} ≠ From={hfrom} | IP={source_ip} x{count}")
            if spf_result == "pass" and auth_spf_domain != hfrom:
                print(f"  ⚠ SPF 对齐异常: auth={auth_spf_domain} ≠ From={hfrom}   | IP={source_ip} x{count}")

    # 汇总统计
    print("\n--- 统计汇总 ---")
    print(f"{'DKIM':<6} {'SPF':<6} {'处置':<12} {'邮件数':>10} {'独立IP':>8}")
    print("-" * 46)
    total = 0
    for key, val in sorted(stats.items(), key=lambda x: -x[1]["count"]):
        dkim, spf, disp = key.split("|")
        print(f"{dkim:<6} {spf:<6} {disp:<12} {val['count']:>10,} {len(val['ips']):>8}")
        total += val["count"]
    print(f"\n总计: {total:,} 封邮件, 统计周期: {begin} – {end}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"用法: {sys.argv[0]}  [...]")
        sys.exit(1)
    for arg in sys.argv[1:]:
        if os.path.exists(arg):
            parse_report(arg)
            print()
        else:
            print(f"文件不存在: {arg}", file=sys.stderr)
```

### 运行示例

```
# 解析单份报告
python3 dmarc-parser.py receiver.example.com!example.com!1720224000!1720310400.xml.gz

# 输出示例：
# 报告: 2024.07.01.00 | 机构: receiver.example.net | 域: example.com | p=reject sp=quarantine pct=100
#   ⚠ DKIM 对齐异常: d=esp.example ≠ From=example.com | IP=198.51.100.10 x3,421
# 
# --- 统计汇总 ---
# DKIM   SPF    处置          邮件数    独立IP
# ----------------------------------------------
# pass   pass   none         12,547        23
# fail   fail   reject        3,421         7
# pass   fail   none          1,240         5
# fail   pass   none            892         3
```

## 14. 分阶段部署路线图

DMARC 部署不是一次 DNS 修改就完了——它是一个持续数周乃至数月的渐进过程。以下是经过大量生产环境验证的标准路线：

14. 分阶段部署路线图

| 阶段 | 策略 | pct | 时长 | 操作 | 验证标准 |
| 1 | `p=none` | — | 1–3 周 | 发布 rua 记录，收集聚合报告 | 确认所有合法来源出现在报告中，且 dkim/spf pass |
| 2 | `p=none` | — | 1–2 周 | 修复阶段 1 发现的不对齐问题（ESP 签名、IP 白名单） | 合法邮件 100% 达到 dkim=pass 或 spf=pass 且对齐 |
| 3 | `p=quarantine` | 1 | 2–3 天 | 1% 隔离灰度 | 聚合报告中 disposition=quarantine 的邮件数和预期一致，且无用户投诉丢信 |
| 4 | `p=quarantine` | 10 | 2–3 天 | 上调至 10% | 同上 |
| 5 | `p=quarantine` | 50 | 3–4 天 | 上调至 50% | 同上，关注时间分布——所有时段的邮件表现应一致 |
| 6 | `p=quarantine` | 100 | ≥1 周 | 全量隔离 | 至少一周无异常后进入 reject 灰度 |
| 7 | `p=reject` | 1 | 2–3 天 | 1% reject 灰度 | 确认 disposition=reject 仅对应真正的伪造/未授权邮件 |
| 8 | `p=reject` | 10 | 2–3 天 | 10% reject | 同上 |
| 9 | `p=reject` | 50 | 3–4 天 | 50% reject | 同上 |
| 10 | `p=reject` | 100 | 持续 | 全量 reject，进入维护模式 | 定期审查 rua 报告；关注 SPF/DKIM 密钥轮换窗口 |

每个 pct 梯度之间不要跳步。尤其在 quarantine → reject 的过程中，即使不打算长期驻留在各中间梯度，也至少用 48 小时观察趋势。

## 15. 附录：dmarc.lhs 客户端验证脚本

以下 Literate Haskell 风格的客户端脚本（实际为 Python 实现）可用于发送一封测试邮件并验证全链路 DMARC 结果：

```
#!/usr/bin/env python3
"""
dmarc-lhs.py — DMARC 客户端全链路验证
发送测试邮件 → 检查 SPF → 检查 DKIM → 检查 DMARC → 输出诊断
"""
import smtplib
import dns.resolver
from email.mime.text import MIMEText
from email.utils import formatdate, make_msgid

def query_dmarc(domain):
    """查询 DMARC DNS 记录"""
    try:
        answers = dns.resolver.resolve(f"_dmarc.{domain}", "TXT")
        for rdata in answers:
            txt = "".join(s.decode() for s in rdata.strings)
            if txt.startswith("v=DMARC1"):
                return txt
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.exception.Timeout):
        pass
    return None

def query_spf(domain):
    """查询 SPF DNS 记录"""
    try:
        answers = dns.resolver.resolve(domain, "TXT")
        for rdata in answers:
            txt = "".join(s.decode() for s in rdata.strings)
            if "v=spf1" in txt:
                return txt
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
        pass
    return None

def parse_dmarc_tags(record):
    """将 DMARC 记录字符串拆分为 tag-value 字典"""
    if not record:
        return {}
    tags = {}
    # 按分号分割，跳过第一个 v= 之前的空白
    parts = [p.strip() for p in record.split(";") if p.strip()]
    for part in parts:
        if "=" in part:
            k, v = part.split("=", 1)
            tags[k.strip()] = v.strip()
    return tags

def send_test_email(smtp_host, smtp_port, from_addr, to_addr, subject, body):
    """发送测试邮件"""
    msg = MIMEText(body, "plain", "utf-8")
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg["Subject"] = subject
    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = make_msgid()

    with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.sendmail(from_addr, [to_addr], msg.as_string())
    print(f"✓ 测试邮件已发送: {from_addr} → {to_addr}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print(f"用法: {sys.argv[0]}  [--send smtp_host from to]")
        print(f"示例: {sys.argv[0]} example.com")
        print(f"       {sys.argv[0]} example.com --send smtp.example.com test@example.com you@gmail.com")
        sys.exit(1)

    domain = sys.argv[1]

    print(f"=== DMARC 诊断: {domain} ===")

    # SPF
    spf = query_spf(domain)
    if spf:
        print(f"✓ SPF:  {spf[:80]}...")
    else:
        print(f"✗ SPF:  未找到记录（RFC 7208）")

    # DMARC
    dmarc = query_dmarc(domain)
    if dmarc:
        print(f"✓ DMARC: {dmarc}")
        tags = parse_dmarc_tags(dmarc)
        print(f"\n  Tag 解析:")
        print(f"  p     = {tags.get('p', '未设置')}")
        print(f"  sp    = {tags.get('sp', '(继承 p)')}")
        print(f"  pct   = {tags.get('pct', '100')}")
        print(f"  aspf  = {tags.get('aspf', 'r')} ({'宽松' if tags.get('aspf','r')=='r' else '严格'})")
        print(f"  adkim = {tags.get('adkim', 'r')} ({'宽松' if tags.get('adkim','r')=='r' else '严格'})")
        print(f"  fo    = {tags.get('fo', '0')}")
        print(f"  rua   = {tags.get('rua', '未设置')}")
        print(f"  ruf   = {tags.get('ruf', '未设置')}")
        print(f"  ri    = {tags.get('ri', '86400')}s")

        # 策略评估
        p = tags.get("p", "未设置")
        if p == "none":
            print(f"\n  当前阶段: 监控（p=none）→ 仅收集数据，不影响递送")
        elif p == "quarantine":
            print(f"\n  当前阶段: 隔离（p=quarantine pct={tags.get('pct','100')}%）→ 失败邮件进垃圾箱")
        elif p == "reject":
            print(f"\n  当前阶段: 拒绝（p=reject pct={tags.get('pct','100')}%）→ 失败邮件在 SMTP 层拒绝（RFC 7489 §10.3）")
    else:
        print(f"✗ DMARC: 未找到 _dmarc.{domain} TXT 记录")
        print(f"  提示: 在 DNS 中添加: _dmarc.{domain} TXT \"v=DMARC1; p=none; rua=mailto:dmarc@{domain}\"")

    # 发送测试邮件
    if "--send" in sys.argv:
        idx = sys.argv.index("--send")
        if idx + 3 < len(sys.argv):
            smtp_host = sys.argv[idx + 1]
            from_addr = sys.argv[idx + 2]
            to_addr = sys.argv[idx + 3]
            send_test_email(
                smtp_host, 587, from_addr, to_addr,
                subject=f"DMARC Test: {domain}",
                body=f"这是一封 DMARC 测试邮件，由 dmarc-lhs 客户端发出。\n域: {domain}\n时间: {formatdate(localtime=True)}"
            )
            print(f"\n提示: 在收件端检查 Authentication-Results header 以确认 DMARC 结果。")
```

### 依赖安装

```
pip3 install dnspython
```

### 使用示例

```
# 仅诊断 DNS 配置
python3 dmarc-lhs.py example.com

# 诊断并发送测试邮件
python3 dmarc-lhs.py example.com --send smtp.example.com test@example.com recipient@gmail.com
```

## 参考规范

参考规范

| RFC | 标题 | 引用章节 |
| RFC 7489 | Domain-based Message Authentication, Reporting, and Conformance (DMARC) | §1、§3.1、§3.2、§4.3、§6.3、§6.4、§6.6、§7.1、§7.2、§7.3、§9.1、§10.3、§10.4、§12.2、Appendix C |
| RFC 7208 | Sender Policy Framework (SPF) Version 1 | §4.6.4（DNS 查询限制） |
| RFC 6376 | DomainKeys Identified Mail (DKIM) Signatures | §3.5（d= 标签定义）、§3.6（签名验证） |
| RFC 6591 | Authentication Failure Reporting Using the Abuse Report Format (AFRF) | §3（AFRF 报告格式）、§4（feedback-type） |
| RFC 8460 | SMTP TLS Reporting (TLS-RPT) | 补充传输层安全性可见性 |
| RFC 8617 | Authenticated Received Chain (ARC) Protocol | 转发场景下的认证链保留 |

最后更新：2024-07-04 · 本指南基于 RFC 7489、RFC 7208、RFC 6376、RFC 6591、RFC 8460 编写，不涉及任何商业产品品牌。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/dmarc-guide.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
