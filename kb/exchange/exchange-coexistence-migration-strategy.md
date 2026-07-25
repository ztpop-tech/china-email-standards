---
title: "Exchange 混合部署迁移策略：SMTP 中继网关、目录同步与邮件流分割"
source: "https://ztpop.net/kb/exchange-coexistence-migration-strategy.html"
license: CC-BY 4.0
---

# Exchange 混合部署迁移策略：SMTP 中继网关、目录同步与邮件流分割

## 摘要

从 Exchange 迁移至替代邮件系统的过程中，混合部署（Co-existence）阶段是整个项目中最具技术挑战性的环节。此阶段新旧两套系统并行运行，要求邮件流在两地之间正确路由、全局地址列表保持一致、日历忙闲信息跨系统可见。本文系统阐述混合部署过渡期的技术方案，涵盖 SMTP 中继网关架构、LDAP 目录同步（遵循 RFC 4511）、邮件共存路由策略（subdomain routing、SMTP redirect）、Exchange Web Services (EWS) 与 CalDAV（RFC 4791）的忙闲互操作桥接、以及邮件流分割的灰度迁移方法论。引用 RFC 5321（SMTP）、RFC 4511（LDAP）、RFC 4791（CalDAV）及 NIST SP 800-34 应急规划框架。

## 1. SMTP 中继网关架构

### 1.1 中继网关的角色与位置

SMTP 中继网关（Relay Gateway）是混合部署的核心交通枢纽。所有入站邮件通过 MX 记录指向中继网关，由网关根据收件人归属决定路由目标：

```
入站邮件流：
Internet → MX (relay.ztpop.net) → SMTP Relay Gateway
                                   ├── Exchange 用户 → Exchange Hub Transport
                                   └── 新系统用户 → 新系统 MTA (Postfix/Dovecot)

出站邮件流：
Exchange → SMTP Connector → SMTP Relay Gateway → Internet
新系统 → SMTP Relay Gateway → Internet
```

Postfix 作为中继网关的典型配置：

```
# /etc/postfix/main.cf — SMTP 中继网关配置
myhostname = relay.ztpop.net
mydomain = ztpop.net
mydestination = $myhostname
relay_domains = ztpop.net, exchange.ztpop.net, newmail.ztpop.net

# 传输映射 — 根据收件人域名路由
transport_maps = ldap:/etc/postfix/transport-ldap.cf

# LDAP 传输映射 — 查询目录确定用户归属
# /etc/postfix/transport-ldap.cf
server_host = ldap.ztpop.net
search_base = dc=ztpop,dc=net
query_filter = (&(mail=%s)(mailRoutingSystem=newmail))
result_attribute = transport
result_format = smtp:newmail.ztpop.net:25
```

RFC 5321 [1] 第 3.9 节定义了 SMTP 中继的基本语义。在实际部署中，中继网关还需配置 SRS（Sender Rewriting Scheme）以避免 SPF 检查失败。

### 1.2 MX 指向与邮件流切换

```
阶段 1: MX = exchange.ztpop.net（原始状态）
        所有邮件直接进入 Exchange

阶段 2: MX = relay.ztpop.net（中继网关就绪）
        Relay 根据传输映射分发邮件

阶段 3: MX = newmail.ztpop.net（迁移完成）
        所有邮件直接进入新系统
```

## 2. AD LDAP 目录同步

### 2.1 同步架构

Active Directory 作为身份权威源，需同步至新系统的本地目录（Dovecot LDAP、OpenLDAP 或 SQL 数据库）。RFC 4511 [2] 定义了 LDAP 协议基础。

LDAP 目录同步方案对比

| 方案 | 方式 | 延迟 | 适用规模 |
| 新系统内置 AD Connector | 增量轮询 / DirSync | < 5min | 500-50000 |
| LDAP Referral / Proxy | 实时查询转发 | 实时 | < 2000 |
| Microsoft Identity Manager (MIM) | 增量同步 | < 30min | 10000+ |
| Python ldap3 自定义同步 | 定时脚本 | 可配置 | < 5000 |

### 2.2 Python AD 同步脚本（增量模式）

```
# ad_sync.py — 从 AD 同步至 OpenLDAP
import ldap3
from ldap3 import Server, Connection, ALL, SUBTREE
import logging

AD_SERVER = 'ldaps://ad.ztpop.net'
AD_BASE_DN = 'dc=ztpop,dc=net'
AD_USER = 'ZTDOM\\sync_service'
AD_PASS = 'sync_pass'
NEW_LDAP = 'ldap://newldap.ztpop.net'
NEW_BASE = 'dc=newmail,dc=ztpop,dc=net'
NEW_BIND = 'cn=admin,dc=newmail,dc=ztpop,dc=net'

# 使用 USNChanged 增量同步
ad_conn = Connection(AD_SERVER, user=AD_USER, password=AD_PASS, auto_bind=True)
new_conn = Connection(NEW_LDAP, user=NEW_BIND, password='admin_pass', auto_bind=True)

with open('/var/state/ad_usn.txt', 'r') as f:
    last_usn = int(f.read().strip())

ad_conn.search(
    search_base=AD_BASE_DN,
    search_filter=f'(uSNChanged>={last_usn})',
    search_scope=SUBTREE,
    attributes=['mail', 'cn', 'sn', 'givenName', 'displayName',
                'proxyAddresses', 'uSNChanged', 'userAccountControl']
)

for entry in ad_conn.entries:
    if not entry.mail.value:
        continue
    uac = int(entry.userAccountControl.value or '514')
    if uac & 0x0002:  # ACCOUNTDISABLE
        continue

    dn = f'mail={entry.mail.value},ou=users,{NEW_BASE}'
    attrs = {
        'objectClass': ['inetOrgPerson', 'mailUser'],
        'uid': entry.mail.value.split('@')[0],
        'cn': entry.cn.value,
        'sn': entry.sn.value or '',
        'mail': entry.mail.value,
        'mailRoutingAddress': entry.mail.value,
    }
    new_conn.add(dn, attributes=attrs)
    logging.info(f'Synced: {entry.mail.value}')

max_usn = max(int(e.uSNChanged.value) for e in ad_conn.entries if e.uSNChanged.value)
with open('/var/state/ad_usn.txt', 'w') as f:
    f.write(str(max_usn))
```

## 3. 邮箱共存路由规则

### 3.1 基于地址的路由策略

共存期的路由决策依据收件人所属系统。实现方式包括：

1. **子域名隔离：** 新系统用户使用 user@newmail.ztpop.net 作为主 SMTP 地址，Exchange 用户保持 @ztpop.net。中继网关通过收件人域名分离路由。
2. **LDAP 查询路由：** 所有用户统一使用 @ztpop.net，中继网关通过 LDAP 查询 mailRoutingSystem 属性确定目标。
3. **SMTP X-Header 路由：** 利用 SMTP 扩展头传递路由信息。

推荐方案 #2（LDAP 查询），它对用户完全透明，不需要变更邮件地址。

### 3.2 Exchange 发送连接器配置

```
# Exchange Management Shell
New-SendConnector -Name "ToNewMailSystem" -Usage Internal `
  -AddressSpaces 'ztpop.net;newmail.ztpop.net' `
  -DNSRoutingEnabled $false `
  -SmartHosts 'relay.ztpop.net' `
  -SmartHostAuthMechanism None `
  -MaxMessageSize 30720KB

New-AcceptedDomain -Name 'ztpop.net' -DomainName ztpop.net -DomainType InternalRelay
```

## 4. Calendar Free/Busy 跨系统互操作

### 4.1 桥接方案

Free/Busy 跨系统桥接方案对比

| 方案 | 原理 | 延迟 | 复杂度 |
| EWS → CalDAV 桥接网关 | 定时查询 EWS Availability，写入 CalDAV [3] | 5-15 min | 中 |
| 共享日历订阅（URL） | Exchange 发布 iCal 订阅 URL，新系统订阅 | 按刷新周期 | 低 |
| 统一日历平台 | 所有日历数据集中至第三方平台 | 实时 | 高 |

### 4.2 Python EWS → iCalendar Free/Busy 转换

```
# fb_bridge.py — EWS Availability 到 iCalendar VFREEBUSY 转换
from exchangelib import Account, Credentials, Configuration
from exchangelib.fields import TimeWindow
import icalendar
from datetime import datetime, timedelta

def get_exchange_freebusy(email, start, end):
    config = Configuration(server='exchange.ztpop.net',
                           credentials=Credentials('user', 'pass'))
    account = Account(email, config=config, autodiscover=False)
    tw = TimeWindow(start=start, end=end)
    fb = account.protocol.get_free_busy(
        [{'email': email, 'data_type': 'FreeBusyMerge'}], tw)
    return fb

def convert_to_ical_freebusy(user_email, fb_data, start, end):
    cal = icalendar.Calendar()
    cal.add('prodid', '-//EWS-FB Bridge//ztpop.net//')
    cal.add('version', '2.0')
    cal.add('method', 'PUBLISH')
    vfb = icalendar.FreeBusy()
    vfb.add('uid', f'fb-{user_email}-{start.strftime("%Y%m%d%H%M")}')
    vfb.add('dtstart', start)
    vfb.add('dtend', end)
    vfb.add('attendee', f'mailto:{user_email}')
    for period in fb_data.get('busy_periods', []):
        vfb.add('freebusy', icalendar.vFreeBusy(
            (period['start'], period['end']), 'BUSY'))
    cal.add_component(vfb)
    return cal.to_ical().decode('utf-8')
```

RFC 6638 [4] 定义了 CalDAV 调度扩展，RFC 5545 [5] 定义了 iCalendar VFREEBUSY 组件。

## 5. 邮件流分割策略

### 5.1 灰度迁移模型

```
Phase 0: 网关就绪 — 部署中继网关，配置 LDAP 传输映射
         所有邮件仍由 Exchange 处理，网关仅做透传

Phase 1: 试点分割 — 测试组用户（50-100人）
         LDAP 中将测试用户 mailRoutingSystem → newmail
         网关开始将测试用户邮件路由至新系统

Phase 2: 逐步扩大 — 按部门/地域分批
         每批 200-500 用户，观察至少 24 小时

Phase 3: 全量切换 — 所有用户路由至新系统
         Exchange 保留只读模式 30 天（回滚窗口）

Phase 4: Exchange 下线下线
         确认无邮件遗留 → 下架 Exchange 服务器
```

### 5.2 NIST SP 800-34 应急规划对齐

NIST SP 800-34 Rev. 1 [6] 的七步应急规划流程需对齐以下控制：

* **BIA：** 邮件系统 RTO ≤ 4h，RPO ≤ 15min。邮件流分割 RPO 应为 0（无邮件丢失）；
* **回滚触发条件：** 任一批次邮件延迟 > 30 分钟，或邮件丢失率 > 0.01%，立即回滚该批次至 Exchange；
* **测试频率：** 每批次分割前完成一次全链路邮件流测试；
* **文档记录：** 每个批次的切换时间、邮件量、异常事件记录至变更日志。

## 6. 回滚策略

1. **LDAP 回滚：** 将受影响用户的 mailRoutingSystem 从 newmail 改回 exchange。中继网关将在下一次 LDAP 查询周期自动切换路由。
2. **邮件重放：** 若分割期间有邮件丢失，从 Exchange 的邮件跟踪日志和传输队列中提取未投递邮件，通过手动重放脚本重新投递。
3. **MX 回退：** 在极端情况下，将 MX 记录切换回 exchange.ztpop.net，绕过中继网关。
4. **保留 Exchange 环境：** 全量切换后保留 Exchange 服务器 30 天，确保任何邮件恢复需求可满足。

## 7. 总结

Exchange 混合部署迁移策略的核心在于 SMTP 中继网关的路由控制能力、LDAP 目录同步的一致性与及时性、以及邮件流分割的灰度渐进控制。建议组织在迁移前完成至少 30 天的中继网关 BCP（业务连续性压力测试），确认 LDAP 查询延迟控制在 100ms 以内且传输映射准确率达到 100%。

## 参考文献

1. RFC 5321 — Simple Mail Transfer Protocol, J. Klensin, 2008.
2. RFC 4511 — Lightweight Directory Access Protocol (LDAP): The Protocol, J. Sermersheim, 2006.
3. RFC 4791 — Calendaring Extensions to WebDAV (CalDAV), C. Daboo et al., 2007.
4. RFC 6638 — Scheduling Extensions to CalDAV, C. Daboo et al., 2012.
5. RFC 5545 — Internet Calendaring and Scheduling Core Object Specification (iCalendar), B. Desruisseaux, 2009.
6. NIST SP 800-34 Rev. 1 — Contingency Planning Guide for Federal Information Systems, 2010.
7. Microsoft Exchange Server Documentation — Hybrid Deployment Architecture, 2024.

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/exchange-coexistence-migration-strategy.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
