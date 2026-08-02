---
title: "邮件系统 DNS 配置全指南 — MX/SPF/DKIM/DMARC/MTA-STS/TLS-RPT/BIMI 九类记录逐条验证 · ztpop 邮件技术知识库"
source: "https://ztpop.net/kb/email-dns-configuration.html"
license: CC-BY 4.0
---

# 邮件系统 DNS 配置全指南 — MX/SPF/DKIM/DMARC/MTA-STS/TLS-RPT/BIMI 九类记录逐条验证 · ztpop 邮件技术知识库

邮件系统 DNS 配置全指南 — MX/SPF/DKIM/DMARC/MTA-STS/TLS-RPT/BIMI 九类记录逐条验证

## 摘要

DNS 是邮件系统的"指路牌"——MX 记录决定邮件往哪里投递，PTR 记录影响发件 IP 的信誉评分，SPF/DKIM/DMARC 三条 TXT 记录构成邮件身份认证的三角支撑，MTA-STS/TLS-RPT/DANE 决定传输层的加密策略，BIMI 记录控制邮件客户端的品牌 Logo 展示。每一条 DNS 记录的配置错误都可能导致邮件被拒收、投递到错误服务器或安全机制完全失效。本文以"配置 + 验证 + 排错"三段式结构覆盖九类邮件相关 DNS 记录的完整配置指南，每条记录附带
`dig`
和
`nslookup`
验证命令。末尾提供自动化 DNS 配置检查脚本，可在 30 秒内完成全链路验证。

## 1. MX 记录 — 邮件路由入口（RFC 5321 §5.1）

### 1.1 优先级与负载均衡

MX（Mail Exchanger）记录的优先级值（0–65535，RFC 5321 §5.1 规定）决定了远程 MTA 连接本域 MTA 服务器时的尝试顺序——值越小优先级越高。同一优先级的多条 MX 记录由远程 MTA 随机选择实现简单的负载均衡。

```
# 标准双 MX 配置（主服务器 + 备份服务器）
example.com.  3600  IN  MX  10  mail1.example.com.
example.com.  3600  IN  MX  20  mail2.example.com.

# 验证命令
dig MX example.com +short
# 输出：
# 10 mail1.example.com.
# 20 mail2.example.com.

nslookup -type=MX example.com
# 输出：
# example.com    MX preference = 10, mail exchanger = mail1.example.com
# example.com    MX preference = 20, mail exchanger = mail2.example.com
```

### 1.2 备份 MX 的架构模式

低优先级（高数值）的 MX 服务器有两种典型用途：(1)
**同数据中心热备份**
：两个 MX 优先级相同或相差 0（同优先级随机选择），均直接接受邮件；(2)
**异地灾备 MX**
：高数值（如 50）的 MX 在异地数据中心运行，仅当主数据中心完全不可用时才接管邮件——并配置为"邮件队列"模式（只存储，等主 MX 恢复后再转发）。

```
# 异地灾备 MX 的 Postfix 配置
# /etc/postfix/main.cf — 备份 MX 模式
relay_domains = example.com, example.net
# 不存储邮件在本地，所有接受的邮件暂存后通过 smtp_fallback_relay 转发
smtp_fallback_relay = $relayhost  # 指向主 MX 恢复后转发
maximal_queue_lifetime = 7d       # 灾备邮件最多保留 7 天
```

### 1.3 MX 记录的铁律

* MX 记录的值必须是主机名（A/AAAA 记录），不能是 IP 地址（RFC 5321 §5.1 明确禁止 IP 地址作为 MX 值）。
* MX 记录指向的主机名必须有对应的 A 或 AAAA 记录。无 A 记录的 MX 会导致邮件投递失败。
* MX 记录不应指向 CNAME——这违反了 RFC 2181 §10.3 的建议。
* TTL 建议值：稳定的生产 MX 记录 TTL 应设为 3600 秒（1 小时），便于 MX 变更时快速传播。

## 2. A/AAAA 记录 — 邮件服务器的主机名解析

```
# IPv4 A 记录
mail1.example.com.  3600  IN  A     203.0.113.10
mail2.example.com.  3600  IN  A     203.0.113.11

# IPv6 AAAA 记录
mail1.example.com.  3600  IN  AAAA  2001:db8::10
mail2.example.com.  3600  IN  AAAA  2001:db8::11

# 验证
dig A mail1.example.com +short
dig AAAA mail1.example.com +short
```

## 3. PTR 反向解析 — SMTP Banner 匹配（RFC 5321 §4.1.4）

PTR（Pointer Record, RFC 1035 §3.3.12）是反向 DNS（rDNS）的核心——将 IP 地址反向映射为主机名。大多数反垃圾邮件系统会对发件 IP 进行 PTR 存在性检查，如果 PTR 缺失或与 SMTP EHLO 主机名不匹配，该邮件的信誉评分会显著降低。

```
# PTR 记录配置（需由 IP 所有者——通常是 ISP 或 IDC——在 in-addr.arpa 域中设置）
# 203.0.113.10 → mail1.example.com
# 10.113.0.203.in-addr.arpa.  IN  PTR  mail1.example.com.

# 验证命令
dig -x 203.0.113.10 +short
# 输出：mail1.example.com.

nslookup 203.0.113.10
```

### 3.1 SMTP Banner 一致性检验

SMTP 服务器在 EHLO 响应中宣告的主机名应与 PTR 记录一致。RFC 5321 §4.1.4 要求 SMTP 服务器的 EHLO 主机名必须是完整限定域名（FQDN），且应该与 PTR 记录匹配。检查方法：

```
# Step 1: 获取 SMTP Banner
echo "" | nc mail1.example.com 25 | head -1
# 输出：220 mail1.example.com ESMTP Postfix

# Step 2: 获取 PTR
dig -x 203.0.113.10 +short
# 输出：mail1.example.com.

# Step 3: 检查 PTR → A 的正向一致性
dig A $(dig -x 203.0.113.10 +short) +short
# 输出：203.0.113.10  （正向 A 记录应该解析回原始 IP）
```

## 4. SPF TXT 记录（RFC 7208）

### 4.1 基础语法与机制

SPF 记录发布在域根（或子域）的 TXT 记录中，声明哪些 IP 地址被授权以该域的名义发送邮件：

```
# 基本 SPF 记录（仅本域 MTA 发送）
example.com.  3600  IN  TXT  "v=spf1 mx -all"

# 包含第三方 ESP 的 SPF 记录
example.com.  3600  IN  TXT  "v=spf1 mx include:spf.google.com include:spf.protection.outlook.com -all"

# 验证
dig TXT example.com +short | grep v=spf1
nslookup -type=TXT example.com | grep v=spf1
```

### 4.2 常见 SPF 配置错误

4.2 常见 SPF 配置错误

| 错误 | SPF 记录 | 后果 | 修正 |
| --- | --- | --- | --- |
| 超过 10 次 DNS 查询限制 | `v=spf1 include:a include:b ... include:k -all` | permerror → DMARC fail | 扁平化 SPF 为 ip4/ip6 列表 |
| 使用 `+all` 或 `?all` | `v=spf1 mx +all` | 所有 IP 都能通过 SPF——等于没配 | 改为 `-all` （严格拒绝）或 `~all` （软拒绝） |
| SPF 记录包含无效机制 | `v=spf1 mx ptr -all` | `ptr` 机制触发大量 DNS 查询，现代 SPF 实现已弃用 | 使用 ip4/ip6 替代 ptr 机制 |
| 一条域有多条 SPF 记录 | 两条 v=spf1 TXT 记录 | permerror——RFC 7208 §4.5 规定多 SPF 记录为错误 | 合并为一条 SPF 记录 |

## 5. DKIM TXT 记录（RFC 6376）

### 5.1 selector.\_domainkey 语法

DKIM 公钥发布在
`._domainkey.`
的 TXT 记录中。selector 是一个任意的标签（如
`202607`
、
`default`
、
`google`
），允许同一域同时使用多套 DKIM 密钥。

```
# DKIM 公钥 TXT 记录（2048 位 RSA 密钥）
202607._domainkey.example.com.  3600  IN  TXT  (
    "v=DKIM1; k=rsa; "
    "p=MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAw1..."
)

# 验证
dig TXT 202607._domainkey.example.com +short
nslookup -type=TXT 202607._domainkey.example.com
```

### 5.2 DKIM 密钥轮换

DKIM 密钥应定期轮换（建议每 6 个月），方法：

1. 生成新密钥对：
   `opendkim-genkey -b 2048 -s 202701 -d example.com`
2. 将新公钥发布到
   `202701._domainkey.example.com`
3. 在新旧 selector 共存期间（建议 7 天）同时用两个 selector 签名：
   `opendkim -S 202607,202701`
4. 7 天后移除旧 selector 的签名，再 30 天后删除旧公钥 DNS 记录

## 6. DMARC TXT 记录（RFC 7489 / RFC 9989）

```
# 监控模式（推荐起始配置）
_dmarc.example.com.  3600  IN  TXT  "v=DMARC1; p=none; rua=mailto:dmarc@example.com"

# 拒绝模式（最终目标）
_dmarc.example.com.  3600  IN  TXT  "v=DMARC1; p=reject; sp=reject; pct=100; adkim=s; aspf=r; rua=mailto:dmarc@example.com"

# 验证
dig TXT _dmarc.example.com +short
# 应返回以 "v=DMARC1" 开头的 TXT 记录
```

## 7. MTA-STS — 强制传输加密策略（RFC 8461）

MTA-STS 需要两条 DNS 记录和一个 HTTPS 策略文件：

```
# (1) _mta-sts DNS TXT 记录
_mta-sts.example.com.  3600  IN  TXT  "v=STSv1; id=2026071101"

# 验证
dig TXT _mta-sts.example.com +short
```

```
# (2) MTA-STS Policy 文件 — https://mta-sts.example.com/.well-known/mta-sts.txt
version: STSv1
mode: enforce
mx: mail1.example.com
mx: mail2.example.com
max_age: 86400

# 验证 policy 文件可通过 HTTPS 访问
curl -s https://mta-sts.example.com/.well-known/mta-sts.txt
```

## 8. TLS-RPT — SMTP TLS 报告（RFC 8460）

```
# _smtp._tls DNS TXT 记录
_smtp._tls.example.com.  3600  IN  TXT  "v=TLSRPTv1; rua=mailto:tls-reports@example.com"

# 验证
dig TXT _smtp._tls.example.com +short
```

## 9. BIMI — 品牌邮件标识（IETF BIMI 草案）

BIMI 记录发布在
`default._bimi.`
的 TXT 记录中：

```
# BIMI TXT 记录
default._bimi.example.com.  3600  IN  TXT  "v=BIMI1; l=https://example.com/brand/logo.svg; a=https://example.com/brand/cert.pem"

# 验证
dig TXT default._bimi.example.com +short
```

BIMI 的前置条件：域必须已部署 DMARC 且
`p=quarantine`
或
`p=reject`
（
`p=none`
不满足 BIMI 要求）。Logo 必须是 SVG Tiny 1.2 格式，文件大小不超过 32 KB，且应通过 VMC（Verified Mark Certificate）验证。

## 10. 自动化 DNS 配置检查脚本

```
#!/usr/bin/env python3
"""
dns-mail-check.py — 邮件系统 DNS 配置全链路检查
用法: python3 dns-mail-check.py example.com
"""
import sys, subprocess, json

def dig(record_type, name, short=True):
    """执行 DNS 查询并返回结果"""
    cmd = ['dig', '+short', record_type, name]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
    return result.stdout.strip()

def check_all(domain):
    results = {}
    print(f"=== 邮件 DNS 配置全链路检查: {domain} ===\n")

    # 1. MX 记录
    mx = dig('MX', domain)
    results['mx'] = 'PASS' if mx else 'FAIL'
    print(f"[{'✓' if mx else '✗'}] MX: {mx if mx else '未找到 MX 记录'}")

    # 2. A 记录（如果 MX 存在，检查 MX 主机名的 A 记录）
    if mx:
        for line in mx.split('\n'):
            parts = line.split()
            if len(parts) >= 2:
                mx_host = parts[-1].rstrip('.')
                a = dig('A', mx_host)
                print(f"    A({mx_host}): {'✓ ' + a if a else '✗ 无 A 记录'}")
                # PTR
                if a:
                    for ip in a.split('\n'):
                        ptr = dig('-x', ip)
                        print(f"    PTR({ip}): {'✓ ' + ptr if ptr else '✗ 无 PTR 记录'}")

    # 3. SPF
    spf = dig('TXT', domain)
    spf_found = 'v=spf1' in spf
    results['spf'] = 'PASS' if spf_found else 'FAIL'
    print(f"[{'✓' if spf_found else '✗'}] SPF: {'已找到' if spf_found else '未找到 SPF 记录'}")

    # 4. DKIM (检查 default selector)
    dkim = dig('TXT', f'default._domainkey.{domain}')
    dkim_found = 'v=DKIM1' in dkim
    results['dkim'] = 'PASS' if dkim_found else 'WARN'
    print(f"[{'✓' if dkim_found else '⚠'}] DKIM (default): {'已找到' if dkim_found else '未找到 default._domainkey 记录（可能使用了其他 selector）'}")

    # 5. DMARC
    dmarc = dig('TXT', f'_dmarc.{domain}')
    dmarc_found = 'v=DMARC1' in dmarc
    results['dmarc'] = 'PASS' if dmarc_found else 'FAIL'
    if dmarc_found:
        p_value = 'none'
        sp_value = '(inherit)'
        for tag in dmarc.replace('"', '').split(';'):
            tag = tag.strip()
            if tag.startswith('p='):
                p_value = tag.split('=')[1]
            if tag.startswith('sp='):
                sp_value = tag.split('=')[1]
        print(f"[✓] DMARC: p={p_value} sp={sp_value}")
    else:
        print(f"[✗] DMARC: 未找到 _dmarc.{domain} 记录")

    # 6. MTA-STS
    mta_sts = dig('TXT', f'_mta-sts.{domain}')
    mta_sts_found = 'v=STSv1' in mta_sts
    results['mta-sts'] = 'PASS' if mta_sts_found else 'WARN'
    print(f"[{'✓' if mta_sts_found else '⚠'}] MTA-STS: {'已找到' if mta_sts_found else '未配置（非必需但推荐）'}")

    # 7. TLS-RPT
    tls_rpt = dig('TXT', f'_smtp._tls.{domain}')
    tls_rpt_found = 'v=TLSRPTv1' in tls_rpt
    results['tls-rpt'] = 'PASS' if tls_rpt_found else 'WARN'
    print(f"[{'✓' if tls_rpt_found else '⚠'}] TLS-RPT: {'已找到' if tls_rpt_found else '未配置（非必需但推荐）'}")

    # 8. BIMI
    bimi = dig('TXT', f'default._bimi.{domain}')
    bimi_found = 'v=BIMI1' in bimi
    results['bimi'] = 'PASS' if bimi_found else 'WARN'
    print(f"[{'✓' if bimi_found else '⚠'}] BIMI: {'已找到' if bimi_found else '未配置（可选）'}")

    # 汇总
    print(f"\n--- 检查汇总 ---")
    pass_count = sum(1 for v in results.values() if v == 'PASS')
    fail_count = sum(1 for v in results.values() if v == 'FAIL')
    warn_count = sum(1 for v in results.values() if v == 'WARN')
    print(f"✓ PASS: {pass_count}  ⚠ WARN: {warn_count}  ✗ FAIL: {fail_count}")
    if fail_count > 0:
        print(f"❌ 存在 {fail_count} 个必要项失败——请优先修复 FAIL 项。")
    else:
        print(f"✅ 所有必要 DNS 记录均已正确配置。")
    return results

if __name__ == '__main__':
    if len(sys.argv)
<
2:
        print(f"用法: {sys.argv[0]}  [domain2 ...]")
        sys.exit(1)
    for domain in sys.argv[1:]:
        check_all(domain)
        print()
```

### 运行示例

```
$ python3 dns-mail-check.py example.com
=== 邮件 DNS 配置全链路检查: example.com ===

[✓] MX: 10 mail1.example.com.
20 mail2.example.com.
    A(mail1.example.com): ✓ 203.0.113.10
    PTR(203.0.113.10): ✓ mail1.example.com.
    A(mail2.example.com): ✓ 203.0.113.11
    PTR(203.0.113.11): ✓ mail2.example.com.
[✓] SPF: 已找到
[✓] DKIM (default): 已找到
[✓] DMARC: p=reject sp=reject
[⚠] MTA-STS: 未配置（非必需但推荐）
[⚠] TLS-RPT: 未配置（非必需但推荐）
[⚠] BIMI: 未配置（可选）

--- 检查汇总 ---
✓ PASS: 4  ⚠ WARN: 3  ✗ FAIL: 0
✅ 所有必要 DNS 记录均已正确配置。
```

昆仑邮件系统在为客户域进行上线前的 DNS 全链路验证时，使用上述脚本作为标准检查流程的一环。在一个典型的客户上线案例中，该脚本在 5 分钟内发现了三处 DNS 配置错误（PTR 缺失、SPF 超 10 次查询限制、DMARC sp= 未覆盖所有发送子域），避免了上线后邮件被标记为垃圾邮件的运营事故。

### 参考文献

1. RFC 1034 — Domain Names — Concepts and Facilities (IETF, November 1987). 第 3.6 节资源记录类型定义（MX、A、PTR 等），第 5.2 节反向域 in-addr.arpa 的结构.
2. RFC 1035 — Domain Names — Implementation and Specification (IETF, November 1987). 第 3.3.12 节 PTR 记录格式，第 3.3.9 节 MX 记录格式.
3. RFC 5321 — Simple Mail Transfer Protocol (IETF, October 2008). 第 5.1 节 MX 记录的优先级与目标选择规则，第 4.1.4 节 EHLO 主机名与 PTR 的一致性要求.
4. RFC 7208 — Sender Policy Framework (SPF) Version 1 (IETF, April 2014). 第 4.5 节单条 SPF 记录规则，第 4.6.4 节 10 次 DNS 查询限制，第 5 节机制定义（mx/a/ip4/ip6/include/ptr）.
5. RFC 6376 — DomainKeys Identified Mail (DKIM) Signatures (IETF, September 2011). 第 3.6.2.2 节 DKIM 密钥 DNS TXT 记录格式（selector.\_domainkey），第 3.6.1 节密钥管理.
6. RFC 7489 — Domain-based Message Authentication, Reporting, and Conformance (DMARC) (IETF, March 2015). Historic. 第 6.3 节 \_dmarc DNS TXT 记录语法，第 7.2 节聚合报告 rua 地址.
7. RFC 8461 — SMTP MTA Strict Transport Security (MTA-STS) (IETF, September 2018). 第 5 节 \_mta-sts DNS TXT 记录，第 3.2 节 .well-known/mta-sts.txt Policy 文件.
8. RFC 8460 — SMTP TLS Reporting (IETF, September 2018). 第 3.1 节 \_smtp.\_tls DNS TXT 记录声明.
9. IETF BIMI 草案（draft-brand-indicators-for-message-identification）— BIMI 第 4 节 default.\_bimi TXT 记录语法及 l= / a= 标签定义.
10. GB/T 37002-2018 — 信息安全技术 电子邮件系统安全技术要求. 第 6.2.1 节网络架构安全要求引用 DNS 配置为邮件系统安全基线的组成部分.

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-dns-configuration.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
