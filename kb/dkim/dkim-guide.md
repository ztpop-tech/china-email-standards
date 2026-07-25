---
title: "DKIM 邮件签名机制深度解析 — RFC 6376：密钥管理、规范算法与 Selector 选择器"
source: "https://ztpop.net/kb/dkim-guide.html"
license: CC-BY 4.0
---

# DKIM 邮件签名机制深度解析 — RFC 6376：密钥管理、规范算法与 Selector 选择器

## 一、DKIM 的设计动机：为什么 SPF 不够

SPF（RFC 7208）问世后，运维圈一度以为邮件伪造问题即将终结。现实是 SPF 在纯直连场景下工作良好，但遇到邮件转发和邮件列表（mailing list）时几乎全线崩溃。原因很简单：SPF 校验的是 SMTP 信封中的 MAIL FROM 域与发送方 IP 的授权关系，而转发服务器会改写 MAIL FROM 域（例如变成转发服务自己的域），此时收件方查的已不是原始发件域的 SPF 记录。RFC 6376 第 1.1 节将这个问题概括为 SPF "无法跨越信任边界" —— 中间 MTA 在转发时可能修改邮件头部（添加 Received 头、Subject 重写），但 DKIM 的密码学签名附着于邮件自身，不依赖传输路径，因此具备跨越中继转发的能力。

一、DKIM 的设计动机：为什么 SPF 不够

| 场景 | SPF | DKIM |
| 直连发送 | ✅ 有效 | ✅ 有效（但非必需） |
| 邮箱转发（.forward / alias） | ❌ 通常失败（IP 变化） | ✅ 签名仍有效 |
| 邮件列表（Mailman / Google Groups） | ❌ 失败（头部改写 + IP 变化） | ⚠️ 取决于列表是否破坏签名 |
| 内容被中间 MTA 篡改 | ❌ 检测不到 | ❌ 签名验证失败，可感知 |
| Sender 重写（如 SRS） | ✅ 配合 SRS 可用 | ✅ 不影响 DKIM（签名不依赖信封） |

DKIM 的设计思路是用"信纸"而不是"信封"来承载身份。RFC 6376 第 2.1 节将其表述为：签名域对选定的头部字段和邮件正文进行数字签名，签名结果作为 DKIM-Signature 头部字段附加到邮件中，接收方利用 DNS 中发布的分域公钥独立验证。由于签名由发送域的私钥生成，任何没有私钥的第三方无法伪造有效签名；又因为签名覆盖了邮件内容，任何传输途中的内容篡改都会导致验证失败。

不过 DKIM 本身并不对验证失败策略做强制约束 —— 它只是一个
**签名与验证**
框架。是 DMARC 在 DKIM 上层建立起"失败后怎么办"的策略层。这个分层设计在 RFC 7489 第 1 节中有明确阐述。

**关键认知：**

DKIM 签名的是"谁对内容负责"（d= 域声明责任归属），不是"谁发了这封邮件"。d= 域可以和 5322.From 域不同。防冒充需要 DMARC 的 Identifier Alignment 来补齐。

## 二、DKIM-Signature 头部字段逐个拆解

RFC 6376 第 3.5 节定义了 DKIM-Signature 头部字段的完整语法。下发邮件中实际看到的一条标准 DKIM 签名如下：

DKIM-Signature: v=1; a=rsa-sha256; c=relaxed/relaxed; d=example.com;

  
s=202407; t=1720000000; x=1720604800;
  
h=from:to:subject:date:message-id:mime-version;
  
bh=47DEQpj8HBSa+/TImW+5JCeuQeRkm5NMpJWZG3hSuFU=;
  
b=Kj7G8v2MpL9xR3QweZ5TyU1VbN6AsDfGhJkLzXc...（base64 签名值）

以下逐标签解析其含义：

二、DKIM-Signature 头部字段逐个拆解

| 标签 | 含义 | RFC 引用 |
| `v=1` | DKIM 版本号，当前固定为 1 | RFC 6376 §3.5 |
| `a=` | 签名算法。rsa-sha256 是当前主力；ed25519-sha256 为 RFC 8463 定义的新一代算法 | RFC 6376 §3.5 / RFC 8463 §3 |
| `c=` | 规范化算法（canonicalization），格式为「头部算法/正文算法」。取值 simple 或 relaxed | RFC 6376 §3.4 |
| `d=` | 签名域（Signing Domain Identifier, SDID）。即声称对此签名负责的域名 | RFC 6376 §3.5 |
| `s=` | Selector（选择器）。与 d= 联合定位 DNS TXT 记录，用于密钥发现 | RFC 6376 §3.5、§3.6.2.1 |
| `h=` | 被签名的头部字段列表，用冒号分隔。接收方严格按此列表进行验证 | RFC 6376 §3.5、§5.4 |
| `bh=` | 正文哈希值（Body Hash），对规范化后的邮件正文计算得出 | RFC 6376 §3.7 |
| `b=` | 实际签名数据（Signature Data）。对 h= 中列出的头部字段 + bh= 正文哈希的联合哈希签名后，base64 编码 | RFC 6376 §3.5、§3.7 |
| `t=` | 签名时间戳（UNIX epoch 秒） | RFC 6376 §3.5 |
| `x=` | 签名过期时间。超过此时间接收方可拒绝签名 | RFC 6376 §3.5 |
| `l=` | 正文签名长度（body length count）。只对正文前 l 字节签名，超出部分不纳入验证范围 | RFC 6376 §3.5 |

### 2.1 h= 签名的头部字段

h= 标签列出被 DKIM 签名覆盖的头部字段。RFC 6376 第 5.4 节要求以下规则：

* h= 中列出的字段
  **必须包含 From**
  。From 是 DKIM 签名的强制项，因为它是 DMARC 对齐的唯一标准头部字段。
* 字段顺序不重要——签名验证时按字段名的字典序重新排列后再做哈希。这是规范化的一部分。
* 未列在 h= 中的头部字段不参与签名，中途可以任意增删而不破坏 DKIM。

典型的最小签名集合：

```
h=from:to:subject:date:message-id:mime-version:content-type;
```

这个集合覆盖了邮件最核心的元信息。发送方可以根据自身需求扩展——加上 Reply-To、List-Unsubscribe 等头部字段。但每多加一个字段，邮件的可传递性就降低一分，因为转发服务对这些非核心字段的改写概率远高于 From/Subject。

### 2.2 bh= 正文哈希

bh= 是对邮件正文进行哈希计算后的 base64 编码值。RFC 6376 第 3.7 节的规定：

1. 先对正文应用规范化算法（c= 的第二个参数），得到规范正文
2. 对规范正文计算 SHA-256（当 a=rsa-sha256 时）
3. 结果进行 base64 编码，放入 bh= 标签

bh= 的存在使 DKIM 验证时不必重新传输原始正文来计算签名：接收方拿到正文后独立计算 bh，与 DKIM-Signature 中的 bh= 比对，如果一致说明正文未被篡改。这个设计将「正文验证」与「头部验证」解耦，便于流式处理大体积邮件。

一个合理的疑问是：既然 bh= 已经做了正文哈希，为什么还要 b= 做第二层签名？答案在 RFC 6376 第 3.7 节的签名生成流程图中写得很清楚——b= 签的是「头部字段哈希 + bh=」这个联合体，不是逐字段签名。bh= 保证正文完整性，b= 保证头部字段与正文之间的
**绑定关系**
不可伪造。如果只有 bh= 而没有 b=，中间人可以替换 DKIM-Signature 的 h= 字段后重算 bh=，验证照样通过。

## 三、Simple vs Relaxed 规范化：为什么 Relaxed 是默认选择

邮件从发件 MTA 到收件 MTA 途中会经过若干中间节点，每个节点都可能对邮件做微小的格式调整。IETF 邮件基础设施中最常见的两种改动是：

* **空白字符折叠**
  ：某些转发 MTA 会将连续空格压缩为单个空格
* **头部字段大小写改写**
  ：From 变成 from，Message-ID 变成 Message-Id
* **换行符转换**
  ：CRLF（\r\n）与 LF（\n）之间的互转

这些改动在语义上对邮件内容毫无影响，但二进制级别完全不同。如果 DKIM 对原始字节做签名，任何一个空白/大小写变化都会导致验证失败——邮件列表场景尤甚，因为列表服务器几乎必然重写 Subject（添加 [list] 前缀）和修改正文尾部（添加退订链接）。

RFC 6376 第 3.4 节为此定义了两套规范化算法：

三、Simple vs Relaxed 规范化：为什么 Relaxed 是默认选择

| 算法 | 头部处理 | 正文处理 |
| **simple** | 不做任何改动，原始头部字段直接参与签名 | 不做任何改动，连末尾空行都保留 |
| **relaxed** | 字段名转小写；展开折叠空白（unfolding）；删除字段值末尾多余空白；将连续空白折叠为单个空格 | 忽略末尾空白行；将连续空白折叠为单个空格；删除行尾空白 |

c=relaxed/relaxed 是绝大多数生产部署的选择。它在两个维度上都是 relaxed——头部和正文。少数运维使用 c=relaxed/simple 组合，即头部用 relaxed（容忍中间 MTA 对头部的大小写/空白改写），正文用 simple（正文不容忍任何改动）。

用一个具体例子理解 relaxed 头部规范化的行为：

```
# 原始头部（发送方 MTA 书写）
From: "Sender Name" 
Subject: Hello   World

# simple 规范化结果（不变）：
From: "Sender Name" \r\nSubject: Hello   World\r\n

# relaxed 规范化结果：
from:"Sender Name" \r\nsubject:Hello World\r\n
  ↑小写       ↑空白折叠
```

RFC 6376 第 3.4.3 节明确指出：relaxed 是
**推荐**
的正文规范化算法。simple 正文规范化的脆弱性在现实运维中反复被验证——邮件列表在正文末尾追加退订页脚后，simple 正文验证必然失败。Relaxed 通过忽略末尾空白行来适应这种情况。

## 四、RSA vs Ed25519：密钥算法的选择

DKIM 的签名算法由 a= 标签指定。长期以来主力算法是 rsa-sha256，2023 年后 Ed25519 的支持显著增长，得益于 RFC 8463 的标准化。

四、RSA vs Ed25519：密钥算法的选择

| 维度 | rsa-sha256 | ed25519-sha256 |
| 标准化 | RFC 6376 §3.3 | RFC 8463 §3 |
| 推荐密钥长度 | 2048 位（最低），3072 位（推荐） | 256 位（固定） |
| 公钥大小 | ~450 字节（2048 位） | ~60 字节 |
| 签名大小 | ~340 字节（base64 后） | ~90 字节（base64 后） |
| DNS TXT 记录 | 可能超过 255 字节限制，需要拆分 | 远小于 255 字节 |
| 签名速度 | 慢（~1000 次/秒） | 快（~10000 次/秒） |
| 验证速度 | 中等 | 非常快 |
| 互操作性 | 所有邮件系统支持 | 较新 MTA 支持，老系统可能不识别 |

RSA 2048 位密钥的实际生成：

```
# 生成 RSA 2048 位 DKIM 私钥
openssl genrsa -out dkim_private.pem 2048

# 提取公钥（用于 DNS TXT 记录发布）
openssl rsa -in dkim_private.pem -pubout -out dkim_public.pem

# 查看公钥（去除 PEM 头尾 + 换行符，得到 DNS 中 p= 的值）
openssl rsa -in dkim_private.pem -pubout 2>/dev/null | \
  grep -v '^-' | tr -d '\n'
```

Ed25519 密钥的生成（RFC 8463 第 3 节定义的 ed25519-sha256 算法）：

```
# 生成 Ed25519 私钥
openssl genpkey -algorithm ed25519 -out dkim_ed25519_private.pem

# 提取公钥
openssl pkey -in dkim_ed25519_private.pem -pubout -out dkim_ed25519_public.pem
```

**互操作性提示：**
截至 2026 年，Google Workspace、Microsoft 365、Proofpoint 均已支持 ed25519-sha256 的 DKIM 验证。但部分企业邮件网关（尤其是 2020 年前部署的老旧设备）可能不支持。生产环境建议双签名——同时签发 rsa-sha256 和 ed25519-sha256，让接收方选择自己能验证的算法。

## 五、Selector 选择器：密钥分层的核心机制

DKIM 的公钥不直接挂在域名上，而是通过
**Selector**
选择器实现一层间接寻址。RFC 6376 第 3.6.2.1 节定义了公钥的记录格式与查询路径：

```
查询路径：[selector]._domainkey.[domain] 的 TXT 记录

例：s=202407; d=example.com
→ DNS 查询：202407._domainkey.example.com  TXT
```

这层间接寻址的设计非常精妙，解决了现实运维中的一系列问题：

### 5.1 密钥轮换（Key Rotation）

密钥需要定期更换。如果公钥直接挂在域名上，换密钥时新旧交替的空窗期会丢信。有了 Selector：

1. 生成新密钥对，发布到新 Selector（如 2024Q3.\_domainkey.example.com）
2. 修改 MTA 配置，用新 Selector + 新私钥签名
3. 保留旧 Selector 的 DNS 记录至少 7 天（等待途中的旧签名邮件被验证完毕）
4. 7 天后删除旧 Selector 的 DNS TXT 记录

整个过程接收方无感知——它们查的是邮件 DKIM-Signature 中 s= 指定的 Selector，只要该 Selector 的记录还在 DNS 中就行。

### 5.2 多部门 / 多服务隔离

同一个域名可能有多个发送源：

* 公司邮件服务器（Exchange / Postfix）→ s=mail2024
* 营销邮件平台（SendGrid / Mailchimp）→ s=marketing
* 工单系统（Zendesk / Jira）→ s=service
* 开发测试环境 → s=dev

每个 Selector 对应独立的密钥对。一旦某个密钥泄露（比如营销平台的私钥被第三方滥用），只需撤销对应 Selector 的 DNS 记录，不影响其他发送源。RFC 6376 第 3.6.2 节将此概括为「每个签名实体拥有独立的公钥命名空间」。

### 5.3 DNS TXT 记录格式

一个典型的 DKIM TXT 记录：

```
202407._domainkey.example.com.  IN  TXT  "v=DKIM1; k=rsa; p=MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8A..."
```

各字段含义（RFC 6376 第 3.6.1 节）：

5.3 DNS TXT 记录格式

| 标签 | 含义 |
| `v=DKIM1` | DKIM 版本标识，固定值 |
| `k=rsa` | 密钥类型：rsa（默认）或 ed25519（RFC 8463） |
| `p=` | Base64 编码的公钥数据。这是核心字段 |
| `t=s` | 可选。s 表示此域所有邮件都必须签名（strict mode） |
| `t=y` | 可选。y 表示测试模式，验证方可酌情处理失败 |
| `h=sha256` | 可选。指定接受的哈希算法（RFC 6376 §3.6.1） |

RSA 2048 位密钥的 p= 值约 400 字节，单个 TXT 记录的字符串段限制为 255 字节（RFC 1035），所以通常需要拆成多段：

```
202407._domainkey.example.com.  IN  TXT  (
    "v=DKIM1; k=rsa; "
    "p=MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAu..."
    "......QIDAQAB" )
```

Ed25519 就没有这个麻烦——公钥仅 32 字节，base64 后约 44 字符，一条 TXT 记录绰绰有余。

## 六、t= / x= / l=：签名范围控制

DKIM 提供了三个可选标签用于控制签名的有效范围，理解它们对排错至关重要：

### 6.1 t= 签名时间戳

t= 记录签名生成时的 UNIX 时间戳（秒）。RFC 6376 第 3.5 节将其标记为
**推荐**
（RECOMMENDED）字段。接收方可以用 t= 来判断签名是否过新或过旧，配合 x= 做时间窗口校验。缺少 t= 的签名仍然有效，但无法做时间维度的判断。

### 6.2 x= 签名过期时间

x= 定义了签名的过期时间。RFC 6376 第 5.4 节指出：

> "A verifier MAY ignore a signature if the verification time at the verifier is past the expiration time."
>   
> — 接收方可以在当前时间超过 x= 后拒绝接受此签名。
>
> x= 的典型设置是 t + 7 天（604800 秒）。邮件排进队列后可能数小时才投递到收件方，太短的 x= 容易让合法邮件在队列排队期间就"过期"。但 x= 也不能设太长——已废弃的签名在 DNS 中仍然存活，过长的有效期意味着密钥泄露后的窗口更大。
>
> ### 6.3 l= 正文签名长度
>
> l= 是一个有争议的设计。它指定只对正文的前 l 个字节签名，超出部分不纳入验证范围。RFC 6376 第 3.5 节和 8.2 节对这个字段有特别讨论——它的存在是为了让邮件列表在正文末尾追加退订页脚后签名仍然有效。
>
> 但 l= 也引入了一个严重的安全问题：如果 l= 设得太小（比如只签正文前 100 字节），攻击者可以在签名覆盖范围之外插入恶意内容，DKIM 验证仍然通过。这在 RFC 6376 第 8.2 节被标记为已知的安全考量：
>
> > "Use of the 'l=' tag might allow recipients to be deceived... A signer using 'l=' should be aware that content beyond the signed length may have been added."
> >   
> > — RFC 6376 §8.2
> >
> > 因此，安全敏感场景（金融、政务）的邮件签名
> > **不使用 l=**
> > 。如果邮件列表需要追加内容，更优雅的做法是让列表服务器用自己的域名重新签名（见后文"邮件列表的 DKIM 断链"一节）。
> >
> > 6.3 l= 正文签名长度
> >
> > | 标签 | 推荐值 | 不设置的风险 |
> > | `t=` | 始终设置 | 无法判断签名生成时间 |
> > | `x=` | t + 604800（7 天） | 重放攻击窗口更大 |
> > | `l=` | 不设置（默认签全文） | 无风险；设置不当反而引入内容注入漏洞 |
> >
> > ## 七、DKIM Oversigning：额外签头部字段防篡改
> >
> > DKIM 的一个精妙战术叫做
> > **Oversigning**
> > —— 在 h= 中签入比邮件实际存在的数量更多的同一字段。RFC 6376 虽然没有使用 "Oversigning" 这个术语，但在第 5.4.1 节强调了「签名者可以签入邮件中不存在的字段实例」的行为。
> >
> > 原理如下：正常的一封邮件通常只有一个 From、一个 Subject、一个 Date。如果签名时 h= 中声明了
> > `from:from:from`
> > （签入 3 个 From 实例），而邮件本身只有一个 From 头部，那么中间人即便增加一个额外的 From 头部，也只会凑齐 2 个——远不到 3 个，验证仍然失败。
> >
> > 更精确的表达：DKIM 的头部字段签名机制是
> > **计数索引**
> > 的（per-field instance counting，RFC 6376 第 5.4 节）。h=from:from 意味着签名覆盖第 1 个和第 2 个 From 实例。如果邮件只有一个 From，那第 2 个实例被认为是空值签入——任何后添加的第 2 个 From 都会使签名失效。
> >
> > Oversigning 实战中签入的额外字段通常包括：
> >
> > ```
> > # 标准签名（不 oversign）：
> > h=from:to:subject:date:message-id;
> >
> > # Oversigning 签名（额外签入空实例）：
> > h=from:from:to:subject:date:message-id:message-id:mime-version:mime-version;
> > #  ↑双签 ↑双签          ↑双签
> > ```
> >
> > 这个小技巧对防御 DKIM 重放攻击（replay attack）也有帮助。如果一个攻击者截获一封 DKIM 签名邮件，原封不动地改变收件人（RCPT TO）再次发送，签名依然有效——因为 DKIM 不签信封收件人。而如果原始签名对 To 字段做了 Oversigning（h=...:to:to:...），攻击者新增的第 2 个 To 就会破坏签名。
> >
> > ## 八、与 DMARC 的协同：d= 域与 5322.From 的对齐
> >
> > DKIM 验证通过只说明签名有效，不解决"签名域 d= 是否与发件人可感知身份一致"的问题。这正是 DMARC 的切入点。
> >
> > RFC 7489 第 3.1 节定义了 Identifier Alignment（标识符对齐）的概念。DKIM 对齐有两种模式：
> >
> > 八、与 DMARC 的协同：d= 域与 5322.From 的对齐
> >
> > | 对齐模式 | 规则 | RFC 7489 |
> > | **Strict** | DKIM 签名中的 d= 必须与 5322.From 域 **完全一致** | §3.1 |
> > | **Relaxed** | DKIM 签名中的 d= 必须与 5322.From 域属于同一 **组织域** （Organizational Domain） | §3.1 |
> >
> > 以一个具体例子说明差异：
> >
> > ```
> > From: user@mail.example.com
> > DKIM-Signature: d=example.com
> >
> > Strict 对齐  → ❌ 失败（mail.example.com ≠ example.com）
> > Relaxed 对齐 → ✅ 通过（organization domain 都是 example.com）
> > ```
> >
> > 组织域的提取规则在 RFC 7489 第 3.2 节——从域名最左端开始，一直剥到公共后缀（Public Suffix）的上一级。也就是说，mail.example.com 和 news.example.com 的组织域同为 example.com。
> >
> > **关键安全边界：**
> > DKIM 签名只担保 d= 域对签名内容负责，
> > **不担保 d= 域与邮件实际发件人身份一致**
> > 。假设 attacker.com 正确签发了一封 DKIM 签名的邮件但 5322.From 为 ceo@victim.com，DKIM 验证通过（签名有效），但收件人看到的是 ceo@victim.com。没有 DMARC 对齐校验，这就是一次成功的伪装攻击。这就是 DKIM 和 DMARC 必须协同部署的根本原因。
> >
> > ## 九、生产环境实操：OpenDKIM 配置
> >
> > OpenDKIM 是 Trusted Domain Project 维护的开源 DKIM 实现，在 Postfix 和 Sendmail 生态中广泛使用。以下为完整部署流程。
> >
> > ### 9.1 安装与基础配置
> >
> > ```
> > # Debian/Ubuntu
> > apt install opendkim opendkim-tools
> >
> > # 主配置文件 /etc/opendkim.conf
> > Syslog              yes
> > UMask               002
> > Canonicalization    relaxed/relaxed
> > Mode                sv
> > SubDomains          no
> > AutoRestart         yes
> > AutoRestartRate     10/1M
> > KeyTable            /etc/opendkim/KeyTable
> > SigningTable        /etc/opendkim/SigningTable
> > ExternalIgnoreList  /etc/opendkim/TrustedHosts
> > InternalHosts       /etc/opendkim/TrustedHosts
> > Socket              inet:8891@localhost
> > ```
> >
> > ### 9.2 密钥与签名表
> >
> > ```
> > # 为域名 example.com 生成密钥（selector: 202407）
> > opendkim-genkey -b 2048 -d example.com -s 202407
> >
> > # 生成的文件：
> > #   202407.private    → 私钥
> > #   202407.txt        → DNS TXT 记录（公钥，可直接贴到 DNS 控制台）
> >
> > # /etc/opendkim/KeyTable
> > 202407._domainkey.example.com example.com:202407:/etc/opendkim/keys/202407.private
> >
> > # /etc/opendkim/SigningTable
> > *@example.com 202407._domainkey.example.com
> > ```
> >
> > ### 9.3 Postfix 集成
> >
> > ```
> > # /etc/postfix/main.cf
> > milter_default_action = accept
> > milter_protocol = 6
> > smtpd_milters = inet:localhost:8891
> > non_smtpd_milters = inet:localhost:8891
> > ```
> >
> > ## 十、Python dkimpy 签名与验证脚本
> >
> > dkimpy 是 Python 生态中的 DKIM 库，适合自动化测试和自定义签名逻辑。以下为完整的签名与验证示例：
> >
> > ```
> > #!/usr/bin/env python3
> > """DKIM 签名生成与验证示例 (dkimpy)"""
> > import dkim
> > import email
> > from email.mime.text import MIMEText
> >
> > # ============ 签名 ============
> > msg = MIMEText("这是一封测试邮件正文。\n")
> > msg["From"] = "sender@example.com"
> > msg["To"] = "receiver@example.org"
> > msg["Subject"] = "DKIM Test Email"
> >
> > # 读取私钥
> > with open("/etc/opendkim/keys/202407.private", "rb") as f:
> >     private_key = f.read()
> >
> > # 添加 DKIM 签名
> > signed_msg = dkim.sign(
> >     message=msg.as_bytes(),
> >     selector=b"202407",
> >     domain=b"example.com",
> >     privkey=private_key,
> >     include_headers=[b"from", b"to", b"subject", b"date", b"message-id"],
> >     canonicalize=(b"relaxed", b"relaxed"),
> >     sig_algorithm=b"rsa-sha256",
> > )
> >
> > print("=== 签名后的邮件 ===")
> > print(signed_msg.decode(errors="replace"))
> >
> > # ============ 验证 ============
> > # 从 DNS 获取公钥后进行验证
> > # 注意：实际验证时需要 DNS 查询 _domainkey 记录
> > try:
> >     verified = dkim.verify(
> >         message=signed_msg,
> >         dnsfunc=dkimplug.dnsplug  # 需要实现 DNS 查询函数
> >     )
> >     print(f"\n验证结果: {verified}")
> > except dkim.ValidationError as e:
> >     print(f"验证失败: {e}")
> > except dkim.KeyFormatError as e:
> >     print(f"密钥格式错误: {e}")
> > ```
> >
> > ## 十一、排错：多跳转发中 DKIM 断掉的经典场景
> >
> > DKIM 验证失败的场景远比生成签名更复杂。通过对大量生产环境日志的归纳，以下是最常见的中断场景：
> >
> > ### 11.1 邮件列表重写（最高频）
> >
> > 邮件列表是最经典的 DKIM 杀手。一封被 DKIM 签名过的邮件进入列表服务器后：
> >
> > 1. Subject 被添加 [list-name] 前缀 → 如果 Subject 在 h= 内，签名破裂
> > 2. 正文末尾追加退订页脚（unsubscribe footer）→ 如果 l= 未设置，正文哈希 bh= 不匹配
> > 3. 列表服务器可能修改 Reply-To / List-\* 头部 → 取决于是否在 h= 中
> >
> > RFC 6376 第 5.4.2 节和附录 B 对邮件列表场景给出了以下应对策略：
> >
> > * **策略 A：列表服务器用自己的域重新签名**
> >   。列表服务器在修改邮件后，用列表域的新 Selector 添加自己的 DKIM 签名。这是 RFC 推荐的方案，也是 Google Groups 和 Mailman 3 的默认行为。
> > * **策略 B：使用 l= 允许正文追加**
> >   。列表服务器在正文末尾追加内容时，如果原始签名设置了 l= 只覆盖原始正文长度，追加内容不会破坏签名。但如第 6.3 节所述，这会引入内容注入风险。
> >
> > ### 11.2 邮件网关的 MIME 重组
> >
> > 某些安全网关在扫描附件后会对 MIME 结构进行重组——比如将 multipart/mixed 重新编码为 multipart/related。这种操作改变了正文的规范化输出，导致 bh= 校验失败。RFC 6376 第 8.1 节的描述：
> >
> > > "An intermediary that re-encodes or otherwise transforms the message body will invalidate the body hash."
> >
> > 解决方法：(a) 让网关在签名前扫描；(b) 网关用自己的域名重新签名；(c) 网关配置为不修改 MIME 结构。
> >
> > ### 11.3 自动转发 + SRS 的交叉影响
> >
> > 自动转发（如 .forward 文件）只修改 SMTP 信封（MAIL FROM），不修改邮件头部和正文，因此
> > **不会破坏 DKIM**
> > 。但在 SRS（Sender Rewriting Scheme）场景中，转发服务器用 SRS 地址替换 MAIL FROM 以保证 SPF 通过——这对 DKIM 仍然无影响，因为 DKIM 签的是头部和正文，不依赖信封。
> >
> > 然而新问题出现了：如果转发服务器在自动转发过程中改写了消息头（例如添加 Resent-From、Resent-To），而这些头部在被签名字段 h= 列表之外，DKIM 仍然有效——但接收方可视的 From 与 DKIM 的 d= 域可能不一致。这时需要 DMARC 的对齐校验来兜底。
> >
> > ### 11.4 DNS 不可达导致公钥查询失败
> >
> > 这是最容易被忽略的故障场景。DKIM 验证需要实时查询 DNS TXT 记录：
> >
> > ```
> > dig +short 202407._domainkey.example.com TXT
> > ```
> >
> > 如果 DNS 服务器超时、返回 SERVFAIL、或者 DNSSEC 验证链断裂，验证方可能获得一个 "tempfail"（临时失败）而非 "permanent fail"。RFC 6376 第 6.3 节的建议是：遇到临时失败应暂缓决策，等 DNS 解析恢复后重试，而非直接拒绝。
> >
> > ### 11.5 DKIM 断链场景速查表
> >
> > 11.5 DKIM 断链场景速查表
> >
> > | 场景 | DKIM 状态 | 根因 | 修复方向 |
> > | 自建 MTA 直发 | ✅ 正常 | — | — |
> > | 邮件列表（Mailman） | ❌ 断裂 | Subject 改写 / 正文追加 | 列表服务器重新签名 |
> > | 安全网关 MIME 重组 | ❌ 断裂 | MIME 结构变更 | 网关在签名之前扫描 |
> > | .forward 邮箱转发 | ✅ 正常 | 信封修改不影响 DKIM | — |
> > | SRS 信封重写 | ✅ 正常 | DKIM 不关心信封 | — |
> > | 邮件正文 Base64 → QP 转码 | ❌ 断裂 | 正文编码变更影响 bh= | 禁止中间 MTA 转码 |
> > | DNS TXT 记录不存在 | ❌ 失败 | Selector 不存在或 DNS 故障 | 检查 DNS 发布状态 |
> > | 公钥长度不足（1024 位） | ❌ 被拒绝 | RFC 8301 强制要求 ≥1024 位但建议 ≥2048 | 升至 2048+ 位 RSA |
> > | 时钟偏差（t= / x= 范围外） | ❌ 过期 | MTA 系统时间不同步 | NTP 同步 + 合理的 x= |
> >
> > ## 十二、总结
> >
> > DKIM 是邮件认证体系中承上启下的关键环节。它用密码学签名填补了 SPF 在转发和邮件列表场景下的断链，为 DMARC 提供了 Identifier Alignment 的基础。RFC 6376 定义了一套完整且灵活的框架——从规范化算法（Simple / Relaxed）到 Selector 分层的密钥管理，再到 t=/x=/l= 的签名范围控制——每一个设计决策背后都对应着现实运维中的具体痛点。
> >
> > 几个不容妥协的原则：
> >
> > * **RSA 密钥至少 2048 位**
> >   ，推荐 3072 位。1024 位在 2026 年已经不安全（RFC 8301）。
> > * **c=relaxed/relaxed**
> >   为标准配置。simple 正文规范化对任何后追加内容都零容忍。
> > * **不使用 l=**
> >   ，除非你的邮件列表架构明确需要它并在安全评估中接受了相应风险。
> > * **实施 Oversigning**
> >   ——对 From、Subject、To 等关键头部至少签入一个空实例。
> > * **Ed25519 作为前瞻性部署**
> >   ：密钥更短、签名更快、DNS 记录不超长。双签名（RSA + Ed25519）是最稳健的过渡策略。
> > * **DMARC 的对齐校验不可省略**
> >   ——没有 DMARC，DKIM 的 d= 域可以是任意域，无法阻止跨域冒充。
> >
> > DKIM 不是万能的。它不加密邮件（那是 S/MIME 和 PGP 的事），不提供传输安全性（那是 STARTTLS / DANE 的事），也不定义策略（那是 DMARC 的事）。它只做一件事：让接收方能够以密码学方式确认邮件在签名后未被篡改，且签名域声明了对内容负责。正确理解这个边界，是把 DKIM 用到极致的前提。
> >
> > **参考来源：**
> >   
> > [1] IETF RFC 6376 — DomainKeys Identified Mail (DKIM) Signatures, September 2011
> >   
> > [2] IETF RFC 8463 — A New Cryptographic Signature Method for DKIM (Ed25519-SHA256), September 2018
> >   
> > [3] IETF RFC 7489 — Domain-based Message Authentication, Reporting, and Conformance (DMARC), March 2015
> >   
> > [4] IETF RFC 5322 — Internet Message Format, October 2008
> >   
> > [5] IETF RFC 8301 — Cryptographic Algorithm and Key Usage Update to DKIM, January 2018
> >   
> > [6] IETF RFC 7208 — Sender Policy Framework (SPF) for Authorizing Use of Domains in Email, April 2014
> >   
> > [7] Trusted Domain Project — OpenDKIM Documentation
> >   
> > [8] dkimpy — Python DKIM signing & verification library
> >   
> > [9] NIST SP 800-177 Rev.1 — Trustworthy Email, February 2019
> >
> > ### 相关文章
> >
> > [SPF记录配置详解](/kb/spf-guide.html)
> > [DMARC完整部署指南](/kb/dmarc-guide.html)
> > [邮件认证报告解读 — DMARC、parsedmarc](/kb/email-auth-reporting.html)
> > [SPF / DKIM / DMARC 三合一部署检查清单](/kb/spf-dkim-dmarc-checklist.html)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/dkim-guide.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
