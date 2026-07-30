---
title: "DNS 安全在邮件系统中的部署"
source: "https://ztpop.net/kb/dns-security-email-deployment.html"
license: CC-BY 4.0
---

# DNS 安全在邮件系统中的部署

邮件传输依赖 DNS 解析来找到目标服务的服务器。但如果 DNS 本身被篡改或欺骗，整个邮件安全体系将形同虚设。DNSSEC、DANE 和 MTA-STS 构成了"DNS 安全层"的核心技术栈，保障邮件从发出到接收的全链路安全。

## 一、DNS 安全在邮件系统中的角色定位

邮件系统在传输过程中依赖 DNS 进行以下关键查询：

* **MX 记录查询：** 发件 MTA 通过 MX 记录找到收件域的邮件服务器
* **SPF 记录查询：** 收件方通过 SPF TXT 记录验证发件 IP 是否被授权
* **DKIM 公钥查询：** 通过 TXT 记录获取 DKIM 公钥用于验证签名
* **DMARC 策略查询：** 通过 \\_dmarc TXT 记录获取域的策略
* **TLSA 记录查询（DANE）：** 通过 TLSA 记录获取 TLS 证书的哈希值

所有这些 DNS 查询都在"明文"环境下进行（默认 DNS 协议不提供加密和完整性保护）。这意味着，**如果 DNS 响应被篡改，**攻击者可以将邮件流量劫持到自己的服务器、提供伪造的 SPF/DKIM 记录、甚至绕过 DMARC 检查。

这就是为什么 DNS 安全——具体来说是 DNSSEC、DANE 和 MTA-STS——对于邮件系统至关重要。

## 二、DNSSEC：DNS 安全的基础层

### 2.1 工作原理

DNSSEC（DNS Security Extensions，RFC 4033-4035）通过**数字签名**为 DNS 响应提供数据完整性和来源验证：

1. **区域签名：** 域管理员生成公钥-私钥对，使用私钥对区域文件中的所有 DNS 记录进行签名
2. **签名链：** 从根域（.）到顶级域（.cn、.com），再到二级域（ztpop.net），形成一条完整的信任链
3. **验证过程：** 解析器可以从根域的公钥开始，逐级验证每一级的签名，最后验证目标 DNS 记录的真实性

### 2.2 DNSSEC 记录类型

| 记录类型 | 作用 |
| --- | --- |
| RRSIG | DNS 记录的签名值，包含签名有效期、签名者信息等 |
| DNSKEY | 区域的公钥，用于验证 RRSIG |
| DS | 子域名的信任锚，父域中的 DS 记录指向子域的 DNSKEY 哈希 |
| NSEC/NSEC3 | 提供"不存在"证明（认证拒绝），防止枚举攻击 |

### 2.3 对邮件系统的价值

* **MX 记录防护：** 防止攻击者篡改 MX 记录将邮件流量劫持到恶意服务器
* **DANE 的前置条件：** 没有 DNSSEC，DANE 无法工作
* **SPF/DKIM/DMARC 查询保护：** 防止 DNS 欺骗篡改认证记录

## 三、DANE：将 TLS 证书绑定到域

### 3.1 解决的问题

传统的 TLS 证书验证依赖证书颁发机构（CA）。但 CA 生态存在众所周知的问题：任何 CA 都可以为任意域颁发证书。**DANE（DNS-based Authentication of Named Entities，基于 DNS 的命名实体认证，RFC 6698）提供了一种替代方案**——使用 DNSSEC 保护的 DNS 来声明哪些 TLS 证书是该域合法的。

### 3.2 TLSA 记录

DANE 通过在 DNS 中发布 **TLSA（TLS Association）记录**将 TLS 证书与域绑定。TLSA 记录的查询路径为：

```
_25._tcp.mail.ztpop.net. IN TLSA (3 1 1 49373BC...)
```

这条记录的含义是：

* **\_25.\_tcp：** 对应 SMTP 端口 25
* **使用方式（Usage）3：** DANE-TA（域作为信任锚，不依赖公共 CA）
* **选择器（Selector）1：** 匹配整个证书（而非公钥）
* **匹配类型（Matching Type）1：** SHA-256 哈希值

### 3.3 DANE 的邮件应用：DANE SMTP（MTA-STS 的前身）

DANE 在邮件传输中的具体应用标准是 **DANE SMTP（RFC 7672）**，它允许发件 MTA 通过 TLSA 记录验证收件邮件服务器的 TLS 证书：

1. 发件 MTA 查询收件域的 MX 记录
2. 发件 MTA 同时查询 MX 指向服务器对应的 TLSA 记录
3. 建立 TLS 连接时，收件服务器提供其证书
4. 发件 MTA 将收到的证书哈希值与 TLSA 记录中的哈希值比较
5. 匹配 → 连接继续；不匹配 → 拒绝连接

### 3.4 DANE 的优势

* **不依赖 CA 生态：** 域管理员自主控制哪些证书是合法的
* **抗 CA 劫持：** 即使恶意 CA 为你的域签发了证书，DANE 记录仍然能识别出该证书不合法
* **自签名证书可用：** 小企业可以使用自签名证书，通过 DANE 合法化

## 四、MTA-STS：TLS 强制的一种替代方案

### 4.1 MTA-STS 的定位

**MTA-STS（SMTP MTA Strict Transport Security，RFC 8461）** 提供了一种不依赖 DNSSEC 的 TLS 强制机制。它通过两种方式告知发件方必须使用 TLS：

* **DNS TXT 记录：** 在 \_mta-sts.ztpop.net TXT 记录中声明策略版本
* **HTTPS 策略文件：** 在 https://mta-sts.ztpop.net/.well-known/mta-sts.txt 发布详细策略

### 4.2 MTA-STS 配置示例

**DNS TXT 记录：**

```
_mta-sts.ztpop.net. IN TXT "v=STSv1; id=20250730000000;"
```

**HTTPS 策略文件（https://mta-sts.ztpop.net/.well-known/mta-sts.txt）：**

```
version: STSv1
mode: enforce
mx: mail.ztpop.net
mx: backup-mail.ztpop.net
max_age: 86400
```

### 4.3 MTA-STS vs DANE

| 维度 | DANE | MTA-STS |
| --- | --- | --- |
| 依赖 | 需要 DNSSEC | 不需要 DNSSEC，依赖 Web PKI（CA） |
| 公钥绑定 | 直接在 TLSA 记录中绑定证书哈希 | 不绑定证书，只要求 TLS 加密 |
| MITM 保护 | 强（证书级绑定） | 弱（仅强制 TLS，不验证证书真实性） |
| 部署难度 | 高 | 中等 |
| TLS-RPT | 支持 | 支持（同一报告格式） |

## 五、联动关系：DNSSEC 是 DANE 的基础

DNSSEC 和 DANE 的关系是**依赖与被依赖**：

* DANE 通过 TLSA 记录来"宣告"合法的 TLS 证书
* 但是 **TLSA 记录本身也是一个 DNS 记录**，如果不通过 DNSSEC 保护，TLSA 记录同样可以被攻击者篡改
* 没有 DNSSEC 的 DANE 只是将信任从 CA 转移到了 DNS 提供商——而 DNS 提供商可能成为新的攻击点
* DNSSEC 验证了 TLSA 记录的**来源真实性**和**数据完整性**，使 DANE 的证书声明具有密码学可验证性

因此，一个完整的 DNS 安全栈应该是：

**DNSSEC ⊃ DANE → MTA-STS（备选）**

即 DNSSEC 是整个安全栈的根基，DANE 在其上构建证书绑定，MTA-STS 作为不需要 DNSSEC 时的备选方案。

## 六、中国网络环境下 DNSSEC 部署现状

### 6.1 根区 DNSSEC

根区 DNSSEC 自 2010 年签署以来已经稳定运行。全球 13 组根服务器全部支持 DNSSEC 签名。

### 6.2 中国 TLD 支持情况

* **.cn 顶级域：** CNNIC 自 2017 年起支持 DNSSEC 签名。可以在 .cn 域上配置 DS 记录启用 DNSSEC
* **.com / .net 等通用顶级域：** 完全支持 DNSSEC
* **其他中国 TLD：** 部分支持，需向各注册管理机构确认

### 6.3 国内 DNS 解析器的支持情况

中国网络环境下 DNSSEC 验证的实际情况较复杂：

| DNS 服务商 | DNSSEC 验证 | 备注 |
| --- | --- | --- |
| 公共 DNS（114.114.114.114） | 有限支持 | 已验证 DoT/DoH，但 DNSSEC 验证可能受防火墙限制 |
| 公共 DNS（AliDNS 223.5.5.5） | 部分支持 | 已支持 DNSSEC 签名链验证 |
| 运营商 DNS | 多数不支持 | 国内三大运营商默认 DNS 基本不验证 DNSSEC |
| Cloudflare 1.1.1.1 | 完全支持 | 国内访问不稳定 |
| Google 8.8.8.8 | 完全支持 | 国内访问受限 |

### 6.4 中国用户的实际替代方案

由于国内 DNSSEC 验证覆盖不完整，对于面向中国用户的邮件系统，建议采取**混合策略**：

1. **积极部署 DNSSEC + DANE：** 即使国内解析器不验证，国际邮件服务商会验证，有助于出站信誉
2. **同时部署 MTA-STS：** 作为不依赖 DNSSEC 的 TLS 强制方案，覆盖国内 DNS 场景
3. **使用可信 DNS 服务：** 自建邮件系统时，配置使用支持 DNSSEC 验证的递归 DNS（如 AliDNS、114DNS 的 DoT/DoH 版本）
4. **TLS-RPT 报告：** 收集 TLS 连接失败的统计报告，及时发现问题
5. **传统 STARTTLS 兜底：** 确保即使 DANE/MTA-STS 不可用，邮件系统仍会尝试 STARTTLS

## 七、部署检查清单

**☑ DNSSEC 部署清单**

* 向域名注册商获取 DS 记录信息
* 在 DNS 服务商处生成并配置 DNSSEC 签名密钥
* 将 DS 记录提交给注册商（由注册商上传到父域）
* 验证：使用 dig +dnssec ztpop.net RRSIG 确认签名存在

**☑ DANE 部署清单**

* 确认为邮件服务器配置了有效的 TLS 证书
* 计算证书的 SHA-256 哈希值
* 在 DNS 中添加 TLSA 记录（\_25.\_tcp.mail.ztpop.net）
* 验证：使用 dig \_25.\_tcp.mail.ztpop.net TLSA
* 使用 swaks 或 telnet 测试 DANE SMTP 连接

**☑ MTA-STS 部署清单**

* 创建 MTA-STS DNS TXT 记录（\_mta-sts.ztpop.net）
* 配置 HTTPS 站点 mta-sts.ztpop.net 并提供策略文件
* 在策略文件中列出所有 MX 主机名
* 配置 TLS-RPT 报告地址（smtp.mailto.ztpop.net / rua@ztpop.net）
* 验证：使用在线 MTA-STS 检查工具

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/dns-security-email-deployment.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
