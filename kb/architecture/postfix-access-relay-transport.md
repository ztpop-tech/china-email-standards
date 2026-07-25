---
title: "Postfix Access / Relay / Transport 三层策略设计：安全边界、配置原则与性能影响"
source: "https://ztpop.net/kb/postfix-access-relay-transport.html"
license: CC-BY 4.0
---

# Postfix Access / Relay / Transport 三层策略设计：安全边界、配置原则与性能影响

## 1. 三层策略的时序与责任边界

### 1.1 SMTP会话的检查顺序

Postfix的smtpd(8)进程在完整的SMTP会话中按严格的时序执行检查 [1]：

```
连接阶段 (smtpd_client_restrictions)
  ↓
EHLO/HELO阶段 (smtpd_helo_restrictions)
  ↓
MAIL FROM阶段 (smtpd_sender_restrictions)
  ↓
RCPT TO阶段 (smtpd_recipient_restrictions) ← 最密集
  ↓  ┌─── relay_domains 在此阶段检查
  ↓  ├─── access 检查 (check_*_access)
  ↓  └─── mydestination 接收判断
  ↓
DATA阶段 (smtpd_data_restrictions)
  ↓
END-OF-MESSAGE (smtpd_end_of_data_restrictions)
  ↓
队列 → clean → pickup → 入站处理完成
  ↓
出站: qmgr → transport (transport_maps决定) → smtp (连接目标MTA)
          ↓
     fallback_relay / relay_transport (无匹配时的回退)
```

### 1.2 三层职责总结

| 策略层 | 配置文件 | 处理阶段 | 主要职责 |
| --- | --- | --- | --- |
| Access | smtpd\_\*\_restrictions | SMTP会话（RCPT TO前） | 连接控制、黑白名单、SPF/DNSBL策略检查 |
| Relay | relay\_domains | SMTP会话（RCPT TO时） | 中继授权边界——确定接收还是中继 |
| Transport | transport\_maps | 队列处理（qmgr调度） | 路由规则——指定出站邮件的MTA/端口/传输方式 |

## 2. Access 层：smtpd\_\*\_restrictions 详解

### 2.1 UCE检查清单

Postfix的UCE（Unsolicited Commercial Email）检查清单是邮件安全的第一道防线 [1]。推荐的完整配置：

```
# /etc/postfix/main.cf

# ==== 连接层 ====
smtpd_client_restrictions =
    permit_mynetworks           # 内网IP直接放行
    permit_sasl_authenticated   # SASL认证用户放行
    reject_rbl_client zen.spamhaus.org    # DNSBL实时黑名单
    reject_rbl_client bl.spamcop.net
    reject_rhsbl_client dbl.spamhaus.org
    permit

# ==== EHLO/HELO层 ====
smtpd_helo_required = yes
smtpd_helo_restrictions =
    permit_mynetworks
    reject_invalid_helo_hostname
    reject_non_fqdn_helo_hostname      # HELO必须是完整域名
    check_helo_access hash:/etc/postfix/helo_access
    permit

# ==== MAIL FROM层 ====
smtpd_sender_restrictions =
    permit_mynetworks
    permit_sasl_authenticated
    reject_non_fqdn_sender              # 发件地址必须是FQDN
    reject_unknown_sender_domain        # 域名必须可解析
    check_sender_access hash:/etc/postfix/sender_access
    permit

# ==== RCPT TO层（最密集） ====
smtpd_recipient_restrictions =
    permit_mynetworks
    permit_sasl_authenticated
    reject_unauth_destination           # 核心：防止开放中继
    reject_non_fqdn_recipient
    reject_unknown_recipient_domain
    check_recipient_access hash:/etc/postfix/recipient_access
    reject_unverified_bounce            # BATV退信验证（如启用）
    reject_unauth_pipelining
    permit
```

### 2.2 check\_\*\_access 表设计原则

access表（hash格式）支持域名级、邮箱级的多粒度匹配 [2]：

```
# /etc/postfix/recipient_access
example.com               OK            # 无条件接收
spamdomain.com            REJECT        # 整域拒绝
user@malicious.com        550 5.1.1 Blocked by policy
@badhosting.net           REJECT        # 子域通配

# /etc/postfix/sender_access
goodpartner.com           OK
bulkmailer.example.com    REJECT        # 仅拒绝该发件人

# 注意：access表是正则非贪婪匹配——@badhosting.net
# 匹配所有以 badhosting.net 结尾的地址
```

### 2.3 Access层性能特征

* **延迟敏感**：每个检查都在SMTP会话中同步完成。DNSBL查询和rbl检查是IO密集型操作——如果DNSBL服务响应慢，整个SMTP握手会停滞。
* **缓存**：Postfix内置ncache（负缓存）和scache（正缓存）机制，重复检查省略。
* **表类型选择**：hash（数据库表）比regexp（正则表达式表）快10-100倍。大量规则建议先hash后regexp。
* **检查顺序**：permit类排在前面可短路后续检查——SASL认证用户应绕过DNSBL。

## 3. Relay层：relay\_domains 安全边界

### 3.1 收件与中继的本质区别

Postfix根据RCPT TO地址决定是本地接收（投递到mydestination指定的域）还是中继（转发出站）。relay\_domains定义了哪些域是"授权代收"的——通常是托管域的MX目标。安全模型 [1]：

* `mydestination`：匹配该参数的域 → 作为终极目标接收
* `relay_domains`：匹配该参数的域 → 授权中继到下一跳（通常是互联网上的其他MTA）
* **都不匹配**：reject\_unauth\_destination触发 → 550拒绝（非开放中继的核心原理）

### 3.2 relay\_domains 配置示例

```
# /etc/postfix/main.cf
myhostname = mail.example.com
mydomain = example.com
myorigin = $mydomain

# 本地接收域
mydestination = $myhostname, localhost.$mydomain, localhost, $mydomain

# 授权中继域（邮件托管服务）
relay_domains = $mydomain
relay_domains = hash:/etc/postfix/relay_domains   # 或使用数据库

# 中继域查找
relay_recipient_maps = hash:/etc/postfix/relay_recipients

# relay_domains 数据库文件
# /etc/postfix/relay_domains:
# example.net           OK
# partner-company.com   OK
```

### 3.3 中继授权的安全陷阱

* **开放中继（Open Relay）**：如果relay\_domains包含\*或配置了permit任何未授权目的地的规则，Postfix成为开放中继。RFC 2505（Anti-Spam Recommendations for SMTP MTAs）将此列为最高优先级反制措施 [3]。
* **relay\_domains与mydestination重叠**：同一个域如果同时出现在两者中，Postfix优先作为收件处理。多域名环境下建议使用明确的数据库映射。
* **relay\_recipient\_maps的精度**：如果不配置，Postfix接受relay\_domains中任何收件人（可以中继不存在收件人的邮件给下游MTA，导致成为垃圾邮件回弹问题）。
* **性能考量**：relay\_domains每RCPT查询一次。对于高吞吐邮件集群，建议使用proxymap表（共享缓存）而非独立的hash文件。

## 4. Transport层：transport\_maps 出站路由

### 4.1 路由规则语法

transport\_maps在队列处理（qmgr）阶段查询，决定出站邮件的传输通道 [1]：

```
# /etc/postfix/transport 格式：
# domain transport:nexthop
domain                  transport:nexthop

# 示例
example.com             smtp:mail.example.com       # 通过指定MX中继
[198.51.100.10]         smtp:[10.0.0.1]:2525        # IP+端口覆盖
.example.net            relay:                      # 子域通配，使用relay传输
*                       smtp:fallback.example.com   # 默认回退
```

### 4.2 生产级transport配置

```
# /etc/postfix/main.cf
transport_maps = hash:/etc/postfix/transport

# 默认传输（transport_maps未匹配时）
default_transport = smtp

# relay传输（当relay_domains匹配且无transport_maps时）
relay_transport = relay

# 当所有出站尝试失败时（延迟而非退回）
fallback_transport_maps = hash:/etc/postfix/fallback_transport
# fallback_relay通常用于智能主机场景

# /etc/postfix/transport:
# 将发往 partner.com 的邮件通过专用中继发送
partner.com             smtp:partner-relay.example.com:587

# 发往特定域的邮件限制并发数
# 通过master.cf中定义多个smtp实例，每个配置不同的process_limit
highvolume.example.com  smtp-fast:

# 将某个域的全部邮件转发到另一个MTA（内部MTLS流量）
internal-corp.com       smtp:[10.0.10.100]:2525

# 更新transport映射
postmap /etc/postfix/transport
```

### 4.3 关于[braket]（字面量）的行为

transport表中的[braket]语法（如`smtp:[10.0.0.1]`）指示Postfix不进行MX查询，直接将邮件发送至指定的IP/主机名。未使用[]时，Postfix会对此主机进行MX解析（可能覆盖意图）。此机制在RFC 5321 §5.1（地址解析顺序）中有详细描述 [4]。区别：

```
# 无[] — 进行MX/A/AAAA查询
smtp:mail.example.com
# → Postfix 查询 mail.example.com 的 MX
#   → 如果存在MX则使用MX；否则使用A/AAAA记录

# 有[] — 跳过MX查询，直接连接
smtp:[mail.example.com]
# → 跳过MX查询，直接A/AAAA解析 mail.example.com

smtp:[198.51.100.10]
# → 字面量IP，直接连接
```

## 5. 三层策略的交互与故障排查

### 5.1 决策树

```
SMTP RCPT TO 到达
  ↓
是否在 mydestination 中？
  ├── 是 → 本地投递（不检查relay_domains）
  └── 否 → 继续
      ↓
reject_unauth_destination 是否触发？
  ├── 是 → 550拒绝（除非在relay_domains中）
  └── 否 → 继续
      ↓
是否在 relay_domains 中？
  ├── 是 → 授权中继
  │   ↓
  │  transport_maps有匹配？
  │   ├── 是 → 使用指定传输通道
  │   └── 否 → relay_transport（默认）
  │       ↓
  │  fallback_relay → MX解析 → 出站连接
  └── 否 → 550拒绝（非授权中继）
```

### 5.2 故障排查命令

```
# 模拟邮件检查（不发送）
postmap -q "user@example.com" hash:/etc/postfix/recipient_access
postmap -q "example.com" hash:/etc/postfix/transport
postmap -q "example.com" hash:/etc/postfix/relay_domains

# 验证中继授权
postconf -n | grep -E 'relay_domain|mydestination|reject_unauth'

# 检查transport映射是否加载
postconf -n | grep transport_maps
postmap -s hash:/etc/postfix/transport

# 日志分析
grep "relay=" /var/log/mail.log | tail -20
grep "transport=" /var/log/mail.log | tail -20

# 检查邮件是否因relay拒绝
grep "relay access denied" /var/log/mail.log | tail -10
```

## 6. 性能影响分析

### 6.1 各层开销对比

| 操作 | 平均延迟 | 缓存生效 | 并发影响 |
| --- | --- | --- | --- |
| hash表查询（mmap） | ~10μs | 隐式（mmap页面缓存） | 无 |
| regexp表匹配（10条） | ~50μs | 不适用 | 低 |
| DNSBL查询（无缓存） | 50-500ms | ncache/scache | 显著 |
| relay\_domains数据库查询 | ~100μs-1ms | proxymap共享 | 低 |
| transport\_maps查询 | ~10μs-1ms | qmgr内部缓存 | 低（队列处理阶段） |

### 6.2 Access层过载保护

`smtpd_client_restrictions`在其第一阶段（DNSBL查询）可能造成过载。如果DNSBL服务不可用，Postfix会阻塞连接建立。配置了多个DNSBL的服务器的典型问题是：一个慢速的DNSBL延迟了整个入站邮件接收。设置`smtpd_client_restrictions`的超时和跳过的机制 [5]：

```
# 设置DNSBL查询超时（避免依赖外部服务导致阻塞）
smtpd_client_event_limit_exceptions = $mynetworks
smtpd_client_connection_count_limit = 10
smtpd_client_connection_rate_limit = 30

# 使用postscreen前检查（Postfix 2.8+）减轻smtpd压力
# 将部分检查前置到postscreen
postscreen_dnsbl_threshold = 3
postscreen_dnsbl_sites = zen.spamhaus.org*3
    bl.spamcop.org*2
    dbl.spamhaus.org*1
```

## 7. 多层协同设计实例

### 7.1 典型多租户邮件中继设计

```
# 场景：邮件服务平台，为500个客户域提供邮件中继和托管

# Access层 — 客户专属连接策略
smtpd_client_restrictions =
    (hash) /etc/postfix/customer_whitelist  # 客户MTA IP白名单
    permit_mynetworks
    reject_rbl_client zen.spamhaus.org
    permit

# Relay层 — 客户域映射
relay_domains = hash:/etc/postfix/relay_domains
relay_recipient_maps = hash:/etc/postfix/relay_recipients

# Transport层 — 按客户路由到专用出站IP池
transport_maps = hash:/etc/postfix/transport
# /etc/postfix/transport:
# customer1.com  smtp:outbound-1.example.com:25
# customer2.com  smtp:outbound-2.example.com:25
```

## 参考文献

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/postfix-access-relay-transport.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
