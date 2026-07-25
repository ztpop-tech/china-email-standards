---
title: "摘要：单一反垃圾技术（如关键字过滤或IP黑名单）无法应对现代垃圾邮件的多元化攻击手段。生产级邮件系统的反垃圾防护应采用分层架构（Layered Defense），将不同维度的检测技术部署在SMTP会话的不同阶段——连接建立时、MAIL FROM提交时、RCPT TO指定时、DATA传输时、邮件入队后——每一层独立决策、层层过滤，使垃圾邮件穿透整个防护链的概率趋近于零。本文以九层防护模型为框架，逐层解析每层的技术原理、开源实现和配置方案，基于M3AAWG最佳实践和RFC 6647灰名单标准。"
source: "https://ztpop.net/kb/anti-spam-layered-defense.html"
mirror_date: 2026-07-25
license: CC-BY 4.0
---

# 摘要：单一反垃圾技术（如关键字过滤或IP黑名单）无法应对现代垃圾邮件的多元化攻击手段。生产级邮件系统的反垃圾防护应采用分层架构（Layered Defense），将不同维度的检测技术部署在SMTP会话的不同阶段——连接建立时、MAIL FROM提交时、RCPT TO指定时、DATA传输时、邮件入队后——每一层独立决策、层层过滤，使垃圾邮件穿透整个防护链的概率趋近于零。本文以九层防护模型为框架，逐层解析每层的技术原理、开源实现和配置方案，基于M3AAWG最佳实践和RFC 6647灰名单标准。

## 1. 架构总览

分层反垃圾的核心设计原则是
**代价不对称**
：让垃圾邮件发送者在最早的SMTP会话阶段就消耗最大资源、在最低代价的检测层就被拒绝，而正常邮件几乎不受影响。按处理阶段从早到晚排列：

1. 架构总览

| 层级 | SMTP阶段 | 检测方法 | 命中后动作 |
| L1 — 网络层控制 | 连接建立前（TCP SYN） | IP信誉、连接速率限制、并发数限制 | 拒绝TCP连接 |
| L2 — 协议合规检查 | EHLO/HELO后 | HELO语法验证、PTR反向DNS一致性 | 554拒绝并断开 |
| L3 — 黑名单查询 | MAIL FROM后 | DNSBL/RBL实时查询 | 550/554拒绝 |
| L4 — 灰名单 | RCPT TO后 | 三元组（IP+发件人+收件人）首次临时拒收 | 451临时拒收 |
| L5 — SPF/DKIM验证 | MAIL FROM + DATA后 | 发件域认证 | 550/554拒绝或加分标记 |
| L6 — 内容过滤 | DATA接收后 | Bayesian分类、关键字规则、URL黑名单 | 标记Spam头或隔离 |
| L7 — 发件人信誉 | 邮件入队后 | 持久化发件人评分、行为模式分析 | 动态调整后续评分 |
| L8 — 云端协同 | 邮件入队后 | 云端指纹库比对、实时威胁情报 | 事后撤回或隔离 |
| L9 — 用户反馈 | 投递后 | 用户标记垃圾/非垃圾、反馈环路(FBL) | 训练Bayesian、更新规则 |

## 2. L1 — 网络层控制

网络层是最早、代价最低的防御层。在TCP三次握手完成前即可决策是否接受连接，拒绝一个连接消耗的资源几乎为零。Postfix通过
`postscreen`
守护进程实现这一层的能力：

```
# /etc/postfix/main.cf — postscreen 配置
postscreen_access_list = permit_mynetworks, cidr:/etc/postfix/postscreen_access.cidr
postscreen_dnsbl_sites = zen.spamhaus.org*2, bl.spamcop.net*1, b.barracudacentral.org*1
postscreen_dnsbl_threshold = 3
postscreen_greet_action = enforce
postscreen_dnsbl_action = enforce
postscreen_blacklist_action = drop
postscreen_cache_retention_time = 7d
postscreen_cache_cleanup_interval = 12h
```

`postscreen_dnsbl_threshold = 3`
的含义：一个连接的IP在三家DNSBL中的加权分数之和达到3分即拒绝。上述配置中Spamhaus ZEN权重为2（最权威），SpamCop和Barracuda权重各为1。如果IP被Spamhaus列入黑名单，仅Spamhaus一家即可达到2分（不满足阈值3），仍需另一家黑名单确认（1分）。这种配置避免单家DNSBL的误判导致正常邮件丢失。

## 3. L2 — 协议合规检查

大量垃圾邮件发送软件不遵循RFC 5321的协议规范。通过严格检查SMTP会话的协议合规性，可以在极低计算开销下过滤掉20%-30%的垃圾邮件：

```
# Postfix 协议合规检查
smtpd_helo_required = yes
smtpd_helo_restrictions = reject_invalid_helo_hostname, reject_non_fqdn_helo_hostname
smtpd_sender_restrictions = reject_non_fqdn_sender, reject_unknown_sender_domain
smtpd_recipient_restrictions = reject_non_fqdn_recipient, reject_unknown_recipient_domain
```

`reject_invalid_helo_hostname`
检查HELO参数是否为有效的hostname语法（不允许IP地址字面量、不允许纯数字或非法字符）。RFC 5321 §4.1.1.1规定HELO参数必须是一个完全限定域名（FQDN）或地址字面量——发送纯数字或单字的HELO明显违反协议规范。

## 4. L3 — DNSBL黑名单查询

DNSBL（DNS-based Blackhole List）是反垃圾邮件中最成熟、最广泛使用的技术之一。原理是将已知垃圾邮件来源的IP地址编码为DNS A记录，邮件服务器在收到SMTP连接时通过DNS查询判断发件IP是否在黑名单中。

Spamhaus ZEN（
`zen.spamhaus.org`
）是综合了SBL（已知垃圾源）、XBL（漏洞利用主机）、CSS（僵尸网络）和PBL（策略阻止列表，包含不应发邮件的动态IP段）的统一黑名单。SpamCop（
`bl.spamcop.net`
）基于用户提交的垃圾邮件报告自动生成。Barracuda（
`b.barracudacentral.org`
）由Barracuda Networks维护。国内反垃圾邮件联盟提供CBL（
`cbl.anti-spam.org.cn`
）和CDL（
`cdl.anti-spam.org.cn`
）。

查询性能优化：DNSBL查询是反垃圾链路中延迟最大的环节（每次查询需要1-50ms），在高峰期对数千个连接逐一查询会增加显著的SMTP响应延迟。Postfix通过
`postscreen_cache`
将查询结果缓存7天，避免了重复查询。

```
# 手动测试DNSBL查询
$ dig +short 2.0.0.127.zen.spamhaus.org
127.0.0.2  # 命中：IP已被列入

# 查询未列入的IP返回NXDOMAIN（无结果）
$ dig +short 8.8.8.8.zen.spamhaus.org
# (无输出 = 未列入)
```

## 5. L4 — 灰名单 Greylisting

灰名单（Greylisting）基于一个极简的前提：合法的MTA在收到临时拒收（SMTP 451）后会按RFC 5321 §4.5.4的规定在合理时间内重试，而大多数垃圾邮件发送软件（尤其是一次性批量投递工具）不会重试。

灰名单记录三元组（发送IP + 信封发件人MAIL FROM + 信封收件人RCPT TO）的首次出现时间。当一个三元组首次出现时，返回451临时拒收；第二次出现且距离首次已超过配置的最小延迟时间时，放行。成功放行后的三元组加入白名单，后续邮件直接通过。RFC 6647（"Email Greylisting: An Applicability Statement for SMTP"）对灰名单的适用性进行了全面评估。

```
# Postgrey 配置（Postfix 灰名单策略守护进程）
# /etc/postfix/main.cf
smtpd_recipient_restrictions = ...
    check_policy_service inet:127.0.0.1:10023

# postgrey 启动参数
postgrey --inet=10023 --delay=300 --max-age=35 --auto-whitelist-clients=5
```

`--delay=300`
设置首次拒绝后要求的最短重试间隔为300秒（5分钟）。
`--max-age=35`
设置三元组白名单的保留天数为35天。
`--auto-whitelist-clients=5`
表示一个IP地址累计成功投递5次后，该IP的所有发信自动绕过灰名单——避免了高频正常发件人每次都经历延迟。

## 6. L5 — SPF/DKIM/DMARC认证

发件域认证是阻止域名伪造（Email Spoofing）的核心机制。SPF（RFC 7208）验证发件IP是否有权使用MAIL FROM域；DKIM（RFC 6376）通过数字签名验证邮件正文未被篡改；DMARC（RFC 9989，替代已废弃的RFC 7489）定义SPF和DKIM的对齐策略及失败处理方式。

详细配置见本站知识库的独立文章：
[SPF配置指南](/kb/spf-guide.html)
、
[DKIM配置指南](/kb/dkim-guide.html)
、
[DMARC配置指南](/kb/dmarc-guide.html)
。

## 7. L6 — 内容过滤

通过前五层的邮件在SMTP协议和IP信誉维度均已通过，但仍可能包含垃圾内容。L6内容过滤层通过分析邮件正文和附件内容做最终判断。主流方法包括：

**Bayesian分类器**
：SpamAssassin的Bayesian引擎基于统计模型计算邮件为垃圾的概率。训练数据来源于已知垃圾和正常邮件（ham）的语料库。每次用户将一封邮件标记为垃圾或非垃圾，Bayesian模型即更新对应的令牌（token）权重。

**规则引擎**
：SpamAssassin维护约1000条规则，每条规则匹配一个垃圾特征并赋予不同分值（如
`HTML_IMAGE_ONLY_24`
= 1.5分、
`RCVD_IN_PBL`
= 3.0分）。邮件总得分超过阈值（默认5.0）即判定为垃圾。SpamAssassin 4.0引入了基于机器学习的插件（
`TxRep`
），利用发件人信誉和邮件历史进行动态评分。

**URL黑名单**
：邮件正文中的URL通过SURBL（Spam URI Realtime Blocklists）和Spamhaus DBL验证，防止钓鱼链接和恶意软件下载地址穿透。

```
# SpamAssassin 核心配置片段
required_score 5.0
use_bayes 1
bayes_auto_learn 1
bayes_auto_learn_threshold_spam 12.0
bayes_auto_learn_threshold_nonspam 0.1
use_dcc 0
use_pyzor 0
use_razor2 0
skip_rbl_checks 0
dns_available yes

# Amavis 与 SpamAssassin 集成
# /etc/amavis/conf.d/50-user
$sa_tag_level_deflt  = undef;
$sa_tag2_level_deflt = 5.0;
$sa_kill_level_deflt = 10.0;
$final_spam_destiny   = D_DISCARD;
```

## 8. L7-L9 — 信誉系统、云端协同、用户反馈

L7信誉系统对发件人和发件IP进行持久化评分——一个IP一段时间内连续发出垃圾邮件，其信誉分持续降低，后续即使内容评分低于阈值，信誉加权后仍可能被拦截。L8云端协同将本地提取的垃圾邮件特征哈希发送到云端规则库做比对，获取最新的零日威胁情报。L9用户反馈闭环允许用户标记误判邮件（false positive/false negative），反馈数据回流到Bayesian训练集和规则优化中。

## 参考文献

1. RFC 6647, "Email Greylisting: An Applicability Statement for SMTP," IETF, 2012.
   <https://datatracker.ietf.org/doc/rfc6647/>
2. RFC 5321, "Simple Mail Transfer Protocol," §4.1.1.1 Extended HELLO (EHLO) or HELLO (HELO), §4.5.4 Retry Strategies, IETF, 2008.
3. RFC 7208, "Sender Policy Framework (SPF) for Authorizing Use of Domains in Email," IETF, 2014.
4. RFC 6376, "DomainKeys Identified Mail (DKIM) Signatures," IETF, 2011.
5. M3AAWG, "Best Practices for Managing Email Delivery and Anti-Abuse Operations," Version 4.0, 2023.
   [https://www.m3aawg.org/](https://www.m3aawg.org/published-documents)
6. SpamAssassin Project, "Apache SpamAssassin — Open Source Anti-Spam Platform," The Apache Software Foundation.
   <https://spamassassin.apache.org/>
7. Spamhaus Project, "The Spamhaus Block List (SBL), Exploits Block List (XBL), Policy Block List (PBL),"
   <https://www.spamhaus.org/>
8. . 引用日期：2026-07-11.

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/anti-spam-layered-defense.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
