---
title: "邮件传输加密深度解析 — STARTTLS、DANE TLSA 与 MTA-STS 三位一体防护体系 · ztpop 邮件技术知识库"
source: "https://ztpop.net/kb/tls-email-encryption.html"
license: CC-BY 4.0
---

# 邮件传输加密深度解析 — STARTTLS、DANE TLSA 与 MTA-STS 三位一体防护体系 · ztpop 邮件技术知识库

邮件传输加密深度解析 — STARTTLS、DANE TLSA 与 MTA-STS 三位一体防护体系

#### 📑 目录

1. [邮件加密的三个层面](#s1)
2. [STARTTLS：机会加密的基石](#s2)
3. [STRIPTLS 降级攻击与三种防御路径](#s3)
4. [DANE TLSA：基于 DNSSEC 的证书绑定](#s4)
5. [MTA-STS 与 TLS-RPT：策略分发与失败监控](#s5)
6. [DANE 与 MTA-STS 协同部署](#s6)
7. [TLS 1.3 vs TLS 1.2：握手与密码套件](#s7)
8. [证书管理实践](#s8)
9. [互操作性问题与老旧 MTA 兼容](#s9)
10. [Postfix smtp\_tls\_security\_level 五级详解](#s10)
11. [动手实践：诊断与验证](#s11)

## 一、邮件加密的三个层面

把邮件加密的完整链路摊开来看，实际上存在
**三个相互独立的安全边界**
。理解这三个层面的差异，是弄清楚 STARTTLS、DANE 和 MTA-STS 各自解决什么问题的前提。

一、邮件加密的三个层面

| 加密层面 | 保护范围 | 典型协议 | 特点 |
| --- | --- | --- | --- |
| MTA → MTA 传输加密 | 发件服务器到收件服务器之间的 SMTP 会话 | SMTP + STARTTLS (端口 25) | 逐跳（hop-by-hop）；邮件在两端服务器上仍为明文存储 |
| MUA → MTA 提交加密 | 邮件客户端到发件服务器的提交链路 | SMTP Submission (端口 587/465) | RFC 8314 已将明文提交标记为过时 |
| 端到端加密 (E2EE) | 发件人设备到收件人设备，全程密文 | OpenPGP / S/MIME | 邮件服务器无法解密正文；部署门槛最高 |

本文聚焦第一层面——MTA 到 MTA 的传输加密。这是邮件在互联网上跳转时最容易被窃听和篡改的环节，也是 STARTTLS、DANE 与 MTA-STS 三种机制共同防御的战场。

## 二、STARTTLS：机会加密的基石

### 2.1 协议定义与演进

STARTTLS 由
**RFC 3207**
（SMTP Service Extension for Secure SMTP over TLS）于 2002 年定义。其设计思路在当时看来非常务实：SMTP 会话默认以明文开始，客户端发送
`EHLO`
后，若服务器在响应中通告了
`250-STARTTLS`
，客户端即可发出
`STARTTLS`
命令，双方在此之后协商 TLS 握手，将会话升级为加密通道。

这条路径在端口 25 上运行了二十多年，至今仍是互联网邮件传输加密的主要方式。但它的安全模型存在一个根本性弱点——
**STARTTLS 是机会式（opportunistic）的**
。如果中间人拦截了
`EHLO`
响应中的
`250-STARTTLS`
通告，或在 TCP 层剥离 TLS 协商报文，双方的通信就会退化回明文，且收发两端都无感知。

到了 2018 年，IETF 在
**RFC 8314**
中明确表态：邮件提交和访问应使用隐式 TLS（Implicit TLS），即 TCP 连接建立后立即进入 TLS 握手，不再依赖 STARTTLS 升级。这一规范将端口 465（submissions）和 993（IMAPS）、995（POP3S）确立为首选方案，明文提交被标记为"过时"（Cleartext Considered Obsolete）。

### 2.2 验证 STARTTLS 协商

用
`openssl s_client`
可以直接模拟 SMTP STARTTLS 流程，查看对端证书链和协商的密码套件：

```
openssl s_client -starttls smtp -connect mx.example.com:25 -servername example.com 2>&1 \
  | openssl x509 -noout -dates -subject -issuer -fingerprint -sha256
```

如仅需查看 TLS 协商结果而不做证书验证，可以加上
`-verify_return_error`
或省略管道后的 x509 过滤，直接在标准输出中阅读
`SSL handshake has read`
之后的完整协商信息。

对于需要检查特定密码套件连通性的场景：

```
openssl s_client -starttls smtp -connect mx.example.com:25 \
  -cipher 'ECDHE-RSA-AES256-GCM-SHA384' -tls1_2
```

上述命令限定了 TLS 1.2 和特定密码套件，可用于验证对端 MTA 是否支持你期望的安全参数。若连接被拒绝或握手失败，日志中会有对应的
`alert`
级别错误。

## 三、STRIPTLS 降级攻击与三种防御路径

### 3.1 攻击原理

STRIPTLS（也称为 STARTTLS 剥离攻击）是 SMTP 机会加密面临的最直接威胁。攻击者处于 MTA 之间的网络路径上，拦截客户端发出的
`EHLO`
后的服务器响应，移除其中的
`250-STARTTLS`
行，使客户端认为对端不支持 TLS，从而以明文继续通信。在此之后，攻击者可以完整读取 SMTP 会话内容——包括邮件正文、发件人和收件人地址。

由于 STARTTLS 在 RFC 3207 中被设计为可选扩展，MTA 默认不强制加密，STRIPTLS 在现实的互联网邮件传输中并非理论攻击。Google 的邮件透明性报告曾显示，2015 年前后从 Gmail 发出的邮件中约有 20% 在传输途中经过了未加密的跳转。虽然这一比例近年持续下降，但根源在于 STARTTLS 自身的设计缺陷：
**缺乏加密强制机制和证书验证的信任锚**
。

### 3.2 三种防御机制对比

针对 STRIPTLS，目前形成了三种独立的防御体系。它们在信任锚、部署依赖和防护粒度上各有侧重：

3.2 三种防御机制对比

| 防御机制 | 信任锚 | 强制加密 | 证书验证 | 部署依赖 | 标准 |
| --- | --- | --- | --- | --- | --- |
| STARTTLS 纯机会加密 | 无（可选时用，不可用时降级明文） | ❌ | ❌ | 无 | RFC 3207 |
| DANE TLSA | DNSSEC 签名链 → DNS 根 | ✅（通过 TLSA 记录强制） | ✅（TLSA 绑定证书/公钥指纹） | 域名必须启用 DNSSEC | RFC 7672 |
| MTA-STS | Web PKI（公共 CA 证书链） | ✅（通过 HTTPS 策略声明） | ✅（标准 CA 证书验证） | 需部署 HTTPS 站点 + DNS TXT 记录 | RFC 8461 |

需要特别指出的是，
**DANE 和 MTA-STS 并不是互斥的替代方案，而是可以叠加使用的互补机制**
。两者在不同信任模型下解决同一个问题——让发件 MTA 有能力
**验证收件 MTA 的 TLS 证书是否合法**
，并在证书验证失败时拒绝投递（而非降级为明文）。

## 四、DANE TLSA：基于 DNSSEC 的证书绑定

### 4.1 信任模型：摆脱 CA 依赖

DANE（DNS-Based Authentication of Named Entities）的核心思想载于
**RFC 6698**
，而将其应用于 SMTP 的规范是
**RFC 7672**
。RFC 7672 在第 1 节明确指出，SMTP 中的 DANE 旨在解决两个核心问题：一是 STARTTLS 的机会加密无法防止降级攻击；二是在没有共同信任的 CA 之前，无法验证对端 MTA 证书的真伪。

DANE 的信任链不依赖任何证书颁发机构。它的信任锚是 DNSSEC——从 DNS 根区开始，经过逐层签名验证，到达目标域名的 TLSA 记录。这意味着
**域名的所有者自己决定哪些证书（或公钥）是合法的**
，不需要第三方 CA 的背书。RFC 7672 第 1.2 节将这一模型称为"基于 DNS 的命名实体认证"，与 Web PKI 体系形成根本性的架构差异。

### 4.2 TLSA 记录格式

TLSA 记录的结构由四个字段组成：
**端口号、协议、主机名、关联数据**
。其中关联数据部分又分为三个子字段：

4.2 TLSA 记录格式

| 字段 | 名称 | 取值 | 含义 |
| --- | --- | --- | --- |
| Certificate Usage | usage | 0 / 1 / 2 / 3 | 0=CA约束(PKIX-TA), 1=服务证书(PKIX-EE), 2=信任锚(TA), 3=域颁发证书(DANE-EE) |
| Selector | selector | 0 / 1 | 0=完整证书, 1=仅 SubjectPublicKeyInfo (SPKI) |
| Matching Type | matching | 0 / 1 / 2 | 0=完整匹配, 1=SHA-256, 2=SHA-512 |

RFC 7672 第 3.1 节对 SMTP 场景下的 TLSA 用法给出了明确指引：
**usage 字段推荐取值为 2（DANE-TA）或 3（DANE-EE）**
，原因是 SMTP 的 TLS 连接中没有 SNI 机制可用于在 PKIX 模式下匹配主机名。usage=3 (DANE-EE) 是当前社区最推荐的模式——直接将服务端证书或公钥的指纹绑入 DNS，验证路径最短，不依赖任何外部 CA。

一个典型的 TLSA 记录示例：

```
_25._tcp.mx.example.com.  IN  TLSA  3 1 1 (
  2a0b6f8c3d1e45907f82b1c5a93e6d4f70821e35b9ca63d2
  f40e51837a26b9c1 )
```

解读：usage=3 (DANE-EE)，selector=1 (SPKI 公钥)，matching=1 (SHA-256)。这意味着收件 MTA 的公钥（SubjectPublicKeyInfo）的 SHA-256 指纹必须等于该值，才视为合法。

### 4.3 查询与验证

使用
`dig`
命令查询一个域名的 TLSA 记录（需要递归 DNS 支持 DNSSEC 验证）：

```
dig +dnssec +short _25._tcp.mx.example.com TLSA
```

`+dnssec`
参数会同时返回 RRSIG 签名记录，用于确认该 TLSA 记录确实经过了有效的 DNSSEC 签名。如果返回为空，说明该域未配置 DANE；如果返回的数据中缺少 RRSIG，则该 TLSA 记录存在但未受 DNSSEC 保护，按 RFC 7672 第 5 节的规定，此时 MTA 不应信任该 TLSA 记录。

### 4.4 使用 posttls-finger 获取证书指纹

`posttls-finger`
是 Postfix 附带的 TLS 指纹工具，用于探测对端 MTA 的 TLS 证书并计算可用于 TLSA 记录的指纹值：

```
posttls-finger -c -L summary -l secure -P "match=._25._tcp.mx.example.com" mx.example.com
```

该命令连接目标 MTA 的 25 端口，完成 STARTTLS 升级，提取对端证书链和公钥信息，输出可直接写入 TLSA 记录的指纹。RFC 7672 第 7 节建议在首次部署 DANE 时，用该工具或多条路径独立验证对端证书，防止中间人攻击篡改首次指纹采集。

### 4.5 SMTP 客户端的 DANE 验证流程

RFC 7672 第 4 节详细描述了 SMTP 客户端执行 DANE 验证的完整流程：

发件 MTA 在需要向
`recipient@example.com`
投递邮件时，先查询该域的 MX 记录获得目标 MTA 主机名；然后对该主机名构造
`_25._tcp.`
格式的 TLSA 查询；若查询返回了受 DNSSEC 保护的 TLSA 记录，则发起 TLS 连接后进行证书/公钥匹配——匹配成功的条件取决于 TLSA 中的 usage/selector/matching 三元组。验证通过后才投递邮件，失败则根据安全策略退回或延迟重试。

> **RFC 7672 关于回退行为的约束**
> ：第 5.1 节明确规定，如果 TLSA 记录查询因 DNSSEC 验证失败而不可用（bogus 状态），发件 MTA 应将该连接视为不安全并拒绝投递，不得回退为机会加密。只有在安全策略显式允许（如 Postfix 的
> `smtp_tls_security_level = dane`
> 只对支持 DANE 的域生效）时，才允许对未配置 TLSA 的域走机会加密路径。

### 4.6 生成 TLSA 记录的实际操作

生成 usage=3, selector=1, matching=1 的 TLSA 记录，需要提取证书公钥的 SHA-256 指纹：

```
openssl x509 -in /etc/ssl/certs/mx-cert.pem -noout -pubkey \
  | openssl pkey -pubin -outform DER \
  | openssl dgst -sha256 -hex \
  | awk '{print $2}'
```

得到 64 位十六进制指纹后，将其写入 DNS 区域文件：

```
_25._tcp.mx  IN  TLSA  3 1 1
```

这里有一个容易忽略的细节：
**TLSA 记录绑定的主机名是 MX 记录指向的 MTA 主机名，而非收件人域名本身**
。例如
`example.com`
的 MX 指向
`mx1.mailhost.com`
，则 TLSA 应挂在
`_25._tcp.mx1.mailhost.com`
而非
`_25._tcp.example.com`
。RFC 7672 第 2.1 节对此有明确说明。

## 五、MTA-STS 与 TLS-RPT：策略分发与失败监控

### 5.1 MTA-STS 的信任模型

MTA-STS（SMTP MTA Strict Transport Security）由
**RFC 8461**
定义，于 2018 年发布。与 DANE 相反，MTA-STS 选择站在 Web PKI 的肩膀上：
**通过 HTTPS 从收件域名的 Web 服务器获取策略文件**
，策略中声明该域要求 TLS 加密的 MX 主机列表。

MTA-STS 的信任模型是这样的：发件 MTA 通过 HTTPS 访问
`https://mta-sts./.well-known/mta-sts.txt`
，验证 Web 服务器证书链是否有效（与浏览器验证 HTTPS 网站的流程相同），然后解析策略文件中的指令。策略文件中定义了
`mx`
主机列表和
`mode`
字段。当
`mode`
为
`enforce`
时，发件 MTA 必须验证收件 MTA 的证书——验证方式与传统 Web PKI 一致（信任公共 CA 颁发的证书，且证书 SAN 字段需覆盖 MX 主机名）。验证失败则拒绝投递。

### 5.2 DNS 记录与策略文件

MTA-STS 的部署需要两步：首先是 DNS 中设置一条 TXT 记录指示策略存在，其次是在 HTTPS 端点上提供策略文件内容。

DNS 记录格式（
`_mta-sts.example.com`
）：

```
_mta-sts.example.com.  IN  TXT  "v=STSv1; id=2026070401;"
```

`id`
字段是策略版本标识，通常使用时间戳格式。发件 MTA 通过对比
`id`
值来判断策略是否更新，避免每次连接都发起 HTTPS 请求。

策略文件内容（
`https://mta-sts.example.com/.well-known/mta-sts.txt`
）：

```
version: STSv1
mode: enforce
mx: mx1.example.com
mx: mx2.example.com
max_age: 604800
```

各字段含义：

5.2 DNS 记录与策略文件

| 字段 | 含义 | 典型值 |
| --- | --- | --- |
| version | 协议版本，固定为 STSv1 | STSv1 |
| mode | 策略模式：testing（仅报告）/ enforce（强制执行）/ none（撤销策略） | testing 或 enforce |
| mx | 允许的收件 MX 主机名，必须与域名的 MX 记录匹配 | 全限定主机名 |
| max\_age | 策略缓存时长（秒），超过后重新拉取 | 604800（7天）至 31536000（1年） |

部署建议先使用
`mode: testing`
运行至少两周，通过 TLS-RPT 报告确认所有合法发件 MTA 都能正常完成证书验证，再切换到
`mode: enforce`
。

### 5.3 TLS-RPT：加密失败的可视化

光有策略还不够。如果收件域部署了 MTA-STS 的 enforce 模式却不知道有多少邮件因为证书不匹配被拒收，运维就成了瞎子。
**RFC 8460**
定义的 TLS-RPT（SMTP TLS Reporting）正好填补了这个盲区。

部署 TLS-RPT 只需在 DNS 中添加一条记录：

```
_smtp._tls.example.com.  IN  TXT  "v=TLSRPTv1; rua=mailto:tls-reports@example.com"
```

支持 MTA-STS 的发件 MTA 在每次投递（无论成功或失败）后，会在 24 小时内汇总为一份 JSON 报告发送到
`rua`
地址。报告结构如下（简化样例）：

```
{
  "organization-name": "sender.example.net",
  "date-range": { "start-datetime": "2026-07-03T00:00:00Z",
                   "end-datetime": "2026-07-03T23:59:59Z" },
  "policies": [{
    "policy": {
      "policy-type": "sts",
      "policy-string": ["version: STSv1", "mode: enforce", ...],
      "policy-domain": "example.com",
      "mx-host": ["mx1.example.com"]
    },
    "summary": {
      "total-successful-session-count": 3847,
      "total-failure-session-count": 12
    },
    "failure-details": [{
      "result-type": "certificate-expired",
      "sending-mta-ip": "203.0.113.10",
      "receiving-mx-hostname": "mx1.example.com",
      "failed-session-count": 3
    }]
  }]
}
```

失败详情中会指明失败原因——
`certificate-expired`
、
`certificate-not-trusted`
、
`starttls-not-supported`
等。
**这份报告是部署 MTA-STS 从 testing 升级到 enforce 的关键决策依据**
。如果在 testing 阶段报告中出现了合法发件方的失败记录，说明对方 MTA 的证书配置有问题，应先沟通修复再升级模式。

### 5.4 MTA-STS 的局限性

MTA-STS 有几个值得注意的局限。其一，策略缓存依赖
`max_age`
参数，如果域名的证书在缓存期内被吊销，发件 MTA 仍会按缓存策略信任原 MX 列表，直到
`max_age`
到期才重新拉取。其二，HTTPS 策略端点本身也可能成为攻击目标——如果收件域的 Web 服务器被攻陷，攻击者可以修改策略文件内容。其三，MTA-STS 依赖 Web PKI，这意味着你的收件域必须具备一个受公共 CA 信任的 HTTPS 证书。对于小型组织，这通常不是问题（利用 Let's Encrypt 的免费自动化证书即可），但需要确保 Web 服务器的证书和 MTA 的证书由同一个团队管理。

## 六、DANE 与 MTA-STS 协同部署

### 6.1 优先级与并存

当一个收件域同时部署了 DANE 和 MTA-STS，发件 MTA 的决策逻辑涉及先后顺序问题。根据 RFC 8461 第 5 节和 RFC 7672 第 4 节的交叉来看，当前的主流 MTA 实现（Postfix ≥ 3.4、Exim ≥ 4.92）采用的优先级是：
**如果域同时启用了 DANE 和 MTA-STS，DANE 的验证结果优先**
。原因在于 DANE 的信任锚（DNSSEC）在技术层面更"硬"——由域主直接控制，不像 MTA-STS 那样多一层 HTTPS 跳转和 CA 信任。

但这并不意味着应该二选一。两者的覆盖面和安全特性有差异：

6.1 优先级与并存

| 维度 | DANE | MTA-STS |
| --- | --- | --- |
| 信任锚 | DNSSEC 签名链 | Web PKI |
| 证书绑定精度 | 精确到证书或公钥指纹 | PKIX 标准验证（信任链 + 主机名匹配） |
| 部署门槛 | 需域名启用 DNSSEC | 需 Web 服务器 + 公共证书 |
| 策略传达 | TLSA 存在即策略（隐含强制） | 显式 mode: testing/enforce |
| 失败监控 | 无内置报告机制 | TLS-RPT（RFC 8460） |
| 回退风险 | DNSSEC 被strip则全部失效 | HTTPS 被拦截或策略缓存过期 |

最佳实践是
**同时部署两者**
：DANE 提供最精确的证书绑定（阻止任何伪造证书），MTA-STS 提供策略分发和统一的失败监控（TLS-RPT 报告）。两者叠加后，攻击者需要同时绕过 DNSSEC 签名验证和 Web PKI 验证才有机会成功进行中间人攻击——这种威胁模型下，攻击的成本已经被抬高到大多数场景中不可行的程度。

### 6.2 DANE + MTA-STS 协同验证流程

当发件 MTA 需要向
`example.com`
投递邮件时，完整的 DANE + MTA-STS 协同验证逻辑如下：

```
1. 查询 MX 记录 → 获得 mx1.example.com (优先级 10)
2. 查询 _mta-sts.example.com TXT → 策略 id 为 2026070401
3. 对比缓存：若 id 未变且缓存未过期 → 使用缓存策略；否则拉取 HTTPS 策略
4. 查询 _25._tcp.mx1.example.com TLSA → 若存在且 DNSSEC 有效 →
   a. STARTTLS 连接
   b. 提取对端证书/公钥
   c. 按 TLSA 中的 usage/selector/matching 匹配
   d. 匹配成功 → DANE 验证通过，直接投递
   e. 匹配失败 → 拒绝投递（不降级）
5. 若无 TLSA 或 DNSSEC 无效 → 回退到 MTA-STS 策略：
   a. 若 mode=enforce → 验证证书 PKIX（信任链 + SAN 匹配）
      ✓ 通过 → 投递 | ✗ 失败 → 拒绝
   b. 若 mode=testing → 验证证书但失败不拒绝，只记入 TLS-RPT 报告
6. 若无 TLSA 且无 MTA-STS → 传统机会加密
```

这里有一个关键细节：步骤 4 中，TLSA 的存在直接绕过 MTA-STS 的 PKIX 验证。也就是说
**DANE 验证一旦启动，就不再查看证书是否由公共 CA 签发**
——你完全可以用自签名证书，只要它的指纹与 TLSA 记录匹配即可。这是 DANE 对邮件运维最实际的解放。

## 七、TLS 1.3 vs TLS 1.2：握手与密码套件

### 7.1 握手性能：从 2-RTT 到 1-RTT

TLS 1.2 的完整握手（以 ECDHE 密钥交换为例）需要两次往返：ClientHello → ServerHello + Certificate + ServerKeyExchange → ClientKeyExchange + ChangeCipherSpec + Finished → ChangeCipherSpec + Finished。每个 RTT 在跨洲际 SMTP 场景中可能耗时 100-300ms，这意味着仅 TLS 握手就给每封邮件的投递增加了几百毫秒的延迟。

TLS 1.3 将握手压缩为一轮：ClientHello 中直接携带密钥共享（Key Share）参数，ServerHello 中返回选定的密码套件和服务器密钥共享，随后立即进入加密的应用数据交换。在会话复用场景下，TLS 1.3 甚至可以做到 0-RTT——客户端在第一条消息中就附带早期数据（early data），不过这个特性在 SMTP 中需要谨慎使用，因为 0-RTT 数据不具备前向安全性，且容易被重放。

在 SMTP 的语境下，
**1-RTT 握手带来的性能提升虽然存在，但不是决定性因素**
。SMTP 本身是异步存储转发协议，单封邮件的传输延迟在秒级到分钟级，TLS 握手省下的几百毫秒
**在大批量出站时可以累积为显著效果**
——一个日发十万封邮件的出站 MTA，如果每次握手节省 200ms，全天可以节省约 5.5 小时的总握手时间。

### 7.2 密码套件对比

NIST SP 800-52 Rev.2（Guidelines for the Selection, Configuration, and Use of TLS Implementations）为联邦信息系统提供了 TLS 配置的最低安全要求。将 NIST 的建议映射到 SMTP 场景中，以下是常用密码套件对照：

7.2 密码套件对比

| 协议版本 | 密码套件 | 密钥交换 | 加密算法 | 完整性 | PFS |
| --- | --- | --- | --- | --- | --- |
| TLS 1.3 | TLS\_AES\_256\_GCM\_SHA384 | ECDHE | AES-256-GCM (AEAD) | AEAD 内置 | ✅ |
| TLS 1.3 | TLS\_AES\_128\_GCM\_SHA256 | ECDHE | AES-128-GCM (AEAD) | AEAD 内置 | ✅ |
| TLS 1.3 | TLS\_CHACHA20\_POLY1305\_SHA256 | ECDHE | ChaCha20-Poly1305 (AEAD) | AEAD 内置 | ✅ |
| TLS 1.2 | ECDHE-RSA-AES256-GCM-SHA384 | ECDHE | AES-256-GCM (AEAD) | AEAD 内置 | ✅ |
| TLS 1.2 | ECDHE-ECDSA-AES128-GCM-SHA256 | ECDHE | AES-128-GCM (AEAD) | AEAD 内置 | ✅ |

TLS 1.3 相比 1.2 的最大改变在于：移除了所有不使用 AEAD 的密码套件（包括 CBC 模式和 RC4），移除了静态 RSA 密钥交换（因此所有 TLS 1.3 连接都天然具备 PFS），并将整个密码套件的协商从四个独立参数简化为一个组合标识符。在 SMTP 的配置中，TLS 1.3 的密码套件选择几乎不需要手动干预——
`TLS_AES_256_GCM_SHA384`
和
`TLS_AES_128_GCM_SHA256`
是强制实现项，任何符合规范的 TLS 1.3 实现都必须支持。

### 7.3 禁用过时协议版本和密码

NIST SP 800-52 Rev.2 明确要求：TLS 1.0 和 1.1 不应再用于政府系统。在 SMTP 场景中，虽然互联网上仍存在大量运行 TLS 1.0 的老旧 MTA，但出站 MTA 的配置应当主动禁用这些版本：

```
smtp_tls_protocols = !SSLv2, !SSLv3, !TLSv1, !TLSv1.1
smtp_tls_ciphers = high
smtp_tls_mandatory_protocols = !SSLv2, !SSLv3, !TLSv1, !TLSv1.1
smtp_tls_mandatory_ciphers = high
```

**RFC 8998**
正式定义了在 TLS 1.3 中使用国密算法（SM2/SM3/SM4）的密码套件。如果你的 MTA 需要与仅支持国密的国内邮件系统互通，可以通过 OpenSSL 的国密引擎（如 BabaSSL 或 Tongsuo）来支持。不过在当前互联网邮件传输的现实场景中，ECDHE + AES-GCM 仍是全球互操作性最好的组合。

## 八、证书管理实践

### 8.1 DV / OV / EV 证书的选择

三种类型的证书在 MTA 场景中的适用性差异很大：

8.1 DV / OV / EV 证书的选择

| 类型 | 验证方式 | 签发速度 | MTA 适用性 |
| --- | --- | --- | --- |
| DV (Domain Validated) | 验证域名控制权（HTTP/DNS 挑战） | 秒级 | ✅ 完全够用。STARTTLS 和 DANE 都不依赖证书中的组织信息 |
| OV (Organization Validated) | 验证域名 + 组织信息 | 小时到天 | 可选。加入证书透明日志（CT Log）提供额外可见性 |
| EV (Extended Validation) | 深度组织验证 | 天到周 | ❌ 不需要。SMTP 客户端不展示 EV 绿条，EV 证书在邮件传输中无额外价值 |

结论很简单：
**MTA 用 DV 证书足够了**
。Let's Encrypt 提供的免费 DV 证书完全满足 STARTTLS、DANE 和 MTA-STS 的全部证书要求。

### 8.2 SAN 多域名与通配符证书

如果一个组织有多个 MX 主机（如
`mx1.example.com`
、
`mx2.example.com`
），有两类方案：

**方案 A — SAN 多域名证书**
：在单个证书的 Subject Alternative Name 扩展中列出所有 MX 主机名。优点是管理集中，证书续期只需要操作一次；缺点是每次增加 MX 需要重新签发证书。

```
# 签发时指定 SAN 列表
certbot certonly --standalone \
  -d mx1.example.com -d mx2.example.com -d mx3.example.com
```

**方案 B — 各 MX 独立证书**
：每个 MX 主机维护自己的证书。优点是在 DANE 场景下更容易做精确的逐主机指纹绑定；缺点是多台主机的证书续期需要分别管理。

通配符证书（
`*.example.com`
）虽然可以覆盖所有 MX 子域，但安全影响范围更大——一旦私钥泄露，攻击者可以冒充该域下的任何主机。在 MTA 场景中，
**不建议使用通配符证书**
，DANE 的逐主机 TLSA 绑定模式天然倾向于独立证书。

### 8.3 自动化续期

Let's Encrypt 证书有效期仅 90 天，自动化续期不是可选项而是必选项。以下是一个典型的 certbot 续期 + Postfix 重载的部署实例：

```
# /etc/cron.d/certbot-renew
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

# 每日凌晨 3:15 尝试续期
15 3 * * * root certbot renew --quiet --deploy-hook "systemctl reload postfix dovecot"
```

`--deploy-hook`
只在证书实际更新时才触发，避免每天无谓地重启服务。同时配置证书路径，确保 Postfix 始终指向 certbot 维护的 live 目录（符合符号链接跟随）：

```
smtpd_tls_cert_file = /etc/letsencrypt/live/mx.example.com/fullchain.pem
smtpd_tls_key_file  = /etc/letsencrypt/live/mx.example.com/privkey.pem
```

这里有个关键细节：使用
`fullchain.pem`
而不是
`cert.pem`
。
`fullchain.pem`
包含完整的证书链（服务器证书 + 中间 CA），而
`cert.pem`
仅含服务器证书。一些老旧 MTA 可能没有内置完整的中间 CA 证书库，缺少中间证书会导致对方验证失败。

## 九、互操作性问题与老旧 MTA 兼容

### 9.1 现实世界的 TLS 版本分布

尽管理想状态下所有 MTA 应该运行 TLS 1.2 或 1.3，但实际情况中仍存在大量历史遗留。互联网邮件传输的去中心化特性决定了
**你不能控制对方 MTA 的软件版本和配置**
。一份来自邮件安全社区的统计显示，截至 2025 年末，端口 25 上仍有约 3%-5% 的 MTA 不支持 TLS 1.2，约 0.5% 的 MTA 完全不支持任何版本的 STARTTLS。

这意味着如果你的出站 MTA 配置了
`smtp_tls_security_level = encrypt`
（要求所有出站连接必须加密），大约每 200-300 封邮件中就会有一封无法投递——不是对方拒收，而是你的 MTA 因为无法建立加密连接而直接放弃。

### 9.2 TLS 1.0 残留与 RC4 禁用

TLS 1.0（1999 年发布）和 TLS 1.1（2006 年发布）已于 2021 年被 IETF 正式弃用（RFC 8996）。但弃用不等于消失——某些嵌入式邮件网关和企业自建 MTA 至今仍只支持 TLS 1.0。

对入站（smtpd）而言，可以严格限制协议版本：

```
smtpd_tls_protocols = !SSLv2, !SSLv3, !TLSv1, !TLSv1.1
smtpd_tls_mandatory_protocols = !SSLv2, !SSLv3, !TLSv1, !TLSv1.1
```

但对出站（smtp）则需要权衡：禁掉 TLS 1.0 意味着放弃与这些老旧 MTA 的通信。折中做法是使用
`smtp_tls_security_level = may`
（机会加密），允许在对方不支持 TLS 时降级明文，同时通过 TLS-RPT 或日志监控这些明文连接的比例。

关于 RC4：该算法早在 2015 年就被 RFC 7465 禁止在 TLS 中使用。任何现代 MTA 都应在 Cipher 配置中排除 RC4：

```
smtpd_tls_ciphers = high
smtpd_tls_exclude_ciphers = RC4, aNULL, MD5, DES, 3DES, EXP, PSK, SRP
smtp_tls_ciphers = high
smtp_tls_exclude_ciphers = RC4, aNULL, MD5, DES, 3DES, EXP, PSK, SRP
```

### 9.3 证书链完整性

互操作性问题中，最常见的一类是证书链不完整导致的 TLS 握手失败。当 MTA A 的证书缺少中间 CA 证书时，MTA B 可能无法构建到根 CA 的完整信任链。检查方法是：

```
openssl s_client -starttls smtp -connect mx.example.com:25 \
  -showcerts 2>&1 | grep -E '^( 0 s:| 1 s:| 2 s:|subject=|issuer=)'
```

正常情况下应看到至少两层（服务器证书 → 中间 CA），且最底层的
`issuer`
应指向一个常见的根 CA（如 ISRG Root X1 或 DigiCert Global Root CA）。如果只显示一层（服务器证书的 issuer 直接指向根 CA 而没有中间层），在某些 MTA 的证书库中这会造成验证失败。

## 十、Postfix smtp\_tls\_security\_level 五级详解

Postfix 的
`smtp_tls_security_level`
参数是控制出站 TLS 行为的核心配置。理解这五个级别的差异及其适用场景，是部署邮件加密策略的实操基础：

十、Postfix smtp\_tls\_security\_level 五级详解

| 级别 | 行为 | 证书验证 | 降级行为 | 适用场景 |
| --- | --- | --- | --- | --- |
| `none` | 不使用 TLS。即使对端通告 STARTTLS 也忽略 | 无 | 始终明文 | 调试环境、内网受控网络 |
| `may` | 机会加密。对端通告 STARTTLS 则升级，否则明文 | 不验证证书（可选验证但不强制） | 对端不支持 TLS 时自动降级明文 | 通用出站（默认值）；追求最大送达率的场景 |
| `encrypt` | 要求加密。必须协商 TLS，但不验证证书 | 不验证 | 对端不支持 TLS 时拒绝投递 | 基本安全需求；不要求证书合法性 |
| `dane` | DANE 模式。对已配置 TLSA 的域执行 DANE 验证，其他域走 may | 对 DANE 域：按 TLSA 记录匹配证书/公钥指纹 | DANE 域失败拒绝；非 DANE 域可降级 | 生产环境推荐；兼顾安全与兼容 |
| `dane-only` | 严格 DANE。只向支持 DANE 的域投递加密邮件 | 强制 DANE 验证 | 非 DANE 域直接拒绝 | 高安全环境；适用范围窄 |
| `fingerprint` | 证书指纹匹配。通过 `smtp_tls_fingerprint_cert_match` 指定 | 按预配置的指纹匹配特定目的域 | 不匹配拒绝 | 对特定合作伙伴域名做精确绑定 |
| `verify` | 强制 PKIX 验证。要求对端证书通过公共 CA 链验证 | 标准 PKIX | 验证失败拒绝 | 配合 MTA-STS 的 enforce 模式 |
| `secure` | 强制加密 + PKIX 验证。组合 encrypt 和 verify | 标准 PKIX | 无加密或验证失败都拒绝 | 最高安全要求；牺牲互操作性 |

实际部署中，最常见的组合是：

```
smtp_tls_security_level = dane
smtp_tls_CAfile = /etc/ssl/certs/ca-certificates.crt
smtp_dns_support_level = dnssec
```

这条配置的意思是：对支持 DANE 的域使用 DANE 验证（TLSA 指纹匹配），对其他域使用机会加密（may），同时强制系统 DNS 解析器检查 DNSSEC（
`smtp_dns_support_level = dnssec`
是 DANE 生效的前提，因为未受 DNSSEC 保护的 TLSA 记录按 RFC 7672 应被忽略）。

对于同时部署 MTA-STS 的环境，Postfix 3.4+ 可以通过外部
`mta-sts-daemon`
或内置策略来集成 MTA-STS 验证。Postfix 3.10 更直接纳入了对 TLSRPT 协议的原生支持。具体集成方式超出了本文的范围，但核心逻辑是：发件 MTA 在
`smtp_tls_security_level = dane`
的基础上，通过额外的策略查询步骤决定是否对非 DANE 域执行 PKIX 验证（即等效于
`verify`
级别）。

## 十一、动手实践：诊断与验证

### 11.1 快速检测对端 MTA 的 TLS 能力

```
# 检测是否支持 STARTTLS
echo "QUIT" | openssl s_client -starttls smtp -connect mx.example.com:25 2>&1 \
  | grep -E '(Server certificate|subject=|issuer=|Protocol|Cipher|Verify return code)'

# 输出示例:
# Protocol  : TLSv1.3
# Cipher    : TLS_AES_256_GCM_SHA384
# subject=CN = mx.example.com
# issuer=C = US, O = Let's Encrypt, CN = R11
# Verify return code: 0 (ok)
```

### 11.2 验证 DANE TLSA 配置

```
# 检查 TLSA 记录是否存在且 DNSSEC 签名有效
dig +dnssec +multi _25._tcp.mx.example.com TLSA

# 对比远端证书指纹与 TLSA 记录
openssl s_client -starttls smtp -connect mx.example.com:25 \
  -servername mx.example.com /dev/null \
  | openssl x509 -noout -pubkey \
  | openssl pkey -pubin -outform DER \
  | openssl dgst -sha256 -hex
```

### 11.3 使用 posttls-finger 做完整诊断

```
# 连接 + 验证 + 打印详情（包含证书链、TLS策略匹配状态）
posttls-finger -c -L summary -l dane mx.example.com

# 输出包含：
# - TLS 协议版本与密码套件
# - 证书链完整性和过期时间
# - DANE TLSA 匹配状态（验证通过/失败/记录不存在）
# - 信任锚信息（DNSSEC 状态、TLSA usage/selector/matching 细节）
```

### 11.4 监控邮件日志中的 TLS 信息

在生产环境中，通过日志监控 TLS 连接的版本和密码分布：

```
# 统计过去 24 小时中不同 TLS 版本的连接数
grep "TLS connection established" /var/log/maillog \
  | grep -oP 'TLSv[\d.]+' \
  | sort | uniq -c | sort -rn

# 查看使用过时协议连接的对端 IP
grep "TLSv1\b\|TLSv1\.0\b" /var/log/maillog \
  | grep -oP '\b[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+\b' \
  | sort -u
```

邮件传输加密不是一项"部署了就完成"的工作。它需要持续关注 TLS 版本分布的变化、证书的自动化续期、以及 DNS 记录的正确性。STARTTLS 提供了加密的起点，DANE 用 DNSSEC 的信任链抵御证书伪造和 STRIPTLS 降级，MTA-STS 用 Web PKI 实现了策略分发和失败可视化。三者不是互斥选项，而是从不同信任模型出发、最终汇聚在同一个目标上的互补机制——
**让互联网上每一封邮件的传输都不可被窃听和篡改**
。实现这个目标，需要运维人员既理解每个协议的信任模型，也在实际部署中做出务实的兼容性取舍。

### 参考文献

1. RFC 3207 — SMTP Service Extension for Secure SMTP over Transport Layer Security (Hoffman, 2002)
2. RFC 6698 — The DNS-Based Authentication of Named Entities (DANE) Transport Layer Security (TLS) Protocol: TLSA (Hoffman & Schlyter, 2012)
3. RFC 7672 — SMTP Security via Opportunistic DANE TLS (Dukhovni & Hardaker, 2015)
4. RFC 8314 — Cleartext Considered Obsolete: Use of TLS for Email Submission and Access (Moore & Newman, 2018)
5. RFC 8460 — SMTP TLS Reporting (Margolis et al., 2018)
6. RFC 8461 — SMTP MTA Strict Transport Security (MTA-STS) (Margolis et al., 2018)
7. RFC 8996 — Deprecating TLS 1.0 and TLS 1.1 (Moriarty & Farrell, 2021)
8. RFC 8998 — ShangMi (SM) Cipher Suites for TLS 1.3 (Yang, 2021)
9. NIST SP 800-52 Rev.2 — Guidelines for the Selection, Configuration, and Use of Transport Layer Security (TLS) Implementations (NIST, 2019)
10. RFC 5246 — The Transport Layer Security (TLS) Protocol Version 1.2 (Dierks & Rescorla, 2008)
11. RFC 8446 — The Transport Layer Security (TLS) Protocol Version 1.3 (Rescorla, 2018)
12. Postfix TLS Readme — Postfix TLS Support (Wietse Venema, postfix.org/TLS\_README.html)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/tls-email-encryption.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
