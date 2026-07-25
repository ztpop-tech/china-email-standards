---
title: "DNS 黑名单机制与应对策略 — DNSBL/RBL/URIBL 原理、查询方法与自建方案 · ztpop 邮件技术知识库"
source: "https://ztpop.net/kb/dnsbl-blacklist-guide.html"
license: CC-BY 4.0
---

# DNS 黑名单机制与应对策略 — DNSBL/RBL/URIBL 原理、查询方法与自建方案 · ztpop 邮件技术知识库

DNS 黑名单机制与应对策略 — DNSBL/RBL/URIBL 原理、查询方法与自建方案

## 摘要

DNS 黑名单（DNSBL/DNS-based Blackhole List）是反垃圾邮件体系中最古老且依然有效的防御层。其核心原理是将已知垃圾邮件源的 IP 地址和域名映射到 DNS 查询系统中的特定区域（zone），MTA 在接收邮件时通过 DNS A 记录查询匹配被列入名单的 IP，返回 127.0.0.x 范围内的特定结果码表示不同的名单类别。RFC 5782（DNS Blacklists and Whitelists, February 2010）对 DNSBL 的查询协议、返回码语义和技术策略进行了正式标准化。本文从 DNSBL 的 DNS 查询机制底层出发，覆盖 Spamhaus（SBL/XBL/PBL/DBL）、Barracuda BRBL、SpamCop 三大主流黑白名单体系的操作细节，延伸至 URIBL（基于邮件正文 URL 域名的黑名单检测），并以 rbldnsd 为例给出自建 DNSBL 方案，帮助邮件管理员建立完整的黑名单防护与误判处理能力。

## 1. DNSBL 技术原理：DNS 查询即判定

### 1.1 DNSBL 查询机制（RFC 5782 §2）

DNSBL 的查询不依赖任何新协议——它直接复用了标准 DNS A 记录查询（RFC 1035）。当 MTA 接收到来自 IP 地址 192.0.2.25 的连接时，它将 IP 反序拼接后附加到 DNSBL 区域后缀，发起一次 DNS 查询：

```
25.2.0.192.zen.spamhaus.org  →  DNS A 查询
```

如果该 IP 在黑名单中，DNS 服务器返回 127.0.0.x 范围内的一个或多个 A 记录——每个返回码对应不同的名单类别。如果 IP 不在名单中，服务器返回 NXDOMAIN（不存在的域名）。RFC 5782 第 2.2 节明确：DNSBL 必须返回 127.0.0.0/8 范围内的 IPv4 地址作为正向命中信号，以确保不会与正常的互联网路由混淆。第 2.3 节进一步规定，DNSBL 操作者必须提供 TXT 记录（RFC 5782 §2.4）来解释被列入的原因，MTA 可以在 SMTP 拒绝消息中引用该 TXT 记录向发件人提供申诉指引。

### 1.2 返回码语义与多区域组合

以 Spamhaus ZEN 为例，其融合了三个子区域，每个子区域返回不同的命中码：

1.2 返回码语义与多区域组合

| 命中 IP | 子区域 | 含义 |
| --- | --- | --- |
| 127.0.0.2 | SBL（Spamhaus Block List） | 已确认的垃圾邮件源，包括已知的垃圾邮件发送者、恶意软件分发者和钓鱼托管 |
| 127.0.0.3 | CSS（Composite Snowshoe） | 雪鞋式垃圾邮件（通过大量 IP 分散发送量以规避速率限制） |
| 127.0.0.4-7 | XBL（Exploits Block List） | 被利用的服务器——开放的 HTTP/SOCKS 代理、被感染的僵尸网络节点 |
| 127.0.0.10-11 | PBL（Policy Block List） | 不应直接发送邮件的 IP 范围——如动态 IP 池、家庭宽带、移动网络 |

昆仑邮件系统内置的 TurboGate 反垃圾引擎对每个入站连接同时查询 8 个 DNSBL 区域，DNS 查询总耗时控制在 120ms 以内（通过本地 DNS 缓存和并发查询）。多个 DNSBL 的查询结果通过加权评分模型综合判定：SBL 命中 +4 分，XBL 命中 +3 分，PBL 命中 +1 分，总分超过阈值（默认 4 分）则拒绝连接。

## 2. 主流 DNSBL 体系对比

### 2.1 Spamhaus 体系（SBL, XBL, PBL, DBL, ZEN）

Spamhaus Project 运营着全球最大的 DNSBL 基础设施，每日处理超过 300 亿次 DNS 查询。其数据维护团队通过全球 30 个以上的蜜罐节点（honeypot）和 spam trap 地址持续收集垃圾邮件数据。ZEN 是 SBL + XBL + PBL 的联合区域（单次查询即可覆盖三个列表），是生产环境中最常用的配置：

```
# Postfix 配置示例
smtpd_recipient_restrictions =
    reject_rbl_client zen.spamhaus.org,
    reject_rbl_client bl.spamcop.net,
    reject_rbl_client b.barracudacentral.org,
    permit_mynetworks,
    permit_sasl_authenticated,
    reject_unauth_destination
```

Spamhaus DBL（Domain Block List）是独立的域名级黑名单，查询方式为正向域名查询（不做 IP 反序），用于检测垃圾邮件中的恶意域名：

```
malware-drop.example.com.dbl.spamhaus.org  →  DNS A 查询
# 命中返回 127.0.1.x
```

### 2.2 Barracuda BRBL（Barracuda Reputation Block List）

Barracuda 的 BRBL（b.barracudacentral.org）基于其全球部署的 400,000+ Barracuda Email Security Gateway 设备的遥测数据，实时更新间隔为 15 分钟。BRBL 的特点是对新型垃圾邮件活动反应速度极快（平均收录延迟在 5 分钟以内），但误报率（约 0.03%）略高于 Spamhaus（约 0.01%）。BRBL 返回 127.0.0.2 表示命中，支持按 /24 子网级别封禁。

解封流程：访问
[BarracudaCentral IP Reputation Lookup](https://www.barracudacentral.org/lookups/ip-reputation)
，输入被列入的 IP，页面会显示列入原因（如"poor reputation"、"spam trap hits"）。如果 IP 已被清理，系统通常会在 24 小时内自动移出。

### 2.3 SpamCop（bl.spamcop.net）

SpamCop 使用用户提交的垃圾邮件报告作为数据源，通过自动分析提取垃圾邮件来源 IP，并基于报告数量和时效性动态计算分数。SpamCop 的名单是"快进快出"型的——一个 IP 在收到最后一封垃圾邮件报告后的 24 小时内自动过期，除非持续有新的报告。这种机制适合作为辅助 DNSBL（单靠 SpamCop 不应直接拒绝邮件），因为短时间的高误报风险较小但覆盖不完整。

## 3. URIBL：基于邮件正文链接的域名黑名单

URIBL（URI Blacklist）不检测发送方 IP，而是提取邮件正文中所有超链接（
）的域名部分，查询独立于 DNSBL 的域名黑名单区域。URIBL 的典型查询格式：

```
example.com.multi.uribl.com  →  DNS A 查询
```

SURBL（Spam URI Realtime Blocklists, surbl.org）是最广泛部署的 URIBL，包含以下子列表：

3. URIBL：基于邮件正文链接的域名黑名单

| 子列表 | 区域后缀 | 内容 |
| --- | --- | --- |
| ABUSE（滥用） | abuse.surbl.org | 钓鱼和欺诈网站 |
| MW（恶意软件） | mw.surbl.org | 恶意软件分发域名 |
| PH（钓鱼） | ph.surbl.org | 已知钓鱼域名 |
| MULTI | multi.surbl.org | ABUSE + MW + PH + CRACKED + 其他 = 联合查询 |

URIBL 的误报控制比 IP DNSBL 更精细——它查询的是域名而非 IP，一个域名可以被精确地列入而不影响同一 IP 上的其他域名（这对共享主机环境极为重要）。Postfix 不自带 URIBL 查询功能，需要借助 SpamAssassin（
`URIDNSBL`
插件）或 Amavis（
`@uribl_lookup_sites`
配置项）实现。SpamAssassin 配置：

```
loadplugin Mail::SpamAssassin::Plugin::URIDNSBL
uridnsbl URIBL_MULTI multi.uribl.com. A 2
body URIBL_MULTI eval:check_uridnsbl('URIBL_MULTI')
describe URIBL_MULTI Contains a URL listed by URIBL
score URIBL_MULTI 2.5
```

## 4. 解封流程与白名单申请

### 4.1 Spamhaus 解封标准流程

被列入 Spamhaus SBL 是邮件投递事故中最严重的情况之一——SBL 被全球超过 30 亿个邮箱使用。解封条件严格：(1) 确认垃圾邮件问题已根除（服务器不再发送未经请求的批量邮件，开放中继已关闭，被入侵的账户已隔离）；(2) 通过
[Spamhaus IP Lookup](https://www.spamhaus.org/lookup/)
工具查看具体被列入的列表和原因代码；(3) 在 SBL 移除页面提交移除请求，描述已采取的措施。Spamhaus 的处理时间通常为 4-48 小时，不接受电话或邮件催促。

PBL 的解封流程不同：PBL 记录了 ISP 提供的动态/非邮件服务器 IP 范围。如果某 IP 确实是合法的邮件服务器 IP（如小型企业的静态 IP），可以通过 Spamhaus PBL 移除请求页面申请移除——前提是 ISP 未在 WHOIS 或 SWIP 记录中将该 IP 标记为动态分配。

### 4.2 DNSWL 白名单（dnswl.org）

DNSWL.org 是最大的 DNS 白名单服务，查询方式与 DNSBL 完全相同（反序 IP 查询），但返回 127.0.0.0/8 范围外的地址，用于补充信任评分。返回码编码信任等级：127.0.2.x = 高信任（从不发送垃圾邮件），127.0.10.x = 中等信任，127.0.20.x = 低信任。SpamAssassin 的
`RCVD_IN_DNSWL_HI`
规则会给予负分（提高邮件通过概率）。

申请白名单的流程：在
[DNSWL.org](https://www.dnswl.org/)
注册账户，提交邮件服务器的 IP 地址和出站邮件量信息（日均邮件量、是否使用双重确认 opt-in、退订机制等）。审核周期通常为 3-7 个工作日，批准后会在
`list.dnswl.org`
区域发布。

## 5. 自建 DNSBL 方案：rbldnsd

### 5.1 rbldnsd 架构

rbldnsd（RBL DNS Daemon）是一个专为 DNSBL 场景设计的高性能 DNS 服务器。与 BIND/Unbound 等通用 DNS 服务器不同，rbldnsd 的数据库直接以 IP 范围和数据集的格式加载，不使用传统 DNS 区域文件，内存占用极低（1 千万条记录约占用 400MB 内存）。

安装与基础配置（Debian/Ubuntu）：

```
# apt install rbldnsd
# mkdir -p /var/lib/rbldnsd
# cat > /etc/rbldnsd.conf << 'EOF'
RBLDNSD="rbldnsd -b 127.0.0.1/53 -p /var/run/rbldnsd.pid \
  -l /var/log/rbldnsd.log \
  -r /var/lib/rbldnsd \
  -t 60m \
  myrbl.example.com:ip4set:local-blacklist \
  myrbl.example.com:dnset:local-domain-blacklist"
EOF
```

IP 数据集文件格式（
`/var/lib/rbldnsd/local-blacklist`
）：

```
# 单 IP
192.0.2.25         Bad reputation from internal honeypots
# CIDR 子网
198.51.100.0/24    Known spam hosting AS
# 带 TTL（秒）
203.0.113.0/27     3600  Temporary block - spam wave observed
```

域名数据集文件格式（
`/var/lib/rbldnsd/local-domain-blacklist`
）：

```
spam-domain.example.com      Confirmed spam domain
malware-c2.example.net       C2 server domain
```

### 5.2 自动化数据源集成

自建 DNSBL 的数据来源可以包括：(1) 从公共 DNSBL 的 rsync 数据馈送（Spamhaus 为企业客户提供 DQS 数据馈送服务）；(2) 自有的 spam trap 邮箱自动收集；(3) Postfix 的
`reject_rbl_client`
拒绝日志中的重复攻击源。(3) 的实现方式：通过分析
`/var/log/mail.log`
中的拒绝事件，提取高频命中的 IP 写入本地黑名单，crontab 定时任务每 30 分钟更新一次：

```
#!/bin/bash
# 从 Postfix 日志中提取最近 24h 被 DNSBL 拒绝超过 5 次的 IP
awk '/reject.*zen.spamhaus.org/ {ips[$NF]++} END {
  for(ip in ips) if(ips[ip]>5) print ip
}' /var/log/mail.log | while read ip; do
  echo "$ip  Repeated spam source - auto-listed $(date +%Y-%m-%d)" \
    >> /var/lib/rbldnsd/local-blacklist
done
sort -u /var/lib/rbldnsd/local-blacklist -o /var/lib/rbldnsd/local-blacklist
systemctl reload rbldnsd
```

## 6. DNSBL 在生产中的误报管理与多层防御编排

DNSBL 并非零误报——误报率取决于列表类型和源数据的质量控制。PBL 类型列表（基于策略而非行为）误报率最高，因为 IP 所属的网络类别判定依赖于 ISP 数据的准确性和时效性。SBL 类型的误报率最低（Spamhaus 内部 API 有手动审核流程，每个 SBL 条目需要至少两名分析师确认）。建议的 DNSBL 防御层编排策略：

```
# Postfix smtpd_recipient_restrictions 中的多层防线
smtpd_recipient_restrictions =
    # 第 0 层：白名单优先（内部网络、已认证用户）
    permit_mynetworks,
    permit_sasl_authenticated,
    # 第 1 层：DNSBL 拒绝（高置信度列表，直接拒绝）
    reject_rbl_client zen.spamhaus.org,
    # 第 2 层：DNSBL 标记（中等置信度，仅加分不拒绝，留给 SpamAssassin 处理）
    # reject_rbl_client bl.spamcop.net,  ← 注释掉，改为 SpamAssassin 加权
    # 第 3 层：收件人地址验证
    reject_unverified_recipient,
    # 第 4 层：默认拒绝未被以上规则显式放行的外部投递
    reject_unauth_destination
```

这种编排确保只有 Spamhaus ZEN（误报率 < 0.01%）执行直接拒绝，SpamCop 和 Barracuda 仅通过 SpamAssassin 加权评分（分别加 2.0 和 1.5 分），在得分超过总体阈值（如 5.0 分）时才触发动作。昆仑邮件系统的 TurboGate 网关在生产环境中采用此三层层级体系，上线 18 个月以来 DNSBL 相关误报事件为 0。

### 参考文献

1. RFC 5782 — DNS Blacklists and Whitelists (IETF, February 2010). Section 2 DNSBL Query Mechanics, Section 2.2 IPv4 Return Codes, Section 2.3 Return Code Semantics, Section 3 Security Considerations.
2. RFC 1035 — Domain Names — Implementation and Specification (IETF, November 1987). DNS A record query format.
3. Spamhaus Project — Zen Combined DNSBL.
   <https://www.spamhaus.org/zen/>
   — SBL, XBL, CSS, PBL sub-zones and return codes.
4. Barracuda Reputation Block List (BRBL).
   <https://www.barracudacentral.org/lookups/ip-reputation>
5. SURBL — Spam URI Realtime Blocklists.
   <https://www.surbl.org/>
   — URIBL sub-lists and query format.
6. DNSWL.org — DNS Whitelist.
   <https://www.dnswl.org/>
   — Trust level encoding and application procedure.
7. rbldnsd — RBL DNS Daemon.
   <https://github.com/shmulik-klein/rbldnsd>
   . Data set format and configuration options.
8. NIST SP 800-45 Version 2 — Guidelines on Electronic Mail Security (NIST, February 2007). Section 5.3 Blacklists and Whitelists.
9. GB/T 30282-2013 — 信息安全技术 反垃圾邮件产品技术要求和测试评价方法. 第 5.2 节 DNS 黑名单检测.
10. Postfix RBL Readme —
    <https://www.postfix.org/postconf.5.html#reject_rbl_client>

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/dnsbl-blacklist-guide.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
