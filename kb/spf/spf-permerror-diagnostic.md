---
title: "SPF PermError 完全诊断手册：10次DNS查询限制、CNAME解析失败、redirect循环"
source: "https://ztpop.net/kb/spf-permerror-diagnostic.html"
license: CC-BY 4.0
---

# SPF PermError 完全诊断手册：10次DNS查询限制、CNAME解析失败、redirect循环

## 1. PermError 与 SPF fail 的本质区别

| 判断 | 含义 | 示例 | 结果宏 |
| --- | --- | --- | --- |
| pass | 发件源IP匹配授权规则 | IP在ip4范围内 | + |
| fail | 发件源IP在~all或-all范围内被明确拒绝 | IP不在任何授权 | - |
| softfail | 弱否定（建议标记但不拒绝） | ~all匹配 | ~ |
| neutral | 无结论 | ?all | ? |
| **permerror** | **记录本身无法解析** | 语法错误、查询超限 | **N/A（中断检查）** |
| temperror | DNS临时故障 | SERVFAIL | N/A（可重试） |

重要区别：PermError与temperror不同——temperror是临时的（DNS临时故障），应重试；PermError是永久的（记录配置错误），重试也无法解决。RFC 7208 §8规定，如果SPF检查因PermError提前终止，整个SPF判定的结果就是permerror [1]。

PermError对DMARC的"第二次影响"：DMARC（RFC 7489）要求SPF的对齐函数使用SPF验证结果。如果SPF返回permerror，DMARC处理规则设定为"SPF未完成验证，视为未对齐"（RFC 7489 §3.1.1）[2]。如果此时DKIM也为fail（或未签名），DMARC判定就是fail——即使发件方实际上是合法的。

## 2. 七类PermError根因与诊断

### 2.1 10次DNS查询限制突破

**根因**：RFC 7208 §4.6.4限制每次SPF验证的总DNS查询为10次。每次`include`、`a`、`mx`、`ptr`和`exists`机制都会触发DNS查询；`redirect`机制算一次。特别注意：同一域名的`include`链必须去重（重复include域只算一次查询），但重复的`ip4`/`ip6`不算查询。

```
# 诊断方法1：使用spf-tools解析查询次数
pip3 install spf-query
spf-query --domain example.com --print-lookups
# 输出：
# include:spf.protection.outlook.com → 3次
# include:_spf.google.com → 4次
# include:spf.mailspamprotection.com → 3次
# include:spf.example.net → 失败（超限）
# 总计：10次（已达限制！）

# 诊断方法2：dnspython实时检查
python3 << 'PYEOF'
import dns.resolver

def check_spf_lookups(domain, depth=0, seen=None):
    if seen is None:
        seen = set()
    if depth > 10:
        return f"ERROR: exceeds 10 lookups (depth={depth})"
    try:
        answers = dns.resolver.resolve(domain, 'TXT')
        for rdata in answers:
            txt = rdata.to_text()
            if 'v=spf1' in txt:
                for word in txt.split():
                    if word.startswith('include:'):
                        inc = word.split(':', 1)[1]
                        if inc not in seen:
                            seen.add(inc)
                            res = check_spf_lookups(inc, depth+1, seen)
                            if 'ERROR' in str(res):
                                return res
        return f"OK ({len(seen)} lookups)"
    except Exception as e:
        return f"ERROR: {e}"

print(check_spf_lookups("example.com"))
PYEOF
```

### 2.2 CNAME解析失败（最常见的NXD）

**根因**：SPF记录要求以DNS TXT记录形式存在于域名的TXT记录中。CNAME记录指向另一个域名的TXT记录在理论上可行但实际中常因CNAME与其它记录类型的互斥问题导致NXD（不存在的域名返回NXDOMAIN）。RFC 7208 §4.6.3明确规定：解析SPF记录时不执行CNAME跟随 [1]。

```
# 诊断
dig TXT example.com | grep v=spf1
# 如果返回CNAME而非TXT：
dig CNAME example.com
# example.com.  CNAME  alias.example.com.

# 修复：将CNAME改为与SPF的TXT共存
# 错误：
# example.com.  CNAME  alias.example.com.
# 正确（移除CNAME，直接使用TXT记录）：
# example.com.  TXT  "v=spf1 ..."
```

### 2.3 redirect机制循环检测

**根因**：`redirect=domain`机制将SPF检查跳转到另一个域名的SPF记录。如果A域的SPF包含`redirect=B`，而B域的SPF包含`redirect=A`，则形成无限循环。RFC 7208 §6.1要求SPF实现必须检测这种循环，并返回PermError。

```
# 检测redirect链
dig TXT example.com | grep redirect
# v=spf1 redirect=_spf.example.com
dig TXT _spf.example.com | grep redirect
# v=spf1 redirect=example.com  ← 循环！

# 修复：消除循环，确保redirect链是DAG（有向无环图）
# 使用 spf-query 检测循环深度
spf-query --domain example.com --trace
# → Redirect loop detected between example.com and _spf.example.com
```

### 2.4 include深度递归

**根因**：与redirect类似但更常见——`include`链中的深度递归。例如：A include B → B include C → C include A。SPF解析器必须检测include递归，RFC 7208 §4.6.4要求SPF实现跟踪include深度，超过某种实现定义的阈值后应返回PermError。

```
# 检测include链
python3 << 'PYEOF'
import dns.resolver

def trace_includes(domain, path=None, limit=15):
    if path is None:
        path = []
    if domain in path:
        return f"CIRCLE! {' → '.join(path + [domain])}"
    if len(path) > limit:
        return f"DEPTH_EXCEEDED! {len(path)} levels"
    try:
        answers = dns.resolver.resolve(domain, 'TXT')
        for rdata in answers:
            txt = rdata.to_text()
            if 'v=spf1' in txt:
                for word in txt.split():
                    if word.startswith('include:'):
                        inc = word.split(':', 1)[1]
                        return trace_includes(inc, path + [domain], limit)
        return " → ".join(path + [domain]) if path else domain
    except Exception as e:
        return f"{' → '.join(path + [domain])} [ERROR: {e}]"

print(trace_includes("example.com"))
PYEOF
```

### 2.5 语法引号不匹配

**根因**：SPF记录本身以`"v=spf1"`开始，但当多个DNS TXT记录字符串拼接成一条SPF记录时，引号不匹配导致解析失败。RFC 7208 §3指出SPF记录由单条TXT记录的字符串组成。如果有多个字符串片段，`"v=spf1" "include:_spf.a.com"`在DNS中实际合并为`v=spf1 include:_spf.a.com`。但如果引号未正确配对（如`"v=spf1 include:_spf.a.com`缺少闭合引号），SPF解析返回PermError。

```
# 检查引号是否完整
dig TXT example.com | grep -E 'spf1|"'
# 正确输出示例：
# example.com.  300 IN  TXT  "v=spf1 include:_spf.google.com ~all"

# 错误输出示例（不匹配的引号）：
# example.com.  300 IN  TXT  "v=spf1 include:_spf.google.com"  "~all"
# 或：
# example.com.  300 IN  TXT  "v=spf1 include:_spf.google.com ~all

# 使用spf语法验证
python3 -c "
import spf
result, explanation, _ = spf.check(i='203.0.113.5', s='user@example.com', h='mail.example.com')
print(f'SPF result: {result}')
print(f'Explanation: {explanation}')
"
```

### 2.6 多条SPF记录

**根因**：DNS中同一域名存在两条或更多以`v=spf1`开头的TXT记录。RFC 7208 §4.5规定：当查询返回多条SPF记录时，SPF验证工具无法判断哪条是作者预期的，应返回PermError。

```
# 诊断
dig TXT example.com | grep "v=spf1" | wc -l
# 如果 ≥ 2，立即确认PermError

# 查看两条记录
dig TXT example.com | grep "v=spf1"

# 修复：合并为一条记录
# v=spf1 include:_spf.a.com include:_spf.b.com ~all

# 特别注意：有些DNS托管商会自动添加SPF记录
# 如果用户在DNS面板中手动添加了一条SPF记录
# 而DNS托管商又自动生成了一条，就产生了双SPF
```

### 2.7 与DMARC对齐的连锁反应

SPF PermError对DMARC的影响是该问题被低估的原因之一。DMARC策略p=reject但SPF返回permerror时，如果DKIM验证也未通过，DMARC将失败，即使From域本身是合法的。

```
# DMARC报告中的典型记录
# <policy_evaluated>
#   <dkim>pass</dkim>
#   <spf>fail</spf>       ← SPF验证失败
#   <disposition>none</disposition>
# </policy_evaluated>
# <auth_results>
#   <spf>
#     <domain>example.com</domain>
#     <result>permerror</result>   ← 根因是permerror而非fail
#   </spf>
# </auth_results>

# 如果DKIM也失败（未使用DKIM签名的邮件）：
# DMARC = fail（SPF permerror + DKIM fail = 全失败）
```

## 3. DNSPython全面诊断脚本

```
#!/usr/bin/env python3
"""SPF PermError 全面诊断工具"""
import dns.resolver
import sys

def diagnose_spf(domain):
    results = []
    try:
        answers = dns.resolver.resolve(domain, 'TXT')
    except dns.resolver.NoAnswer:
        return [f"❌ No TXT records found for {domain}"]
    except dns.resolver.NXDOMAIN:
        return [f"❌ Domain {domain} does not exist"]
    
    spf_records = []
    for rdata in answers:
        txt = rdata.to_text()
        if 'v=spf1' in txt:
            spf_records.append(txt)
    
    if len(spf_records) == 0:
        results.append(f"❌ No SPF record found for {domain}")
    elif len(spf_records) > 1:
        results.append(f"❌ Multiple SPF records found ({len(spf_records)}):")
        for r in spf_records:
            results.append(f"   {r[:100]}...")
    else:
        results.append(f"✅ Single SPF record: {spf_records[0][:120]}...")
    
    if spf_records:
        spf_text = spf_records[0]
        # Check for CNAME
        try:
            dns.resolver.resolve(domain, 'CNAME')
            results.append("⚠️  CNAME record present - check SPF compatibility")
        except dns.resolver.NoAnswer:
            pass
        
        # Count mechanisms that cause DNS lookups
        mechs = spf_text.split()
        lookup_mechs = sum(1 for m in mechs 
                          if m.startswith('include:') or m.startswith('a') 
                          or m.startswith('mx') or m.startswith('ptr') 
                          or m.startswith('exists') or m.startswith('redirect'))
        results.append(f"📊 Estimated DNS lookups: {lookup_mechs} (limit: 10)")
        if lookup_mechs > 10:
            results.append("❌  EXCEEDS 10 LOOKUP LIMIT - will cause PermError")
        elif lookup_mechs > 8:
            results.append("⚠️  Approaching lookup limit (8+)")
        
        # Check redirect
        redirect = [m for m in mechs if m.startswith('redirect=')]
        if redirect:
            results.append(f"🔍 Redirect target: {redirect[0]}")
        
        # Check all
        has_all = any(m in ['~all', '-all', '+all', '?all'] for m in mechs)
        if not has_all:
            results.append("⚠️  No all mechanism - default is neutral")
    
    return results

if __name__ == '__main__':
    domain = sys.argv[1] if len(sys.argv) > 1 else input("Enter domain: ")
    for line in diagnose_spf(domain.strip()):
        print(line)
```

## 4. 自动化修复：SPF Flatten工具

### 4.1 工具选择

| 工具 | 语言 | 特点 | 适用 |
| --- | --- | --- | --- |
| spftool (jcbf/libspf2) | C | 最成熟的SPF库，支持-flatten | 生产环境 |
| spf-tools (spf-tools.github.io) | Shell | 轻量级，支持macro展开 | 小到中型域 |
| python-spf (pypi: spf-query) | Python | 可编程，集成诊断 | CI/CD管道 |
| spfquery (postfix-policyd-spf-perl) | Perl | Postfix集成最方便 | Postfix集成 |

### 4.2 使用spftool展平

```
# spftool -flatten 自动展开include/mx/redirect为ip4/ip6
# 安装
git clone https://github.com/jcbf/libspf2.git
cd libspf2
./configure && make && sudo make install

# 展平
spftool -flatten example.com
# 输出：
# v=spf1 ip4:203.0.113.0/24 ip4:198.51.100.0/24
#   ip4:192.0.2.0/24 include:_spf.google.com ~all
# Lookups saved: 7→2

# 与原始SPF对比
spftool -flatten -verbose example.com
# 显示每个include解析结果
```

### 4.3 使用spf-tools的spf妙用

```
# spf-tools 是纯shell实现，适合CI
git clone https://github.com/spf-tools/spf-tools.git
cd spf-tools

# 简化并展平
./spf_simplify.sh example.com > flat_spf.txt
cat flat_spf.txt
# v=spf1 ip4:203.0.113.0/24 ip4:198.51.100.0/24 ~all

# 更新DNS记录
./spf_update.sh example.com  # 更新DNS托管商的TXT记录
```

## 5. 预防性检查清单

1. **查询计数**：每次SPF变更前，执行`spf-query --domain DOMAIN --print-lookups`确保≤10次。
2. **多记录检查**：`dig TXT DOMAIN | grep v=spf1 | wc -l` 必须为1。
3. **CNAME审计**：SPF记录所在域名不能同时有CNAME记录。RFC 7208 §4.6.3。
4. **语法验证**：使用`python3 -c "import spf; spf.check(...)"`验证语法。
5. **DMARC联动测试**：在p=reject之前先将p=none监控2周，观察DMARC报告中是否出现SPF permerror而非pass。
6. **redirect链检测**：确保redirect目标域的SPF不包含redirect回来源域。
7. **include去重**：同一域的多次include只计1次查询。
8. **定期扫描**：使用`check_spf.py`脚本或类似工具定期扫描所有托管域的SPF。

## 参考文献

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/spf-permerror-diagnostic.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
