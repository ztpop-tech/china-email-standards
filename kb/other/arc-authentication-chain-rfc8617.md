---
title: "ARC 邮件认证链协议深度解析 — RFC 8617：转发与邮件列表的认证可追溯性"
source: "https://ztpop.net/kb/arc-authentication-chain-rfc8617.html"
license: CC-BY 4.0
---

# ARC 邮件认证链协议深度解析 — RFC 8617：转发与邮件列表的认证可追溯性

SPF（RFC 7208）、DKIM（RFC 6376）和 DMARC（RFC 7489）三者共同构成现代邮件认证的基石。然而这套体系依赖一个隐含前提：邮件从发件方到收件方的传输路径上，所有中间跳转都不会修改邮件内容。一旦邮件经过邮件列表（mailing list）或者自动转发（auto-forwarding），这个前提就会崩塌。邮件列表会在邮件末尾追加退订说明，转发服务可能修改 Return-Path——任何对邮件正文或 header 的修改，都会使原始 DKIM 签名失效。当 DKIM 签名断裂、SPF 因为转发路径的 IP 不属于原始域而 fail 时，DMARC 评估结果就是 fail，收件方可能据此拒收或标记为垃圾邮件。这就是 RFC 8617（Authenticated Received Chain，ARC）要解决的核心问题。

**一、ARC 的设计动机与工作模型**

ARC 的核心理念并不复杂：让每一个处理过这封邮件的「中间人」（intermediary）在邮件头上留下自己的认证快照和签名，形成一条可追溯的认证链条。下游接收方不直接信任中间的 ARC 声明，而是逐环验证链条的完整性，从而推断出邮件在到达第一个中间人之前是否通过了认证。

RFC 8617 第 1.1 节明确了 ARC 的三个参与者角色：
**Originating ADMD**
（原始发件域，即邮件最初离开的域）、
**Intermediary ADMD**
（中间域，如邮件列表服务）、以及
**Destination ADMD**
（最终接收域）。每个中间域在收到邮件后，先执行自己的 SPF / DKIM / DMARC 认证评估，然后以三连头部（ARC Set）的形式将评估结果写入邮件 header。这条链上的每个中间人，都在前一个 ARC Set 的基础上追加自己的 Set，构成 i 值递增的集合。

RFC 8617 第 1.2 节给出了 ARC 的信任模型：下游 ADMD 可以自选是否参与 ARC 评估。如果最终接收方选择评估 ARC 链，它的信任范围仅止于链条上的各个中间人签名——中间人声明的是「我在自己的位置看到了什么认证结果」，而不是「这封邮件没有问题」。最终结论仍由接收方根据 ARC 链的完整性自行判定。

表：Arc Authentication Chain Rfc8617

| 角色 | 阶段动作 | 写入的 ARC 内容 |
| --- | --- | --- |
| Originating ADMD | 完成 SPF / DKIM 签名后发信 | 不写入 ARC（起点无 ARC Set） |
| Intermediary #1 | 收信 → 执行认证评估 → 修改邮件 → 转发 | ARC Set i=1（AAR + AMS + AS） |
| Intermediary #2 | 收信 → 验证前置 ARC 链 → 执行认证评估 → 修改邮件 → 转发 | ARC Set i=2（含前链的 AS 验证结果） |
| Destination ADMD | 收信 → 验证完整 ARC 链 → 结合 SPF/DKIM/DMARC 裁决 | 不写入 ARC（终点只读） |

**二、ARC 三连头部（ARC Set）的完整结构**

一个完整的 ARC Set（RFC 8617 第 5 节）由三部分组成，i 值相同表示它们属于同一中间人：

**1. ARC-Authentication-Results（AAR，认证结果快照）**

AAR 是当前中间人对邮件执行认证后产生的 Authentication-Results header 的快照。它记录了这个中间人在当时看到了什么 SPF / DKIM / DMARC 结果。RFC 8617 第 5.1 节规定，AAR 必须包含 instance 标签（对应 i 值）和完整的 authres 结果。如果原始的 Authentication-Results header 中包含多个方法的结果（如同时包含 SPF 和 DKIM），AAR 应全部保留。

```
ARC-Authentication-Results: i=1;
  mx.example.org;
  spf=pass smtp.mailfrom=alice@example.com;
  dkim=pass header.i=@example.com;
  dmarc=pass header.from=example.com;
```

**2. ARC-Message-Signature（AMS，消息签名）**

AMS 是对当前邮件整个消息体（body）和已选定的头部字段（headers）的 DKIM 风格签名。它的语法与 DKIM-Signature 高度一致（RFC 8617 第 5.2 节）。关键区别在于：AMS 作用域包括
**除 ARC-Seal 外的所有已有的 ARC 头部**
——这意味着 AMS 覆盖了上游的 AAR 和 AMS，一旦邮件 body 或任何被覆盖的 header 被篡改，该 AMS 即告失效。签名算法通过 a= 标签指定，实测中 rsa-sha256 是推荐选择。

```
ARC-Message-Signature: i=1; a=rsa-sha256; c=relaxed/relaxed;
  d=mail-list.example.org; s=arc2024;
  h=From:To:Subject:Date:ARC-Authentication-Results;
  bh=Q6ifBOLECaxqNxPLrI+fS+MAI1J8a84RH/OT5JRQO64=;
  b=LgSHnF7/K0e/qeA2dQL3hFP+mv...;
```

**3. ARC-Seal（AS，密封签名）**

ARC-Seal 是整个 ARC Set 的「封印」。它对本 Set 的 AAR 和 AMS 以及上一跳的 ARC-Seal（如果存在）进行签名。RFC 8617 第 5.3 节对 AS 的覆盖范围做了精确规定：签名覆盖 (1) 当前 i 值的 AAR 和 AMS，(2) 前一个 i-1 值的 AS（除 b= 标签值本身外的全部标签），以及 (3) AMS 签名的 h= 列表中指定的头部字段。这种层层嵌套的封印结构确保了一旦中间某个环被篡改，下游的链式验证就能检测到。

```
ARC-Seal: i=1; a=rsa-sha256; d=mail-list.example.org;
  s=arc2024;
  cv=none;
  b=fCyNh2KZvx6bGqyjYsTWSb4o+i4crlkLwZmWNh/U7v...;
```

上述三个头部中的 i= 标签是 ARC Set 的实例号，从 1 开始递增。RFC 8617 第 4.1 节建议上限不超过 50，以防止无限链式追加导致的头部膨胀。

**三、cv 状态机与 chain 评估逻辑**

ARC-Seal 中的 cv=（chain validation status）标签承载了链式验证的结果。cv 有三种取值（RFC 8617 第 4.3 节）：

表：Arc Authentication Chain Rfc8617

| cv 值 | 含义 | 触发条件 |
| --- | --- | --- |
| `cv=pass` | 链验证通过 | 当前中间人成功验证了 i-1 的 AS 签名，且 i-1 的 cv 也是 pass（或 i-1=0 时不存在前链） |
| `cv=fail` | 链验证失败 | i-1 的 AS 签名不匹配、邮件在到达当前中间人前被篡改，或 i-1 的 cv=fail |
| `cv=none` | 无前链可验证 | i=1（第一个中间人），上游没有任何 ARC Set 可供验证 |

cv 的传播逻辑是「一票否决」式的：如果 i=2 验证 i=1 的 AS 失败 → i=2 写入 cv=fail。然后 i=3 验证 i=2 的 AS 时，即使签名正确，也会因为 i=2 的 cv=fail 而继续判断为链失败（RFC 8617 第 4.3.2 节——cv 值遵循「传递性」规则，即链中任一环的 fail 会污染下游所有 cv）。

最终接收方评估 chain 时，会检查邮件中所有 ARC-Seal header。核心判断逻辑（RFC 8617 第 6.2 节）：

```
如果 chain 中所有 cv 均为 pass：
  推断原始认证结果是可信的 → 可以覆盖 DMARC 的 fail 判定
  
如果 chain 中存在 cv=fail：
  链断，不信任该 ARC 信息 → 维持 DMARC 的原始结果
```

cv 的符号化语义也简化了自动化处理的复杂度：接收方不需要重新执行每一个中间人的 DKIM 验签——只要验证 cv 链中签名的正确性，然后信任 cv 标签本身的串联结果即可。

**四、完整转发链示例**

假设 alice@example.com 向一个邮件列表发信，收件人 bob@destination.org 通过自动转发服务接收。以下是完整链路上各节点的 ARC 头部变化：

**阶段 1：原始邮件（alice@example.com → 邮件列表）**

```
From: alice@example.com
To: mailinglist@list.example.org
Subject: ARC testing
DKIM-Signature: v=1; a=rsa-sha256; d=example.com; s=default; ...
```

邮件到达邮件列表服务器后，SPF 和 DKIM 都通过，但列表服务在 body 尾部追加了退订链接，导致原始 DKIM 签名被破坏。邮件列表写入 ARC i=1：

```
ARC-Authentication-Results: i=1; list.example.org;
  spf=pass smtp.mailfrom=alice@example.com;
  dkim=pass header.i=@example.com;
  dmarc=pass header.from=example.com
ARC-Message-Signature: i=1; a=rsa-sha256; c=relaxed/relaxed;
  d=list.example.org; s=arc;
  h=From:To:Subject:Date:ARC-Authentication-Results;
  bh=H3fK1mQx...; b=P8zL...
ARC-Seal: i=1; a=rsa-sha256; d=list.example.org; s=arc;
  cv=none; b=9k3W...
```

**阶段 2：邮件列表 → 自动转发服务**

转发服务在收件时验证了 i=1 的 ARC-Seal 签名正确，然后修改了 Return-Path 和 To header。写入 ARC i=2：

```
ARC-Authentication-Results: i=2; forwarder.net;
  spf=pass smtp.mailfrom=list-bounce@list.example.org;
  dkim=neutral (unsigned);
  dmarc=pass header.from=example.com
ARC-Message-Signature: i=2; a=rsa-sha256; c=relaxed/relaxed;
  d=forwarder.net; s=arc;
  h=From:To:Subject:Date:ARC-Authentication-Results
    :ARC-Message-Signature:Return-Path;
  bh=Y2kP9r...; b=V5mQ...
ARC-Seal: i=2; a=rsa-sha256; d=forwarder.net; s=arc;
  cv=pass; b=7xR2...
```

最终接收方 destination.org 看到的邮件包含两组完整的 ARC Set（i=1 和 i=2），以及原始的 DKIM-Signature（已失效）。通过验证这两组 ARC-Seal：i=1 AS 签名正确（cv=none 无前链），i=2 AS 签名正确且 cv=pass，确认整条链完整。ARC chain 评估通过——destination.org 可以信任邮件列表和转发服务声明的原始认证结果，从而覆盖 DMARC 基于 SPF fail（因为 Return-Path 被改写）产生的 fail 判定。

**五、从邮件头部提取和验证 ARC 链**

在 Linux / Unix 邮件服务器上，可以使用以下命令从原始邮件文件中提取 ARC 相关的全部 header：

```
# 提取所有 ARC- 开头的头部行
grep -E '^(ARC-|Authentication-Results)' /var/spool/mail/bob | head -30

# 按 i= 值分组显示 ARC Set
grep -E '^ARC-' /var/spool/mail/bob | sort -t= -k2,2n

# 检查 cv 值的分布（快速判断链健康状态）
grep -oP 'cv=\K\w+' /var/spool/mail/bob
```

以下 Python 片段模拟了接收方对 ARC 链的基础验证流程——检查 i 值连续性、提取所有 cv 标签并执行链式传递规则：

```
import re
from email.parser import HeaderParser

def parse_arc_chain(raw_email):
    """从邮件原始文本中提取并验证 ARC 链"""
    msg = HeaderParser().parsestr(raw_email)
    
    arc_sets = {}
    cv_values = []
    max_i = 0
    
    for key, val in msg.items():
        if key.startswith('ARC-Seal') or key.startswith('ARC-Authentication-Results') or key.startswith('ARC-Message-Signature'):
            # 提取 i= 值
            m = re.search(r'i=(\d+)', val)
            if not m:
                continue
            i_val = int(m.group(1))
            max_i = max(max_i, i_val)
            
            if i_val not in arc_sets:
                arc_sets[i_val] = {}
            if key.startswith('ARC-Seal'):
                arc_sets[i_val]['seal'] = val
                # 提取 cv
                cv_m = re.search(r'cv=(\w+)', val)
                if cv_m:
                    cv_values.append((i_val, cv_m.group(1)))
    
    # 检查 i 值连续性
    expected = set(range(1, max_i + 1))
    actual = set(arc_sets.keys())
    if expected != actual:
        missing = expected - actual
        print(f"[WARN]  ARC Set 缺失 i= 值: {missing}")
    
    # 按 i 排序 cv 值
    cv_values.sort(key=lambda x: x[0])
    
    # 执行链式传递规则 (RFC 8617 §4.3.2)
    chain_valid = True
    for i, cv in cv_values:
        if cv == 'fail' or not chain_valid:
            chain_valid = False
            status = 'FAIL  (断链)'
        elif cv == 'none' and i == 1:
            status = 'NONE (起点)'
        elif cv == 'pass' and chain_valid:
            status = 'PASS'
        else:
            status = 'UNKNOWN'
        print(f"  i={i}: cv={cv:
<
6} → {status}")
    
    verdict = 'PASS' if chain_valid else 'FAIL'
    print(f"\n[ARC Chain Verdict] {verdict}")
    return verdict

# 示例调用
# verdict = parse_arc_chain(raw_email_text)
```

表：Arc Authentication Chain Rfc8617

| 验证步骤 | 检查项 | RFC 8617 参考 |
| --- | --- | --- |
| 1. i 值连续性 | 从 1 开始逐一递增，无跳号 | §4.1 |
| 2. 每层 AS 签名 | 使用 d= 域在 DNS 中查 arc.\_domainkey 公钥验签 | §5.3.1 |
| 3. cv 传递规则 | 任一 cv=fail 污染下游，全链即 invalid | §4.3.2 |
| 4. 域对齐 | AMS 的 d= 域与 AS 的 d= 域一致 | §5.3 |
| 5. i 值上限 | ARC Set 数不超过 50 | §4.1 |

**六、ARC 与 SPF / DKIM / DMARC 的协同**

ARC 不是 SPF / DKIM / DMARC 的替代品，而是它们的补充层。各协议在邮件处理流水线上的关系如下：

**SPF（RFC 7208）**
：验证 SMTP MAIL FROM 域授权的发送 IP。转发时 MAIL FROM（Return-Path）可能被改写，导致 SPF 在最终收件端无意义。ARC 的 AAR 在转发点捕获 SPF 当时的 pass/fail 结果，保留历史证据。

**DKIM（RFC 6376）**
：验证邮件内容完整性和签名域与 From 域的关联。正文被中间人修改（邮件列表加 footer、转发加 disclaimer）后 DKIM 签名直接失效。ARC 的 AMS 以类似 DKIM 的机制为修改后的邮件重新签名，保证当前态的内容完整性。

**DMARC（RFC 7489）**
：组合 SPF 和 DKIM 结果做出最终策略（p=none/quarantine/reject）。转发/列表场景下 SPF 和 DKIM 双双 fail 是常态，ARC 链提供了第二种评估路径：如果 ARC chain 验证通过，接收方可以信任中间人记录的认证历史，从而放宽 DMARC 的拒绝策略。

**SMTP（RFC 5321）**
：ARC 的头部在 SMTP DATA 阶段追加，属于邮件消息体的一部分。每个中间 MTA 在完成 SMTP 接收后，通过本地策略决定是否参与 ARC 处理。RFC 8617 未对 SMTP 协议本身提出任何扩展要求，ARC 只是一个纯邮件头部层面的叠加协议。

**七、OpenARC 部署实践与运维要点**

OpenARC 是 Trusted Domain Project 提供的开源 ARC 实现，通常作为 milter 嵌入 Postfix 或 Sendmail 流水线。其配置围绕两张表运作：

**Sign Table（签名表）**
：定义哪些域/消息应被本域签名。典型配置指定本域的所有出站邮件或作为邮件列表转发的邮件。

**Trust Table（信任表）**
：定义哪些上游发送者的 ARC 签名被视为可信（RFC 8617 第 6.1 节明确说明信任表的选择属于本地策略范畴）。如果不配置信任表，OpenARC 仍然会验证签名，但不会将其 cv 值作为决策输入。

DNS 配置要点——ARC 签名用到的公钥发布方式与 DKIM 相同，但查询路径使用
`arc`
作为 selector 前缀。例如 d=example.org、s=arc2024 的 AS 公钥位于
`arc2024._domainkey.example.org`
的 TXT 记录中。

日志监控方面，建议关注以下模式：

```
# OpenARC 日志中的 ARC 链验证结果
grep 'arc=pass\|arc=fail' /var/log/maillog | tail -50

# 统计 cv=fail 的出现频率（链断裂告警）
grep -c 'cv=fail' /var/log/maillog

# 按来源域聚合 ARC 验证通过率
grep 'arc=' /var/log/maillog | awk '{print $NF}' | sort | uniq -c | sort -rn
```

**八、已知局限与注意事项**

ARC 链路的安全假设依赖于中间人的诚实性。RFC 8617 第 7 节的安全考虑部分明确指出：如果攻击者控制了某个中间人，它可以在自己的 ARC Set 中写入伪造的 AAR 数据并用本域密钥签名——下游无法从签名本身区分「合法通过的认证」和「伪造的声明」。因此 ARC 的防护能力随中间人数量增加而递减，实际部署中信任表的选择是策略的核心。

另一个工程上的限制是头部膨胀。每经过一个 ARC 参与方，邮件增加 3 个头部。在邮件列表链条较长（如跨多个转发层）的情况下，头部体积会显著增长。RFC 8617 第 4.1 节建议中间人检查已有 ARC Set 的数量，当 i 超过 50 时停止追加新 Set。

ARC 协议目前的应用覆盖率还远不及 SPF / DKIM / DMARC。主要的邮件列表服务商和大型转发服务已经在基础设施中部署了 ARC，但中小型自建邮件服务器上配置 ARC 的情况仍属少数。对于运维团队而言，引入 ARC 之前应先确保 SPF / DKIM / DMARC 配置无误——ARC 解决的是认证链可追溯性，它无法弥补基础认证缺失。

**总结**

ARC（RFC 8617）是邮件认证栈中最晚加入的一块拼图。它直面了 SPF / DKIM / DMARC 体系在转发和邮件列表场景下系统性断裂的现实，通过「每个中间人留下自己的认证快照和签名」方式构建了一条可追溯的信任链。AAR 记录认证结果快照，AMS 保护内容完整性，AS 封印当前 Set 并与前链锚定——三者环环相扣，让下游接收方有能力穿越多层转发还原原始认证状态。对于运维人员而言，ARC 的部署门槛不高但收益明显：它可以实质降低 DMARC 在 legitimate 转发场景下的误判率，同时保留对伪造邮件的拒绝能力。

**参考来源：**
IETF RFC 8617 - Authenticated Received Chain (ARC) Protocol（§1.1, §1.2, §4.1, §4.3, §4.3.2, §5, §5.1, §5.2, §5.3, §5.3.1, §6.1, §6.2, §7）；IETF RFC 7208 - Sender Policy Framework (SPF)；IETF RFC 6376 - DomainKeys Identified Mail (DKIM) Signatures；IETF RFC 7489 - Domain-based Message Authentication, Reporting, and Conformance (DMARC)；IETF RFC 5321 - Simple Mail Transfer Protocol；OpenARC 开源项目文档 (Trusted Domain Project)；IANA Email Authentication Parameters Registry。

## 相关文章

[DKIM 签名原理与实践](/kb/dkim-guide.html)
[DMARC 完整部署指南](/kb/dmarc-guide.html)
[SPF 记录配置详解](/kb/spf-guide.html)
[邮件认证报告机制](/kb/email-auth-reporting.html)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/arc-authentication-chain-rfc8617.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
