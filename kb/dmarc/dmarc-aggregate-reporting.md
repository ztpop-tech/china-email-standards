---
title: "DMARC 聚合报告深度解读 — RFC 7489 §7：XML 结构、auth_results 解析与异常排查 · ztpop 邮件技术知识库"
source: "https://ztpop.net/kb/dmarc-aggregate-reporting.html"
mirror_date: 2026-07-25
license: CC-BY 4.0
---

# DMARC 聚合报告深度解读 — RFC 7489 §7：XML 结构、auth_results 解析与异常排查 · ztpop 邮件技术知识库

DMARC 聚合报告深度解读 — RFC 7489 §7：XML 结构、auth\_results 解析与异常排查

## 摘要

DMARC（RFC 7489, March 2015）的第 7 节定义了聚合反馈机制（rua, Aggregate Reporting URI），要求接收方 MTA 以每日一次的频率向发件域指定的 rua 地址发送 ZIP 压缩的 XML 格式反馈报告。这份报告是对发件域 SPF 和 DKIM 验证结果的完整映射——每一个
元素代表一个发送方 IP 在 24 小时内向本域发送的所有邮件的汇总统计数据。本文把 RFC 7489 第 7 节和附录 C（XML Schema）中的每个字段逐一拆解，重点关注
`policy_evaluated`
（策略评估结果）、
`auth_results`
（SPF 和 DKIM 的逐项认证详情）以及
`row`
中的
`policy_evaluated`
子结构，并结合 dmarcian、DMARC Analyzer 和 parsedmarc 三类工具的解析视角，给出常见异常信号（如 pct 分阶段部署导致的间歇性 reject、子域 sp= 策略覆盖错误、DKIM 对齐失败但 SPF 通过的单腿通过现象）的诊断与处置方法。

## 1. DMARC 聚合报告的整体 XML 结构

### 1.1 外层容器：feedback 与 report\_metadata

DMARC 聚合报告的 XML 根元素是
（命名空间通常省略或设为默认），其下包含
（报告元数据）、
（接收方看到的发件域 DMARC 记录内容）和
（记录数组，每条对应一个发送源 IP）。一个完整的报告文件骨架：

```
xml version="1.0" encoding="UTF-8"?

  
    google.com
    noreply-dmarc-support@google.com
    1234567890.example.com
    
      1752182400
      1752268799
    
  
  
    example.com
    r
    r

reject

reject
    100
  
  ...
  ...
```

### 1.2 report\_metadata 字段详解

：报告生成组织的名称。Google 使用
`google.com`
，Microsoft 使用
`contoso.com`
，Yahoo 使用
`yahoo.com`
。该字段为自由文本，无标准化验证——某些自建 MTA 可能填入任意字符串。当收到来自未知 org\_name 的异常报告时，交叉验证
字段（报告发送者的联系邮箱）。
中的
和
使用 Unix 时间戳（UTC 秒）。
用于去重和问题报告时的引用——RFC 7489 §7.2 要求 report\_id 在报告的 org\_name 范围内全局唯一。

## 2. policy\_published：接收方观察到的 DMARC 策略

元素记录了报告生成时，接收方 MTA 缓存的发件域 DMARC DNS 记录内容。它与发件域管理员在 DNS 中发布的 DMARC TXT 记录在大多数时间一致，但在记录变更期间可能出现时间差（DNS TTL + MTA 缓存刷新周期，通常在 24 小时内收敛）。

2. policy\_published：接收方观察到的 DMARC 策略

| 字段 | 含义 | 取值 |
| --- | --- | --- |
|  | 被评估的邮件域 | 如 example.com |
|  | DKIM 对齐模式 | `r` (relaxed) 或 `s` (strict) |
|  | SPF 对齐模式 | `r` (relaxed, 仅域匹配) 或 `s` (strict, 完全匹配) |
|  | 组织域策略 | `none` , `quarantine` , `reject` |
|  | 子域策略（可选） | 同 p，不设置则继承 p |
|  | 策略应用比例 | 1-100，仅在 p=quarantine 或 reject 时生效 |

字段是生产中最容易被误解的参数——它只影响 DMARC 的处置动作（quarantine 或 reject），不影响报告的生成（报告始终覆盖 100% 邮件）。例如
`p=quarantine; pct=25`
，接收方对通过的邮件正常投递，对未通过 DMARC 的邮件，随机抽取 25% 执行 quarantine，另外 75% 按 p=none 处理（即仅报告不处置）。RFC 7489 §6.6.4 强调 pct 用于渐进式部署——域管理员从 pct=1 开始观察报告，逐步提升至 100。

## 3. record 元素：单 IP 维度的统计数据

### 3.1 row 子元素：来源 IP、邮件量和 DKIM/SPF 对齐统计

```
    192.0.2.25
    847
    
      none
      pass
      fail
    
  
  
    example.com
  
  ...
```

：发送此批次邮件的源 IP 地址。如果同一 IP 在 24 小时内向多个收件人发送了邮件，接收方会将它们归并为一条
，
字段记录总数。

中的
是此 IP 的邮件最终收到的 DMARC 处置结果（
`none`
/
`quarantine`
/
`reject`
），
和
表示 DKIM 和 SPF 的 DMARC 对齐结果（
`pass`
或
`fail`
），注意这不同于
`auth_results`
中的认证结果——这里是"对齐"结果（即签名域/信封域名是否与 Header From 域名一致），而非签名本身是否有效。

### 3.2 identifiers 与 header\_from

下的
是 DMARC 评估的核心标识符——RFC 7489 §3.1.1 规定 DMARC 验证基于 RFC 5322
`From:`
头域的域名（即用户在邮件客户端中看到的"发件人"域），而非 SMTP 信封的
`MAIL FROM`
域。这种设计是 DMARC 与 SPF 的根本区别之一：SPF 只验证信封域，DMARC 要求信封域（SPF 对齐）或签名域（DKIM 对齐）与 Header From 域匹配。如果
显示的值与发件域不一致（如报告发到 example.com 但 header\_from 显示 attacker.example.net），说明有第三方试图伪造 example.com 的 From 地址——这是 DMARC 设计的核心防御场景。

## 4. auth\_results：SPF 与 DKIM 的逐项认证详情

是报告中最具诊断价值的部分。它包含
和
两个子元素，记录接收方 MTA 对每封邮件执行的认证操作的完整结果链——不只是 DMARC 的"对齐"结论，而是认证自身的结果（pass/fail/neutral）、使用的域和签名选择器。

### 4.1 auth\_results/spf 元素

```
  mailchimp.com
  pass
```

是 SPF 检查中使用的域（SMTP MAIL FROM 或 HELO 域名），
是 SPF 检查的原始结果（
`pass`
,
`fail`
,
`softfail`
,
`neutral`
,
`none`
,
`temperror`
,
`permerror`
）。如果
的值是
`mailchimp.com`
而非
`example.com`
，但
`pass`
，表明 SPF 检查通过了但使用的是 relaxed 对齐模式（组织域匹配——
`example.com`
和
`mailchimp.com`
的组织域不同，这种情况下
`policy_evaluated/spf`
应该是
`fail`
）。

如果 auth\_results 中有多条
记录（极少数接收方会记录多次 SPF 尝试），应以最后一条的
为准（RFC 7208 §8.3 规定一个 SMTP 会话只有一个 SPF 结果）。

### 4.2 auth\_results/dkim 元素

```
  example.com
  pass
  202406
```

是 DKIM 签名中
`d=`
标签的域，
是签名中
`s=`
标签的选择器，
取值为
`pass`
,
`fail`
,
`neutral`
,
`none`
,
`temperror`
,
`permerror`
。一封邮件可以携带多个 DKIM 签名（如由转发服务追加），auth\_results 中会包含多条
记录——DMARC 评估时只要有任意一个签名的域和选择器通过即可，但要求该签名的
`d=`
域与 Header From 域对齐。

常见异常：
`fail`
但
`pass`
——这说明存在两个 DKIM 签名，其中一个失败但另一个通过了且对齐。反之，
`pass`
但
`fail`
，说明 DKIM 验证通过但签名域不与 Header From 域对齐（如第三方 ESP 用自己的域签名但未让客户域的 DMARC 对齐）。

## 5. 第三方解析工具与异常检测

### 5.1 dmarcian 与 DMARC Analyzer

dmarcian 和 DMARC Analyzer（现已被 Mimecast 收购）提供托管的 DMARC 报告聚合服务。域管理员将 rua 地址配置为服务商提供的专用邮箱（如
`rua@dmarc.dmarcian.com`
），服务自动解析 XML 报告并提供 Web 界面展示：(1) 发送源地图（按 IP 和发送量），(2) DMARC 合规率时间线，(3) 未授权发送源（Legitimate/Unknown/Fraudulent 分类），(4) DKIM/SPF 对齐失败明细。dmarcian 对 10 万封以下月流量的域免费。

### 5.2 parsedmarc（开源自部署）

parsedmarc 是 Python 编写的开源 DMARC 报告解析工具，支持从 IMAP 邮箱或本地目录读取 ZIP/XML 报告，输出为 JSON/CSV 或直接写入 Elasticsearch/Splunk。基础使用：

```
$ pip install parsedmarc
$ parsedmarc --imap-host imap.example.com \
             --imap-user dmarc@example.com \
             --imap-password password \
             --output-dir /tmp/dmarc-reports/ \
             --nameservers 8.8.8.8 1.1.1.1
```

parsedmarc 的反向 DNS 验证功能（
`--nameservers`
参数）会对报告中每个
执行 PTR 反向查询，帮助识别发送源（如"这是 SendGrid 的 IP 还是内部邮件服务器的 IP"）。对于使用邮件发送服务（SendGrid、Mailgun、AWS SES）的域，parsedmarc 可以帮助验证这些 ESP 是否正确配置了客户的 DKIM 和 SPF。

### 5.3 常见异常模式与对应措施

5.3 常见异常模式与对应措施

| 异常模式 | XML 信号 | 处置 |
| --- | --- | --- |
| 第三方 ESP 未对齐 | `dkim/result=pass` 但 `dkim/domain` 与 `header_from` 组织域不同 | 让 ESP 用客户域签名（CNAME DKIM selector 到 ESP 的公钥） |
| SPF 通过但 DMARC SPF 失败 | `spf/result=pass` 但 `policy_evaluated/spf=fail` | SPF 认证域非 Header From 域的对齐——检查 Return-Path 域 |
| pct 分阶段导致间歇性 reject | 同一 source\_ip 的 `disposition` 在 `reject` 和 `none` 之间波动 | 正常现象，pct=100 后消失 |
| 子域 sp= 策略覆盖错误 | 子域 header\_from 的 disposition 与组织域不一致 | 检查 `_dmarc.` TXT 记录是否存在错误的 sp= 标签 |
| 验证服务中断导致 temperror | `spf/result=temperror` 或 `dkim/result=temperror` | DNS 可用性问题或接收方 MTA 的临时故障——观察是否持续超过 24h |
| DKIM 密钥长度不足被拒 | `dkim/result=permerror` 伴随 `human_result` 包含 "key too short" | 将 DKIM 密钥从 1024 位升级到 2048 位，更新 DNS 记录 |

## 6. DMARC 部署中的报告治理

DMARC rua 报告是发件域了解自身邮件生态的"X 光片"。昆仑邮件系统为旗下托管域部署的 DMARC 治理管道包括：(1) 自动化的 rua 报告收集（Postfix 接收 → Dovecot sieve 脚本自动将 rua 邮件归档到专用文件夹 → parsedmarc cron 任务每 6 小时解析一次）；(2) Elasticsearch + Grafana 的可视化仪表板（DMARC 合规率趋势、未授权发送源告警、DKIM/SPF 对齐失败分布按发送源和接收方分组）；(3) 对合规率低于 99% 的域自动生成周报。GB/T 37002-2018 第 6.2.5 节要求邮件系统具备"邮件来源真实性验证"能力——DMARC 聚合报告是实现这一能力的持续验证和监控的基础设施，而非一次性配置。

### 参考文献

1. RFC 7489 — Domain-based Message Authentication, Reporting, and Conformance (DMARC) (IETF, March 2015). Section 7 DMARC Feedback, Section 7.2 Aggregate Reports (rua), Section 7.3 Failure Reports (ruf), Appendix C DMARC XML Schema.
2. RFC 7208 — Sender Policy Framework (SPF) for Authorizing Use of Domains in Email (IETF, April 2014). Section 2.3 MAIL FROM Identity, Section 4.6.4 DNS Lookup Limits, Section 8.3 SPF Results.
3. RFC 6376 — DomainKeys Identified Mail (DKIM) Signatures (IETF, September 2011). Section 3.5 The d= Tag (Signing Domain), Section 3.6 The s= Tag (Selector), Section 5 DKIM Verification.
4. dmarcian — DMARC Report Processing Service.
   <https://dmarcian.com/>
   — Source classification and compliance monitoring.
5. parsedmarc — Open Source DMARC Report Analyzer.
   <https://github.com/domainaware/parsedmarc>
6. GB/T 37002-2018 — 信息安全技术 电子邮件系统安全技术要求. 第 6.2.5 节 邮件来源真实性.
7. NIST SP 800-177 Rev.1 — Trustworthy Email (NIST, February 2019). Section 4 Email Authentication — DMARC deployment guidance.
8. RFC 5321 — Simple Mail Transfer Protocol (IETF, October 2008). 4.1.1.2 MAIL command (Return-Path / envelope-from).
9. RFC 5322 — Internet Message Format (IETF, October 2008). Section 3.6.2 Originator Fields (From: header).
10. DMARC.org — Deployment Guide.
    <https://dmarc.org/overview/>

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/dmarc-aggregate-reporting.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
