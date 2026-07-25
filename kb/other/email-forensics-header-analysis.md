---
title: "判断是否存在伪造"
source: "https://ztpop.net/kb/email-forensics-header-analysis.html"
license: CC-BY 4.0
---

# 判断是否存在伪造

邮件取证攻击溯源 — 基于邮件头的追踪分析技术与 Received 链重构

## 

|  |  |  |  |
| --- | --- | --- | --- |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |

**取证原则：**

路由追踪类字段（Received）的可信度最高，因为它们是在传输过程中由第三方 MTA 写入的。内容声明类字段可被 MUA 任意构造，必须通过路由追踪字段交叉验证。

## 二、Received 链基础结构

[RFC 5321 §4.4](https://datatracker.ietf.org/doc/html/rfc5321#section-4.4)
定义了 SMTP 协议的 trace 机制。每一台参与邮件转发的 MTA 都必须在邮件顶部添加一条
`Received`
头。阅读时从上到下即为从目标到源的反向路径：

```
Received: from mail.example.com (mail.example.com [203.0.113.45])
    by mx.recipient.com (Postfix) with ESMTPS id 4xV7qK2nRtz9sD
    for ; Thu, 3 Jul 2025 14:22:17 +0800 (CST)

Received: from sender.mta.org (sender.mta.org [198.51.100.77])
    by mail.example.com (Postfix) with ESMTP id A1bC3dEfGh
    for ; Thu, 3 Jul 2025 14:21:05 +0800 (CST)

Received: from [192.168.1.100] (unknown [203.0.113.200])
    by sender.mta.org (Postfix) with ESMTPA id Z9yX8wV7uT6r
    for ; Thu, 3 Jul 2025 14:20:30 +0800 (CST)
```

▲ 从下往上读：首跳是 203.0.113.200（攻击者 SMTP 客户端），经由 sender.mta.org 和 mail.example.com，最终到达 mx.recipient.com。

[RFC 5321](https://datatracker.ietf.org/doc/html/rfc5321#section-4.4)
规定的
`Received`
行由以下子字段组成：

二、Received 链基础结构

| 子字段 | 含义 | 取证价值 |
| --- | --- | --- |
| `from` | 声称的发送方主机名（EHLO 参数） | 可与 DNS 反向解析对比；伪造时出现不一致 |
| `by` | 接收方 MTA 主机名 | 确认邮件路径中的实际节点 |
| `with` | 传输协议（ESMTP/ESMTPS/ESMTPA） | ESMTPA 表示已认证提交；没有 A 的跳可能是开放中继 |
| `for` | 信封收件人 | 可与 To 头对比，发现 BCC 盲送或收件人不一致 |
| `id` | MTA 内部分配的消息 ID | 唯一标识一次 SMTP 事务；用于与 MTA 日志交叉比对 |
| `时间戳` | 接收时间（含时区） | 构建传输时间线，检测时间异常 |
| `IP 地址` | TCP 连接的对端 IP（方括号内） | 唯一不可伪造的溯源锚点 |

**注意：**
`from`

子字段中的 EHLO 主机名和 IP 反向 DNS 均可被攻击者控制。只有方括号内的 IP 地址是 TCP 握手时由内核提供的，无法伪造。取证分析必须以 IP 为锚点，用 EHLO 和 rDNS 作为辅助佐证。

## 三、Received 链深度解析

### 3.1 from / by 匹配规则

正常的邮件传输中，第 N 跳的
`by`
应与第 N+1 跳的
`from`
在主机名上匹配（或至少在同一管理域内）。如果出现相邻跳之间
`by`
和
`from`
毫无关联，这是典型的伪造插入迹象。

以下脚本从 .eml 文件解析 Received 链，输出每跳的 from/by/ip 三元组，并标记相邻跳不匹配：

```
#!/usr/bin/env python3
"""parse_received_chain.py — 解析 .eml 文件的 Received 链"""
import email, re, sys
from email import policy

def parse_received(eml_path):
    with open(eml_path, 'rb') as f:
        msg = email.message_from_binary_file(f, policy=policy.default)

    received = msg.get_all('Received') or []
    hops = []
    for line in received:
        line = line.replace('\n', ' ').replace('\r', ' ')
        from_m = re.search(r'from\s+(\S+)', line)
        by_m   = re.search(r'by\s+(\S+)', line)
        ip_m   = re.search(r'\[(\d+\.\d+\.\d+\.\d+)\]', line)
        with_m = re.search(r'with\s+(\S+)', line)
        ts_m   = re.search(r';\s+(.+)$', line)
        hops.append({
            'from':  from_m.group(1).rstrip() if from_m else None,
            'by':    by_m.group(1).rstrip() if by_m else None,
            'ip':    ip_m.group(1) if ip_m else None,
            'with':  with_m.group(1) if with_m else None,
            'ts':    ts_m.group(1).strip() if ts_m else None,
            'raw':   line.strip()
        })

    # Received 头顺序：顶端 = 最近一跳，所以反向遍历即从源到目标
    hops.reverse()

    print(f"{'#':<3} {'From':<28} {'By':<28} {'IP':<18} {'With':<12} {'Timestamp'}")
    print("-" * 130)
    for i, h in enumerate(hops):
        f = h['from'] or '-'
        b = h['by'] or '-'
        ip = h['ip'] or '-'
        w = h['with'] or '-'
        t = h['ts'] or '-'
        flag = ''
        if i > 0 and hops[i-1].get('by') and h.get('from'):
            prev_by = hops[i-1]['by'].lower()
            cur_from = h['from'].lower()
            if prev_by not in cur_from and cur_from not in prev_by:
                flag = ' ⚠ MISMATCH'
        print(f"{i+1:<3} {f:<28} {b:<28} {ip:<18} {w:<12} {t}{flag}")

    return hops

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} ")
        sys.exit(1)
    parse_received(sys.argv[1])
```

### 3.2 with 协议类型的取证含义

3.2 with 协议类型的取证含义

| 协议标记 | 含义 | 常见场景 |
| --- | --- | --- |
| `ESMTPA` | 扩展 SMTP + 认证 | 合法用户通过 MSA 提交邮件 |
| `ESMTPS` | 扩展 SMTP + STARTTLS | MTA 间 TLS 传输 |
| `ESMTP` | 扩展 SMTP（无认证、无 TLS） | 开放中继或内部传输 |
| `LMTP` | 本地邮件传输协议 | MTA → MDA 最后一跳 |
| `HTTP` | 通过 Web API 提交 | Webmail、API 发送 |

如果首跳（源跳）标记为
`ESMTPA`
，说明攻击者使用了经过认证的 SMTP 账号 —— 这意味着凭据已泄露。如果没有认证标记而直接是
`ESMTP`
，则可能经过了开放中继或直接 SMTP 注入。

### 3.3 Return-Path 与信封发件人

`Return-Path`
由最终投递的 MDA 根据 SMTP 会话的
`MAIL FROM`
写入（
[RFC 5321 §4.4](https://datatracker.ietf.org/doc/html/rfc5321#section-4.4)
）。它与邮件头的
`From`
可以在 BEC/EAC 攻击中完全不同：

```
Return-Path: 
From: "CEO Name" 
Reply-To: "CEO Name"
```

上面这个组合是 BEC 攻击的典型特征：
`Return-Path`
指向一个被攻破的营销平台，
`From`
伪装成高管，
`Reply-To`
指向攻击者控制的免费邮箱。

## 四、BEC/EAC 攻击的邮件头特征

BEC（Business Email Compromise）和 EAC（Email Account Compromise）是当前造成损失最大的邮件威胁类型。MITRE ATT&CK 将其归类为
[T1566 Phishing](https://attack.mitre.org/techniques/T1566/)
的多个子技术。以下是从邮件头角度识别此类攻击的关键指标：

四、BEC/EAC 攻击的邮件头特征

| 指标 | 检测方法 | 严重程度 |
| --- | --- | --- |
| Reply-To 与 From 域不同 | 提取 From 和 Reply-To 的域名部分，比较是否一致 | 高 |
| 显示名冒充 | 检查 From 的 display-name 是否匹配已知高管姓名，但实际邮箱域不同 | 高 |
| 首跳 IP 地理异常 | 首跳 IP GeoIP 查询结果与声称的发件人所在国家不匹配 | 中 |
| Return-Path ≠ From 域 | 信封域与头部声明域不一致 | 中 |
| 相邻跳 by/from 不匹配 | Received 链中插入的伪造跳 | 极高 |
| 认证结果旁路 | SPF/DKIM/DMARC 均为 none 或 temperror | 中 |
| Message-ID 域与 From 域不一致 | Message-ID 右侧域名与实际发件域不同 | 中 |

### 4.1 Reply-To 劫持

攻击者在
`From`
中使用受害者域以通过 SPF 检查，同时设置
`Reply-To`
指向攻击者邮箱。收件人的邮件客户端回复时，目标地址是 Reply-To 而非 From。

```
#!/usr/bin/env python3
"""check_replyto_hijack.py — 检测 Reply-To 劫持"""
import email, sys
from email import policy
from email.utils import parseaddr, getaddresses

def check(eml_path):
    with open(eml_path, 'rb') as f:
        msg = email.message_from_binary_file(f, policy=policy.default)

    from_addr = msg.get('From', '')
    reply_to  = msg.get('Reply-To', '')
    return_path = msg.get('Return-Path', '')

    _, from_email = parseaddr(from_addr)
    _, rp_email   = parseaddr(return_path)
    rt_list = getaddresses([reply_to]) if reply_to else []

    from_domain = from_email.split('@')[-1] if '@' in from_email else ''
    rp_domain   = rp_email.split('@')[-1] if '@' in rp_email else ''

    alerts = []
    if from_domain and rp_domain and from_domain != rp_domain:
        alerts.append(f"Return-Path 域 ({rp_domain}) ≠ From 域 ({from_domain})")

    for disp, addr in rt_list:
        rt_domain = addr.split('@')[-1] if '@' in addr else ''
        if rt_domain and from_domain and rt_domain != from_domain:
            alerts.append(f"Reply-To 域 ({rt_domain}) ≠ From 域 ({from_domain}) — 疑似 Reply-To 劫持")
            # 检查是否为免费邮箱（常见攻击手法）
            free_providers = {'gmail.com','outlook.com','yahoo.com','proton.me','mail.ru','yandex.ru'}
            if rt_domain.lower() in free_providers:
                alerts.append(f"  ↳ Reply-To 指向免费邮箱 {rt_domain}，高度可疑")

    if alerts:
        print("[!] 告警：")
        for a in alerts: print(f"    {a}")
    else:
        print("[✓] 未发现 Reply-To / Return-Path 劫持特征")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} ")
        sys.exit(1)
    check(sys.argv[1])
```

### 4.2 显示名欺骗

[RFC 5322 §3.4](https://datatracker.ietf.org/doc/html/rfc5322#section-3.4)
定义了地址格式：
`display-name`
。大多数邮件客户端只展示显示名而不展示完整邮箱地址。攻击者利用这一点，将显示名设置为高管姓名，而实际邮箱地址指向无关域。

**真实案例模式：**
`From: "张伟 CEO"`

— 移动端邮件客户端通常只渲染 "张伟 CEO"，收件人根本无法看到实际发件地址。

## 五、发件 IP 追踪与地理定位

Received 链中方括号内的 IP 地址是唯一无法被攻击者伪造的字段。通过对首跳 IP 进行 GeoIP 查询与 ASN 归属分析，可以回答以下问题：

* 发件人实际所在地是否与声称的公司所在地一致？
* 发件 IP 是否属于数据中心/VPS 网段（而非企业/住宅宽带）？
* 发件 IP 是否在已知恶意 IP 库（AbuseIPDB、CINS Army、Spamhaus DROP）中？

```
#!/usr/bin/env python3
"""geoip_trace.py — 对 Received 链中所有 IP 执行 GeoIP + ASN 查询"""
import email, re, sys, json, subprocess
from email import policy

# 依赖: pip install geoip2 — 需要 MaxMind GeoLite2 City + ASN 数据库
try:
    import geoip2.database
except ImportError:
    print("请安装 geoip2: pip install geoip2")
    sys.exit(1)

def extract_ips(eml_path):
    with open(eml_path, 'rb') as f:
        msg = email.message_from_binary_file(f, policy=policy.default)
    received = msg.get_all('Received') or []
    ips = []
    for line in received:
        for ip in re.findall(r'\[(\d+\.\d+\.\d+\.\d+)\]', line):
            if ip not in ips and not ip.startswith(('127.','10.','172.16.','192.168.')):
                ips.append(ip)
    ips.reverse()  # 从源到目标
    return ips

def query_geoip(ip, city_db, asn_db):
    result = {'ip': ip, 'city': '-', 'country': '-', 'asn': '-', 'org': '-'}
    try:
        with geoip2.database.Reader(city_db) as reader:
            resp = reader.city(ip)
            result['city']    = resp.city.name or '-'
            result['country'] = f"{resp.country.name or '-'} ({resp.country.iso_code or '-'})"
    except Exception:
        pass
    try:
        with geoip2.database.Reader(asn_db) as reader:
            resp = reader.asn(ip)
            result['asn'] = f"AS{resp.autonomous_system_number}"
            result['org'] = resp.autonomous_system_organization or '-'
    except Exception:
        pass
    return result

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]}  [city_db_path] [asn_db_path]")
        sys.exit(1)

    city_db = sys.argv[2] if len(sys.argv) > 2 else '/var/lib/GeoIP/GeoLite2-City.mmdb'
    asn_db  = sys.argv[3] if len(sys.argv) > 3 else '/var/lib/GeoIP/GeoLite2-ASN.mmdb'

    ips = extract_ips(sys.argv[1])
    print(f"{'Hop':<4} {'IP':<18} {'Country':<30} {'City':<20} {'ASN':<12} {'Organization'}")
    print("-" * 110)
    for i, ip in enumerate(ips):
        info = query_geoip(ip, city_db, asn_db)
        print(f"{i+1:<4} {info['ip']:<18} {info['country']:<30} {info['city']:<20} {info['asn']:<12} {info['org']}")
```

如果 GeoIP 数据库不可用，可以使用在线 API 作为备选方案：

```
# 使用 ip-api.com 免费 API（每分钟 45 次限额）
curl -s "http://ip-api.com/json/203.0.113.200?fields=country,city,isp,org,as" | python3 -m json.tool
# 输出示例：
# {
#   "country": "Nigeria",
#   "city": "Lagos",
#   "isp": "MTN Nigeria",
#   "org": "",
#   "as": "AS29465 MTN Nigeria Communication Limited"
# }
```

## 六、SPF / DKIM / DMARC 认证结果聚合分析

`Authentication-Results`
头（
[RFC 8601](https://datatracker.ietf.org/doc/html/rfc8601)
）由接收方 MTA 在完成 SPF、DKIM、DMARC 验证后写入。以下脚本提取并聚合所有认证结果：

```
#!/usr/bin/env python3
"""auth_results.py — 提取并解析 Authentication-Results 头"""
import email, re, sys
from email import policy

def parse_auth_results(eml_path):
    with open(eml_path, 'rb') as f:
        msg = email.message_from_binary_file(f, policy=policy.default)

    auth_headers = msg.get_all('Authentication-Results') or []

    spf_status = dkim_status = dmarc_status = 'missing'
    spf_detail = dkim_detail = dmarc_detail = ''

    for ah in auth_headers:
        ah = ah.replace('\n', ' ').replace('\r', ' ')
        spf_m  = re.search(r'spf=(pass|fail|softfail|neutral|none|temperror|permerror)(?:\s+\S+[@\S]+)?', ah)
        dkim_m = re.search(r'dkim=(pass|fail|neutral|none|temperror|permerror)', ah)
        dmarc_m= re.search(r'dmarc=(pass|fail|bestguesspass|none|temperror|permerror)', ah)

        if spf_m and spf_status in ('missing','none'):
            spf_status = spf_m.group(1); spf_detail = spf_m.group(0)
        if dkim_m and dkim_status in ('missing','none'):
            dkim_status = dkim_m.group(1); dkim_detail = dkim_m.group(0)
        if dmarc_m and dmarc_status in ('missing','none'):
            dmarc_status = dmarc_m.group(1); dmarc_detail = dmarc_m.group(0)

    # 同时解析 DKIM-Signature 头
    dkim_sigs = msg.get_all('DKIM-Signature') or []
    dkim_domains = set()
    for ds in dkim_sigs:
        d_m = re.search(r'd=([^;]+)', ds.replace('\n',' '))
        if d_m: dkim_domains.add(d_m.group(1).strip())

    print("=== 认证结果汇总 ===")
    print(f"  SPF:   {spf_status.upper():<10} | {spf_detail}")
    print(f"  DKIM:  {dkim_status.upper():<10} | {dkim_detail}")
    print(f"  DMARC: {dmarc_status.upper():<10} | {dmarc_detail}")
    if dkim_domains:
        print(f"  DKIM 签名域: {', '.join(sorted(dkim_domains))}")

    # 综合判断
    if spf_status == 'fail' or dkim_status == 'fail' or dmarc_status == 'fail':
        print("\n[!] 告警：邮件认证失败，存在伪造风险")
    elif spf_status in ('softfail','neutral','none') and dkim_status in ('neutral','none'):
        print("\n[!] 注意：缺少有效认证，无法确认发件方身份")
    else:
        print("\n[✓] 认证通过")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} ")
        sys.exit(1)
    parse_auth_results(sys.argv[1])
```

当 DMARC 策略为
`p=reject`
却仍然投递成功时，必须检查
[RFC 8617 ARC（Authenticated Received Chain）](https://datatracker.ietf.org/doc/html/rfc8617)
头。ARC 为中间转发方（邮件列表、转发服务）提供了认证结果链式签名机制。如果 ARC 验证通过但 DMARC 失败，说明是合法转发；如果两者都失败，则确定是伪造。

## 七、时间戳异常检测

每跳
`Received`
头中的时间戳记录了该 MTA 接收邮件的时间。邮件传输正常情况下，时间戳应单调递增（从源到目标方向）。以下异常模式值得警惕：

七、时间戳异常检测

| 异常类型 | 描述 | 取证意义 |
| --- | --- | --- |
| 时间倒流 | 下游跳时间早于上游跳 | 可能有人为插入的伪造 Received 跳 |
| 时区不一致 | 相邻跳使用时区差异不合理（如从 +0800 跳到 -0500 再跳回 +0800） | 邮件路径地理上不合理 |
| 传输延迟异常 | 相邻两跳之间间隔数小时乃至数天 | 邮件被暂存、重放，或 MTA 时钟严重偏差 |
| 未来时间戳 | 任意一跳时间晚于分析时刻 | 发件方系统时钟错误，或人为构造 |
| Date 与首跳不匹配 | Date 头的时间与首跳 Received 时间相差过大 | Date 头被手动设置（常见于钓鱼邮件模板） |

```
#!/usr/bin/env python3
"""timeline_rebuild.py — 重建邮件传输时间线并检测异常"""
import email, re, sys
from email import policy
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime

MONTH_MAP = {
    'Jan':1,'Feb':2,'Mar':3,'Apr':4,'May':5,'Jun':6,
    'Jul':7,'Aug':8,'Sep':9,'Oct':10,'Nov':11,'Dec':12
}

def parse_received_ts(line):
    """解析 Received 头中的时间戳，含时区"""
    m = re.search(r';\s*(.+)$', line)
    if not m: return None, line[:80]
    ts_str = m.group(1).strip()
    # 去掉末尾的 (CST) 等冗余时区注释
    ts_str = re.sub(r'\s*\([A-Z]{3,4}\)\s*$', '', ts_str)
    # 替换 "\d+ ( UTC)" 格式
    ts_str = re.sub(r'\s*\(UTC\)', '', ts_str)
    try:
        dt = parsedate_to_datetime(ts_str)
        return dt, ts_str
    except Exception:
        pass
    # 手动解析常见格式: "Thu, 3 Jul 2025 14:22:17 +0800"
    m2 = re.search(
        r'(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4})\s+(\d{1,2}):(\d{2}):(\d{2})\s+([+-]\d{4})',
        ts_str, re.IGNORECASE)
    if m2:
        d, mon_s, y, h, mi, s, tz = m2.groups()
        mon = MONTH_MAP.get(mon_s[:3].title())
        if mon:
            tz_h, tz_m = int(tz[1:3]), int(tz[3:5])
            tz_sign = 1 if tz[0] == '+' else -1
            offset = timedelta(hours=tz_h * tz_sign, minutes=tz_m * tz_sign)
            tz_obj = timezone(offset)
            return datetime(int(y), mon, int(d), int(h), int(mi), int(s), tzinfo=tz_obj), ts_str
    return None, ts_str

def analyze(eml_path):
    with open(eml_path, 'rb') as f:
        msg = email.message_from_binary_file(f, policy=policy.default)

    received = msg.get_all('Received') or []
    # 从上到下是近→远，反向后才是源→目标
    timeline = []
    for line in reversed(received):
        dt, ts_str = parse_received_ts(line)
        ip_m = re.search(r'\[(\d+\.\d+\.\d+\.\d+)\]', line)
        by_m = re.search(r'by\s+(\S+)', line)
        timeline.append({
            'dt': dt, 'ts_str': ts_str,
            'ip': ip_m.group(1) if ip_m else '-',
            'by': by_m.group(1) if by_m else '-'
        })

    print("=== 传输时间线（源 → 目标）===")
    print(f"{'Hop':<5} {'时间 (UTC)':<30} {'IP/主机':<25} {'延迟':<10} {'标志'}")
    print("-" * 95)

    prev_dt = None
    anomalies = []
    for i, h in enumerate(timeline):
        dt = h['dt']
        ts_disp = dt.strftime('%Y-%m-%d %H:%M:%S %Z') if dt else h['ts_str']
        node = h['ip'] if h['ip'] != '-' else h['by']

        delta = ''
        flags = ''
        if dt and prev_dt:
            diff = dt - prev_dt
            delta = f"{diff.total_seconds():.0f}s"
            if diff.total_seconds() < -1:
                flags = '⚠ TIME_REVERSAL'
                anomalies.append(f"跳 {i+1}: 时间倒流 {delta}")
            elif diff.total_seconds() > 86400:
                flags = '⚠ LARGE_DELAY'
                anomalies.append(f"跳 {i+1}: 传输延迟 {delta}")

        print(f"{i+1:<5} {ts_disp:<30} {node:<25} {delta:<10} {flags}")
        if dt:
            prev_dt = dt

    # 对比 Date 头
    date_hdr = msg.get('Date', '')
    if date_hdr:
        try:
            date_dt = parsedate_to_datetime(date_hdr)
            first_dt = timeline[0]['dt'] if timeline else None
            if date_dt and first_dt:
                diff = (first_dt - date_dt).total_seconds()
                print(f"\n  Date 头时间:     {date_dt.strftime('%Y-%m-%d %H:%M:%S %Z')}")
                print(f"  首跳 Received:   {first_dt.strftime('%Y-%m-%d %H:%M:%S %Z')}")
                print(f"  Date → 首跳延迟: {diff:.0f}s", end='')
                if abs(diff) > 300:
                    print(' ⚠ 差异超过 5 分钟，Date 头可能被手动设置')
                else:
                    print()
        except Exception:
            pass

    if anomalies:
        print(f"\n[!] 发现 {len(anomalies)} 个时间异常：")
        for a in anomalies: print(f"    • {a}")
    else:
        print("\n[✓] 时间线无异常")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} ")
        sys.exit(1)
    analyze(sys.argv[1])
```

## 八、Message-ID 与 MIME Boundary 取证

### 8.1 Message-ID 包含的信息

[RFC 5322 §3.6.4](https://datatracker.ietf.org/doc/html/rfc5322#section-3.6.4)
规定每条消息应有一个全局唯一的 Message-ID。生成 Message-ID 的通常是首跳 MTA 或 MUA。其格式一般为：

```
Message-ID:
```

右侧域名揭示生成该消息的系统。如果 Message-ID 域与 From 域不一致，意味着邮件可能由一个系统生成但标注了另一个系统的发件人：

```
# 提取并对比 Message-ID 域
python3 -c "
import email, sys
from email import policy
msg = email.message_from_binary_file(open(sys.argv[1],'rb'), policy=policy.default)
mid = msg.get('Message-ID','')
domain = mid.split('@')[-1].rstrip('>') if '@' in mid else '-'
print(f'Message-ID 域: {domain}')
" file.eml
```

### 8.2 MIME Boundary 的指纹价值

MIME multipart 邮件的 boundary 字符串由生成邮件的软件构造。不同的邮件客户端和发送库有各自的 boundary 生成模式。常见模式包括：

8.2 MIME Boundary 的指纹价值

| 模式 | 关联软件 |
| --- | --- |
| `----=_NextPart_XXX_YYY` | Microsoft Outlook / Exchange |
| `------------[0-9A-F]{24}` | Mozilla Thunderbird |
| `Apple-Mail=` 前缀 | Apple Mail |
| 32 位十六进制随机串 | Python email / PHP mailer |
| 固定字符串模式 | 特定钓鱼工具包（可做指纹） |

如果一封声称来自 iPhone 的邮件其 MIME boundary 却是
`------------[0-9A-F]{24}`
模式（Thunderbird 特征），则发件人关于发送环境的描述不可信。同一攻击活动中多封邮件的 boundary 模式一致，可作为关联分析的依据。

## 九、自动化取证脚本：从 .eml 到可视化时间线

以下脚本整合了前述所有分析模块，输入为 .eml 文件，输出为结构化 JSON 取证报告：

```
#!/usr/bin/env python3
"""email_forensics.py — 邮件头自动化取证分析，输出 JSON 报告"""
import email, re, sys, json
from email import policy
from email.utils import parseaddr, getaddresses, parsedate_to_datetime
from datetime import datetime, timezone, timedelta

MONTH_MAP = {
    'Jan':1,'Feb':2,'Mar':3,'Apr':4,'May':5,'Jun':6,
    'Jul':7,'Aug':8,'Sep':9,'Oct':10,'Nov':11,'Dec':12
}

def parse_received_ts(line):
    m = re.search(r';\s*(.+)$', line)
    if not m: return None
    ts_str = re.sub(r'\s*\([A-Z]{3,4}\)\s*$', '', m.group(1).strip())
    ts_str = re.sub(r'\s*\(UTC\)', '', ts_str)
    try:
        return parsedate_to_datetime(ts_str)
    except Exception:
        pass
    m2 = re.search(
        r'(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4})\s+(\d{1,2}):(\d{2}):(\d{2})\s+([+-]\d{4})',
        ts_str, re.IGNORECASE)
    if m2:
        d, mon_s, y, h, mi, s, tz = m2.groups()
        mon = MONTH_MAP.get(mon_s[:3].title())
        if mon:
            tz_h, tz_m = int(tz[1:3]), int(tz[3:5])
            sign = 1 if tz[0] == '+' else -1
            offset = timedelta(hours=tz_h*sign, minutes=tz_m*sign)
            return datetime(int(y), mon, int(d), int(h), int(mi), int(s), tzinfo=timezone(offset))
    return None

def forensic_report(eml_path):
    with open(eml_path, 'rb') as f:
        msg = email.message_from_binary_file(f, policy=policy.default)

    report = {
        'file': eml_path,
        'analysis_time': datetime.now(timezone.utc).isoformat(),
        'headers': {},
        'received_chain': [],
        'auth': {},
        'anomalies': []
    }

    # 关键头部
    for hdr in ['From','To','Cc','Subject','Date','Message-ID',
                'Return-Path','Reply-To','In-Reply-To','References','X-Mailer']:
        val = msg.get(hdr)
        if val:
            report['headers'][hdr] = val.replace('\n',' ').replace('\r','')

    # Received 链
    received = msg.get_all('Received') or []
    prev_dt = None
    for i, line in enumerate(reversed(received)):
        hop = {}
        for pat, key in [('from\s+(\S+)','ehlo'), ('by\s+(\S+)','by'),
                         ('\[(\d+\.\d+\.\d+\.\d+)\]','ip'),
                         ('with\s+(\S+)','protocol'), ('id\s+(\S+)','queue_id'),
                         ('for\s+(\S+@\S+)','envelope_to')]:
            m = re.search(pat, line)
            if m: hop[key] = m.group(1).rstrip()
        dt = parse_received_ts(line)
        hop['timestamp'] = dt.isoformat() if dt else None
        if dt and prev_dt:
            hop['delay_seconds'] = (dt - prev_dt).total_seconds()
        elif dt:
            hop['delay_seconds'] = 0
        report['received_chain'].append(hop)
        prev_dt = dt

    # 认证结果
    auth_headers = msg.get_all('Authentication-Results') or []
    for ah in auth_headers:
        ah = ah.replace('\n',' ').replace('\r',' ')
        for key in ['spf','dkim','dmarc']:
            m = re.search(rf'{key}=(pass|fail|softfail|neutral|none|temperror|permerror)', ah)
            if m:
                report['auth'][key] = m.group(1)

    # DKIM 签名域
    dkim_sigs = msg.get_all('DKIM-Signature') or []
    dkim_domains = set()
    for ds in dkim_sigs:
        d_m = re.search(r'd=([^;]+)', ds.replace('\n',' '))
        if d_m: dkim_domains.add(d_m.group(1).strip())
    report['dkim_domains'] = sorted(dkim_domains)

    # 异常检测
    a = report['anomalies']

    # Reply-To 劫持
    _, from_addr = parseaddr(msg.get('From',''))
    from_domain = from_addr.split('@')[-1] if '@' in from_addr else ''
    for _, addr in getaddresses([msg.get('Reply-To','')]):
        rt_domain = addr.split('@')[-1] if '@' in addr else ''
        if rt_domain and from_domain and rt_domain != from_domain:
            a.append({
                'type': 'reply_to_mismatch',
                'severity': 'high',
                'detail': f'Reply-To 域 {rt_domain} ≠ From 域 {from_domain}'
            })

    # 时间异常
    chain = report['received_chain']
    for i in range(1, len(chain)):
        if chain[i]['delay_seconds'] is not None and chain[i]['delay_seconds'] < -1:
            a.append({
                'type': 'time_reversal',
                'severity': 'critical',
                'detail': f'跳 {i+1} 时间早于跳 {i}，差 {chain[i]["delay_seconds"]:.0f}s'
            })

    # 相邻跳不匹配
    for i in range(1, len(chain)):
        prev_by = chain[i-1].get('by','').lower()
        cur_from = chain[i].get('ehlo','').lower()
        if prev_by and cur_from and prev_by not in cur_from and cur_from not in prev_by:
            a.append({
                'type': 'hop_mismatch',
                'severity': 'critical',
                'detail': f'跳 {i} by={chain[i-1]["by"]} ≠ 跳 {i+1} from={chain[i]["ehlo"]}'
            })

    # 认证失败
    for key in ['spf','dkim','dmarc']:
        if report['auth'].get(key) == 'fail':
            a.append({
                'type': f'{key}_fail',
                'severity': 'high',
                'detail': f'{key.upper()} 验证失败'
            })

    report['risk_level'] = 'low'
    severities = [x['severity'] for x in a]
    if 'critical' in severities: report['risk_level'] = 'critical'
    elif 'high' in severities:   report['risk_level'] = 'high'
    elif 'medium' in severities: report['risk_level'] = 'medium'

    return report

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]}  [--pretty]")
        sys.exit(1)
    report = forensic_report(sys.argv[1])
    indent = 2 if '--pretty' in sys.argv else None
    print(json.dumps(report, ensure_ascii=False, indent=indent, default=str))
```

运行示例：

```
$ python3 email_forensics.py suspicious.eml --pretty
```

输出为完整 JSON，包含头部摘要、Received 链每跳信息、认证结果、异常列表及综合风险等级。

## 十、证据固定与取证报告模板

### 10.1 证据固定流程

在处理邮件安全事件时，证据固定的时效性极为关键。邮件服务端日志（尤其是 SMTP 会话日志）通常有轮转周期（7-30 天），必须在窗口期内完成提取。

```
# 从主流 MTA 提取特定 Message-ID 的传输日志
# Postfix
grep "4xV7qK2nRtz9sD" /var/log/mail.log

# Exim
exigrep "1tXyZ-0008Ab-Cd" /var/log/exim4/mainlog

# Microsoft Exchange
Get-MessageTrackingLog -MessageId "" \
  | Select Timestamp, EventId, Source, Sender, Recipients \
  | Format-Table -AutoSize
```

**M3AAWG Anti-Abuse Best Practices**

（消息传递、恶意软件与移动反滥用工作组最佳实践）建议在收到滥用报告后 72 小时内完成日志保全，并保留原始 .eml 文件的 SHA-256 哈希值作为证据链的一部分。

### 10.2 取证报告模板

以下模板可直接用于邮件安全事件的内部分析与外部报送：

```
================================================================
        邮件取证分析报告
================================================================
报告编号:  IR-YYYYMMDD-NNN
分析时间:  2025-07-04 14:30:00 UTC
分析师:    [姓名]
原始证据:  suspicious.eml  (SHA-256: a1b2c3...)

一、邮件基本信息
  From:        "CEO" 
  To:          finance@company.com
  Subject:     Urgent Wire Transfer
  Date:        2025-07-03 09:15:23 +0000
  Message-ID:  

二、Received 链 (共 3 跳)
  跳1: 198.51.100.77 (ESMTP) — sender.mta.org
  跳2: 203.0.113.45 (ESMTPS) — mail.example.com
  跳3: 192.0.2.10 (LMTP) — mx.recipient.com
  首跳 IP: 198.51.100.77

三、认证结果
  SPF:   NEUTRAL
  DKIM:  NONE (未签名)
  DMARC: NONE (无策略)

四、异常指标
  [!] CRITICAL — Reply-To 劫持: reply@attacker-gmail.com
  [!] CRITICAL — 首跳 IP GeoIP: Lagos, NG (vs 声称的 New York, US)
  [!] HIGH — Message-ID 域 compromised-server.net ≠ From 域 company.com

五、首跳 IP 信息
  IP:       198.51.100.77
  Country:  NG (Nigeria)
  ASN:      AS29465
  Org:      MTN Nigeria
  已知恶意: 否 (AbuseIPDB 信任分: 未查询)

六、处置建议
  1. 确认收件人是否已执行邮件中的转账请求
  2. 重置 From 地址对应邮箱的凭据
  3. 将首跳 IP 加入邮件网关黑名单
  4. 对全公司通报 CEO 冒充攻击特征

七、证据链
  原始 .eml 文件:      IR-20250704-001.eml
  SHA-256:            a1b2c3d4e5f6...
  保存路径:            /evidence/2025-Q3/
  日志提取时间:        2025-07-04 14:30 UTC
  日志保存路径:        /evidence/2025-Q3/mailog-20250703.txt
================================================================
```

## 十一、MIME 解析与正文证据提取

虽然邮件头是主要取证对象，但正文（特别是 HTML 部分）也可能包含钓鱼链接、跟踪像素和恶意附件。以下命令提取正文中的全部 URL：

```
# 提取 .eml 正文中所有 URL
python3 -c "
import email, re, sys
from email import policy
msg = email.message_from_binary_file(open(sys.argv[1],'rb'), policy=policy.default)
for part in msg.walk():
    if part.get_content_type() in ('text/plain','text/html'):
        try:
            body = part.get_content()
            urls = re.findall(r'https?://[^\s\"\'<>]+', str(body))
            for u in urls: print(u)
        except: pass
" suspicious.eml | sort -u
```

对于跟踪像素（常为 1×1 透明图片），可以检查 HTML 部分中引用的外部图片：

```
# 提取 HTML 中的外部图片引用（潜在跟踪像素）
python3 -c "
import email, re, sys
from email import policy
msg = email.message_from_binary_file(open(sys.argv[1],'rb'), policy=policy.default)
for part in msg.walk():
    if part.get_content_type() == 'text/html':
        try:
            body = str(part.get_content())
            imgs = re.findall(r']+src=[\"\']([^\"\']+)[\"\']', body)
            for img in imgs:
                if img.startswith('http'):
                    print(f'[*] 外部图片: {img}')
        except: pass
" suspicious.eml
```

## 十二、参考规范与延伸阅读

* [RFC 5321](https://datatracker.ietf.org/doc/html/rfc5321)
  — Simple Mail Transfer Protocol（SMTP Received 定义）
* [RFC 5322](https://datatracker.ietf.org/doc/html/rfc5322)
  — Internet Message Format（邮件格式、Message-ID 定义）
* [RFC 5965](https://datatracker.ietf.org/doc/html/rfc5965)
  — An Extensible Format for Email Feedback Reports（ARF 滥用反馈格式）
* [RFC 8617](https://datatracker.ietf.org/doc/html/rfc8617)
  — The Authenticated Received Chain (ARC) Protocol（转发链认证）
* [RFC 8601](https://datatracker.ietf.org/doc/html/rfc8601)
  — Message Header Field for Indicating Message Authentication Status
* [MITRE ATT&CK T1566](https://attack.mitre.org/techniques/T1566/)
  — Phishing（社工邮件投递技术分类）
* [M3AAWG](https://www.m3aawg.org/)
  — Messaging, Malware and Mobile Anti-Abuse Working Group Best Practices

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-forensics-header-analysis.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
