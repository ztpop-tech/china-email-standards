---
title: "M3AAWG 发送域名最佳常见实践——子域 vs 表亲域：邮件发送域名的正确选择方法"
source: "https://ztpop.net/kb/m3aawg-sending-domains-bcp.html"
license: CC-BY 4.0
---

# M3AAWG 发送域名最佳常见实践——子域 vs 表亲域：邮件发送域名的正确选择方法

#### 📑 目录

1. [摘要](#s1)
2. [引言——为何发送域名选择如此重要？](#s2)
3. [子域 vs 表亲域：核心决策](#s3)
4. [分段策略——不同类型流量的隔离原则](#s4)
5. [域名选择与命名规范](#s5)
6. [声誉与 Ramp-up 策略](#s6)
7. [认证配置：SPF/DKIM/DMARC](#s7)
8. [DNS 设置方式（三种方法）](#s8)
9. [迁移指南——更换 ESP 时的域名策略切换](#s9)
10. [国内场景补充](#s10)
11. [参考文献与延伸阅读](#s11)

## 一、摘要

本文基于 M3AAWG（Messaging, Malware and Mobile Anti-Abuse Working Group）**发送域名最佳常见实践**（M3AAWG-130，2019 年 10 月发布），系统阐述邮件发送域名的选择策略与配置规范。核心推荐使用**主域名的子域**发送邮件，**禁止使用"表亲域"（cousin domain）**——即与主品牌名类似但独立的域名。

文章覆盖以下主题：

* **子域 vs 表亲域**——为什么选择子域而非购买独立域名
* **分段策略**——不同类型流量使用不同子域，隔离声誉
* **域名选择与命名**——子域名应反映用途、保持一致的组织域
* **声誉与 Ramp-up**——新域从"unknown"开始，需 6 周左右 warm-up
* **认证配置**——SPF、DKIM、DMARC 在发送域上的正确部署方式
* **DNS 设置方式**——直接设置、CNAME 委派、NS 委派三种方案
* **迁移指南**——更换 ESP 时的域名策略与声誉过渡
* **国内场景补充**——国内 ESP 生态、DNS 服务商 CNAME 支持、典型配置示例

## 二、引言——为何发送域名选择如此重要？

在电子邮件的投递链路中，**发送域名**（sending domain）是收件方评估邮件可信度的首要依据之一。随着 SPF、DKIM、DMARC 等认证协议的广泛采用，发件人在邮件中使用的域名直接影响邮件是否能够通过认证检查并进入收件箱。

M3AAWG-130 文档的发布背景是：大量组织在选择邮件发送域名时做出了次优决策——购买了与主品牌名称相近的独立域名（表亲域），而非使用主域名的子域。这种做法的后果包括：

* 对用户和安全工具来说看起来像**钓鱼攻击**
* 导致**投诉率上升**，邮件被拦截或送入垃圾箱
* 带来不必要的**安全风险**（域名劫持、仿冒）
* 增加域名管理的**运维复杂度**

本文的目的是为邮件运营者提供明确、可操作的最佳实践，帮助他们做出正确的发送域名决策。

**核心原则**：始终使用主域名的子域发送邮件。这不仅符合收件方和用户的预期，也是 SPF/DKIM/DMARC 认证链中最自然、最易于管理的选择。

## 三、子域 vs 表亲域：核心决策

### 3.1 什么是子域？

子域（subdomain）是主域名（组织域）下的子层次域。例如：

* `marketing.example.com` 是 `example.com` 的子域
* `transactional.example.com` 是 `example.com` 的子域

子域是组织域的一部分，DNS 管理通常归属于同一组织。在邮件认证上下文中，子域的 DMARC 策略可以通过组织域的 `sp=` 参数统一控制，也可以在每个子域上独立设置。

### 3.2 什么是表亲域？

表亲域（cousin domain）是与主品牌名称类似但**完全独立的域名**。例如：

表 1：子域 vs 表亲域对比

| 类型 | 示例 | DNS 管理 | DMARC 继承 | 用户感知 |
| --- | --- | --- | --- | --- |
| 子域 | `offers.example.com` | 组织域所有者 | 可通过 `sp=` 继承 | 可信（属于同一品牌） |
| 表亲域 | `example-offers.com` | 独立 DNS 所有者 | 不继承 | 可疑（类似仿冒域名） |
| 表亲域 | `example-deals.net` | 独立 DNS 所有者 | 不继承 | 高度可疑 |

### 3.3 表亲域的风险

M3AAWG 强烈不建议使用表亲域，主要基于以下原因：

1. **钓鱼感知**：用户和安全邮件网关（Secure Email Gateway, SEG）看到 `example-offers.com` 的第一反应是——这是一个试图伪装成 `example.com` 的钓鱼域名。即使组织自己没有恶意意图，这种域名结构在视觉上与典型的钓鱼攻击域名无异。
2. **投诉率上升**：如果用户不记得自己订阅过"example-offers"，他们会点击"举报垃圾邮件"。高投诉率直接导致发件域名声誉骤降。
3. **声誉无法转移**：表亲域的声誉完全独立于主域。即使主域积累了良好的发送声誉，新注册的表亲域从零开始——实际上是从"unknown"开始，大多数收件方将其等同于"bad"。
4. **管理成本**：需要单独管理 SPF、DKIM、DMARC 记录，维护独立的 abuse@ 和 postmaster@ 邮箱，配置独立的 Web 服务器——每个表亲域都意味着全套的运维开销。

**⚠ 警告**：使用表亲域发送邮件是 M3AAWG 明确反对的做法。如果已在使用表亲域，应制定迁移计划过渡到子域方案。

### 3.4 为什么子域是正确选择？

* **品牌一致性**：用户在订阅邮件时看到的是 `newsletter.example.com`，与他们在浏览器中访问的 `example.com` 一致，不会产生信任疑虑
* **认证统一性**：组织域的 DMARC 策略可通过 `sp=` 覆盖所有子域，也可为特定子域设置独立策略
* **DNS 管理集中**：使用同一域名注册商和 DNS 服务商，减少管理面
* **声誉传递**：子域共享组织域的部分声誉信号
* **SPF 简化**：可使用通配 SPF 记录 `*.example.com` 统一授权

## 四、分段策略——不同类型流量的隔离原则

### 4.1 为什么要分段？

不同类型的邮件流量具有不同的用户期望和投诉模式：

* **交易类邮件**（订单确认、密码重置）——用户预期收到，投诉率极低
* **营销类邮件**（促销通知、Newsletter）——用户可能不再感兴趣，投诉率较高
* **通知类邮件**（账户提醒、安全通知）——用户预期收到，但投诉敏感度中等

如果所有类型共享同一个发送域名，营销邮件的投诉行为会污染整个域名的声誉，最终导致交易类邮件也被投递问题影响。

### 4.2 推荐的分段方案

M3AAWG 建议为不同类型的流量分别使用独立的子域：

表 2：邮件流量分段与子域命名建议

| 邮件类型 | 推荐子域 | 声誉特征 | 投诉风险 |
| --- | --- | --- | --- |
| 交易类（Transactional） | `info.example.com` / `transactional.example.com` | 高——用户高度期待 | 极低 |
| 营销类（Marketing） | `offers.example.com` / `marketing.example.com` | 中等——依赖用户参与度 | 较高 |
| 通知类（Notification） | `notify.example.com` / `alerts.example.com` | 中高——安全/账户相关 | 低 |
| 系统类（System/Bounce） | `bounce.example.com` / `system.example.com` | 内部用途，不与用户直接交互 | 不适用 |

### 4.3 分段的声誉隔离优势

分段发送的最重要优势是**声誉隔离**：

* 当营销邮件的投诉率突然上升时，交易类邮件的投递不受影响
* 可以对不同段位分别设置 Ramp-up 计划
* 某个子域被列入黑名单时，其他子域不受牵连
* 便于针对性地监控和调试——Google Postmaster Tools 等平台按域名展示统计数据

**注意**：每个子域必须有**足够且一致的发送流量**。流量过低或忽高忽低的域名无法建立稳定的声誉信号。如果某个邮件类型每月的发送量极少（不足千封），可考虑合并到相关类型的子域中。

## 五、域名选择与命名规范

### 5.1 子域名命名原则

子域的名称应反映其用途，避免混淆：

* **清晰明了**：`marketing.example.com` 比 `news.example.com` 更清晰——前者明确告知是营销邮件
* **避免歧义**：不要使用 `mail.example.com` 作为所有类型流量的单一子域
* **一致的组织域**：建议在整个邮件中保持一致的组织域

### 5.2 组织域一致性要求

M3AAWG 建议发送方在整个邮件生命周期中保持组织域的一致性，即：

* **Return-Path 域**（SPF 评估的 SMTP Mail From 域名）
* **From 域**（RFC 5322.From 中的域名，DMARC 评估目标）
* **DKIM d= 域**（DKIM 签名域名）

应使用**同一个组织域**或其子域。推荐做法：

* `Return-Path: bounce@marketing.example.com`
* `From: "品牌名" <newsletter@marketing.example.com>`
* `DKIM-Signature: d=marketing.example.com; s=selector1; ...`

这种一致性让收件方的 DMARC 验证自然通过，且不会在每个头部中使用不同的域名造成收件方的困惑。

## 六、声誉与 Ramp-up 策略

### 6.1 声誉模型基础

邮件声誉（reputation）是收件方对发件域名和 IP 的信任评分。声誉基于以下因素的组合：

* **发送域名**——使用的子域名
* **发送 IP**——发件源的 IP 地址
* **邮件内容**——内容质量、投诉率、垃圾邮件特征

关键认知：**新域从"unknown"开始，接近"bad"**。收件方对未知域名持怀疑态度，这是正常的安全机制。

### 6.2 Ramp-up 策略

当启用一个新的发送域名（或切换到一个新的 ESP）时，不能立即以全量发送——需要逐步增加发送量以建立声誉：

1. **保持一致性**：在 Ramp-up 期间，保持域名使用的一致性，不要频繁切换
2. **检查 SMTP 日志**：监控退信率（bounce rate）、拒绝（reject）码、延迟（deferral）模式
3. **注册数据监控程序**：主动注册**Google Postmaster Tools**、**Microsoft SNDS**（Smart Network Data Services）等平台
4. **建议平均 6 周 warm-up**：

表 3：推荐 Ramp-up 时间线

| 周期 | 发送量相对目标 | 监控重点 |
| --- | --- | --- |
| 第 1 周 | 总目标的 5-10% | 退信率、SPF/DKIM 验证通过率 |
| 第 2 周 | 15-20% | 投诉率、垃圾邮件比率 |
| 第 3 周 | 25-35% | Gmail/Outlook/Yahoo 的送达率 |
| 第 4 周 | 40-60% | 反馈循环（FBL）数据 |
| 第 5 周 | 65-80% | 延迟率是否正常 |
| 第 6 周 | 100% | 全量发送，持续监控 |

### 6.3 域名/IP 切换注意事项

切换域名或 IP 时，声誉无法自动转移：

* 新域名需要一个完整的 Ramp-up 周期
* 新 IP 网段同样需要 warm-up
* 如果同时切换域名和 IP，建议先稳定域名声誉再更换 IP

```
# 在 Google Postmaster Tools 中监控发送域的声誉
# 1. 登录 https://postmaster.google.com
# 2. 添加子域（如 marketing.example.com）并完成 DNS 验证
# 3. 查看 "IP 声誉" 和 "域名声誉" 两项指标
# 4. 声誉等级由低到高：Bad → Low → Medium → High
#
# 新域出现在 GPT 中需要一定发送量（通常数百封）积累数据
```

```
# 检查退信率的简单脚本（基于 Postfix 日志）
cat /var/log/mail.log | grep "$(date +%Y-%m-%d)" | \
  awk '/status=sent/ {sent++} /status=bounced/ {bounced++} END \
  {printf "Sent: %d, Bounced: %d, Rate: %.2f%%\n", sent, bounced, (bounced/(sent+bounced))*100}'
```

## 七、认证配置：SPF/DKIM/DMARC

### 7.1 SPF 配置

SPF 在 **Return-Path 域**的 DNS zone 中设置。SPF 记录声明哪些 IP 地址被授权代表该域名发送邮件。

```
; 子域 marketing.example.com 的 SPF 记录
; DNS 记录类型：TXT
marketing.example.com.  IN  TXT  "v=spf1 include:_spf.esp-service.com ~all"

; 如果需要同时授权多个发件源
marketing.example.com.  IN  TXT  "v=spf1 ip4:203.0.113.0/24 include:_spf.esp-service.com ~all"

; 通配子域 SPF（覆盖所有 *.example.com 的子域）
*.example.com.  IN  TXT  "v=spf1 include:_spf.esp-service.com ~all"
```

配置要点：

* SPF 记录应设置在发送子域的 DNS zone 中，而非组织域
* 使用 `~all`（softfail）过渡，确认无误后切换为 `-all`（fail）
* 保持 SPF 查询次数在 10 次以内（RFC 7208 Section 10.1 限制）

### 7.2 DKIM 配置

DKIM 在**签名域**（DKIM `d=` 参数指定的域）的 DNS zone 中发布公钥。每个子域应使用**不同的选择器**：

```
; 营销子域的 DKIM 公钥（选择器: s1）
; DNS 记录类型：TXT
s1._domainkey.marketing.example.com.  IN  TXT  "v=DKIM1; h=sha256; k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC..."

; 交易子域的 DKIM 公钥（使用不同选择器: t1）
; 这样可以独立管理密钥轮转和签名策略
t1._domainkey.transactional.example.com.  IN  TXT  "v=DKIM1; h=sha256; k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC..."

; 查看 DKIM 公钥的完整内容（dig 命令）
; dig TXT s1._domainkey.marketing.example.com +short
```

配置要点：

* 每个子域使用独立的选择器，便于分别轮转
* DKIM `d=` 域应与 `header.From` 域的组织域一致（DMARC 对齐要求）
* 推荐使用 2048-bit RSA 密钥或 Ed25519（RFC 8463）
* 定期轮转 DKIM 密钥（见相关阅读：M3AAWG DKIM 密钥轮转最佳实践）

### 7.3 DMARC 配置

DMARC 策略发布在**visible From: 域**的 DNS zone 中。如果无法在组织域立即设置 DMARC，可以先在子域上设置：

```
; 组织域上的 DMARC 策略（覆盖所有子域）
_dmarc.example.com.  IN  TXT  "v=DMARC1; p=quarantine; sp=quarantine; rua=mailto:dmarc@example.com; ruf=mailto:dmarc-forensic@example.com; pct=100"

; 营销子域上的独立 DMARC 策略（覆盖组织域策略）
; 注意：子域 DMARC 记录位于 _dmarc.<子域> 下
_dmarc.marketing.example.com.  IN  TXT  "v=DMARC1; p=reject; rua=mailto:dmarc-marketing@example.com; pct=100"

; 交易子域——采用更严格的策略（因为投诉率低，可以放心设置 reject）
_dmarc.transactional.example.com.  IN  TXT  "v=DMARC1; p=reject; rua=mailto:dmarc-transactional@example.com; pct=100"

; 查询 DMARC 策略
; dig TXT _dmarc.marketing.example.com +short
```

表 4：各认证协议的 DNS 设置位置

| 协议 | 评估目标 | DNS zone 位置 |
| --- | --- | --- |
| SPF | Return-Path（Envelope From）域 | Return-Path 域名的 DNS TXT 记录 |
| DKIM | DKIM-Signature 的 `d=` 域 | `<selector>._domainkey.<d-domain>` 的 DNS TXT 记录 |
| DMARC | RFC 5322.From 域（visible From） | `_dmarc.<from-domain>` 的 DNS TXT 记录 |

### 7.4 其他基础设施要求

* **MX 记录**：发送域必须有指向正常邮件服务器的 MX 记录。即使只发不收，MX 记录也是基础设施要求。
* **abuse@ 和 postmaster@**：这些必须存在、可读（由人工或自动化系统处理）且不弹回。收件方需要能通过这些地址报告滥用问题。
* **Web presence**：visible From: 中的域名应解析到实时运行的网页。如果 From 域没有网站，收件方可能对邮件来源产生不信任。

```
# 验证基础设施要求
# MX 记录检查
dig MX marketing.example.com +short

# abuse@ 邮箱测试
echo "Test abuse report" | mail -s "DMARC report test" abuse@example.com

# postmaster@ 邮箱测试
echo "Test postmaster mail" | mail -s "Postmaster test" postmaster@example.com

# Web Presence 检查
curl -sI https://marketing.example.com/ | head -5
# 预期返回 HTTP 200
```

## 八、DNS 设置方式（三种方法）

在配置发送域名的 DNS 记录时，M3AAWG 根据运维场景提供了三种设置方式。选择哪种方式取决于组织与 ESP（电子邮件服务提供商）之间的关系。

### 8.1 方式一：直接设置（Direct DNS Entry）

**适用场景**：组织自行管理 DNS zone，不使用第三方 ESP 服务。这是没有第三方时唯一的选择。

**优势**：完全控制 DNS 记录，不依赖任何第三方。

**劣势**：任何变更都需要手动操作，当 ESP 需要更新记录值时（如 DKIM 密钥轮转），需要跨组织协调。

```
; 直接在 DNS zone file 中设置所有记录
; 文件示例：/etc/named/db.marketing.example.com

$TTL    3600
@       IN  SOA   ns1.example.com. admin.example.com. (
                   2026072601  ; Serial
                   3600        ; Refresh
                   900         ; Retry
                   604800      ; Expire
                   86400       ; Minimum TTL
                   )

; MX 记录
@       IN  MX    10  mail.example.com.

; SPF
@       IN  TXT   "v=spf1 ip4:203.0.113.0/24 include:_spf.esp-service.com ~all"

; DKIM
s1._domainkey   IN  TXT   "v=DKIM1; h=sha256; k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC..."

; DMARC
_dmarc  IN  TXT   "v=DMARC1; p=quarantine; rua=mailto:dmarc@example.com"

; abuse@ 和 postmaster@ 邮件转发
abuse       IN  MX    10  mail.example.com.
postmaster  IN  MX    10  mail.example.com.
```

### 8.2 方式二：CNAME 委派

**适用场景**：使用 ESP 服务且信任 ESP 管理记录值，但不希望将整个子域的 nameserver 控制权交出。

**优势**：允许 ESP 透明地更新记录值（如 DKIM 公钥轮转时无需客户手动操作），是 ESP 的首选方式。

**劣势**：只能委派单个记录类型（不能委派整个子域为 CNAME，否则会丢失 MX 等记录）。

```
; 方式二：CNAME 委派部分记录给 ESP
; 设置位置：组织域（example.com）的 DNS zone 中

; 将 marketing.example.com 的 TXT 查询委派给 ESP 管理的域名
marketing.example.com.  IN  CNAME  esp-managed-domain.esp-service.com.

; ⚠ 注意：CNAME 会覆盖 zone 中该名称的所有记录类型
; 如果需要 MX、NS 等与其他记录共存，不能直接使用 CNAME 到子域顶点
; 替代方案：为特定记录使用 CNAME

; DKIM 选择器记录的 CNAME 委派（推荐做法）
s1._domainkey.marketing.example.com.  IN  CNAME  s1.dkim.esp-service.com.

; 上述 CNAME 配置的含义：
; dig TXT s1._domainkey.marketing.example.com → 自动解析到
; dig TXT s1.dkim.esp-service.com → 返回 ESP 管理的 DKIM 公钥

; 验证 CNAME 委派是否生效
dig CNAME s1._domainkey.marketing.example.com +short
# 预期输出: s1.dkim.esp-service.com.
dig TXT s1.dkim.esp-service.com +short
# 预期输出: "v=DKIM1; h=sha256; k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC..."
```

### 8.3 方式三：Nameserver (NS) 委派

**适用场景**：完全信任 ESP 且需要 ESP 管理子域及其所有子域的全部 DNS 记录。

**优势**：将整个子域及所有子域委派给 ESP 的 nameserver，ESP 可以完全自主地管理所有 DNS 记录（包括未来的新增记录），无需客户参与任何 DNS 变更。

**劣势**：客户对该子域的 DNS 控制权完全移交给 ESP；如果 ESP 的服务中断，该子域的所有 DNS 解析将受到影响。

```
; 方式三：NS 委派整个子域给 ESP
; 设置位置：组织域（example.com）的 DNS zone 中

; 将 marketing.example.com 及其所有子域委派给 ESP 的 nameserver
marketing.example.com.  IN  NS  ns1.esp-service.com.
marketing.example.com.  IN  NS  ns2.esp-service.com.

; 必须同时设置 glue records（粘合记录）
ns1.esp-service.com.    IN  A   203.0.113.100
ns2.esp-service.com.    IN  A   203.0.113.101

; 委派生效后，以下所有记录都由 ESP 的 nameserver 管理：
; - marketing.example.com 的 MX、SPF、TXT 记录
; - s1._domainkey.marketing.example.com 的 DKIM 记录
; - _dmarc.marketing.example.com 的 DMARC 记录
; - 未来可能需要的 BIMI、MTA-STS、TLSRPT 等记录
; - 甚至 marketing.sub.example.com 等更深层级的子域

; 验证 NS 委派是否生效
dig NS marketing.example.com +short
# 预期输出: ns1.esp-service.com. / ns2.esp-service.com.

dig TXT marketing.example.com +short @ns1.esp-service.com.
# 从委派的 nameserver 直接查询 SPF 记录
```

### 8.4 三种方式对比

表 5：三种 DNS 设置方式对比

| 维度 | 直接设置 | CNAME | NS 委派 |
| --- | --- | --- | --- |
| 控制权 | 完全自主 | 客户保留 zone 控制权，记录值由 ESP 管理 | 完全移交 ESP |
| 变更便利性 | 需客户手动修改 | ESP 可透明更新 | ESP 完全自主 |
| DNS 查询开销 | 直接响应 | 多一次 CNAME 链查询 | 与直接设置相同 |
| ESP 故障影响 | 无影响 | CNAME 目标不可解析时影响记录查询 | 子域整个 zone 不可用 |
| 适用 ESP 关系 | 自运维 / 不支持委派 | 主流 ESP（SendGrid、Mailgun 等） | 深度绑定 ESP 管理 |
| 记录类型覆盖 | 所有记录类型 | 仅 CNAME 目标提供的类型 | 全部 |
| 子域委派深度 | 仅当前 zone | 仅委派单条记录 | 递推委派所有子层级 |

## 九、迁移指南——更换 ESP 时的域名策略切换

### 9.1 迁移的核心原则

**一致性**是维护声誉的关键。更换 ESP 时，应尽可能保持原有域名策略的连续性。

### 9.2 迁移路径

1. **DNS 切换**：更换 ESP 时，通过修改 DNS 设置完成迁移——将 CNAME 或 NS 记录指向新 ESP 的域名/nameserver
2. **MX 记录的约束**：MX 记录只能指向一个供应商（一个邮件系统），因此迁移期间需要规划好 MX 指向
3. **并行发送验证**：在新旧 ESP 上并行发送一段时间，确认新 ESP 的认证配置（SPF/DKIM/DMARC）完全正确
4. **完全切换**：当新 ESP 的发送节奏和量达到稳定后，将所有流量切换到新 ESP

### 9.3 迁移中的 Ramp-up 注意事项

即使使用同一个域名，迁移到新 ESP 仍需要在新 IP 上重新建立声誉：

```
# 推荐迁移流程

# 第一步：准备新 ESP 的 DNS 记录
# 将子域的 CNAME 或 NS 指向新 ESP

# 第二步：验证新 ESP 的认证配置
dig TXT marketing.example.com +short
# 确认返回新 ESP 的 SPF 记录

dig TXT s1._domainkey.marketing.example.com +short
# 确认返回新 ESP 的 DKIM 公钥

dig TXT _dmarc.marketing.example.com +short
# 确认 DMARC 策略不变

# 第三步：在新 ESP 上开始 Ramp-up
# 从低量开始，按照第 6 节的 Ramp-up 时间线执行

# 第四步：监控 GPT / SNDS / FBL 数据
# 确认新 ESP IP 的声誉逐步建立

# 第五步：完成迁移
# 逐步将流量比例从 旧ESP:100% → 50:50 → 新ESP:100%
```

迁移期间可能出现以下问题：

* **延迟（Deferral）增加**：收件方对新 IP 网段持谨慎态度，可能暂时延迟邮件
* **投诉率短期上升**：如果发送节奏变化明显，用户的投诉行为可能受影响
* **DNS 切换延迟**：TTL 缓存导致部分收件方仍然解析到旧 ESP 的配置

建议在迁移前降低 SPF/DKIM 记录的 TTL（如 300 秒），加速 DNS 切换生效。

## 十、国内场景补充

### 10.1 国内 ESP 生态特点

在中国邮件市场，发送域名的选择策略在 M3AAWG 通用原则之外，还需要考虑以下生态特点：

* **主流收件方**：QQ 邮箱（tencent.com）、163/126 邮箱（163.com）、阿里邮箱（aliyun.com/alibaba.com）、新浪邮箱（sina.com）等，均已部署 SPF/DKIM/DMARC 检查
* **国内 ESP**：SendCloud、MailData、Submail、网易企业邮等常作为国内发件方的 ESP 选择
* **特殊要求**：QQ 邮箱对发件域有独立的信誉系统，QQ 域名信誉（Domain Reputation）通过其管理后台可见

### 10.2 国内 DNS 服务商 CNAME 支持

国内 DNS 服务商（DNSPod、阿里云 DNS、华为云 DNS、火山引擎 DNS 等）均支持标准的 CNAME 记录。但在设置时需注意：

表 6：国内 DNS 服务商 CNAME 支持明细

| DNS 服务商 | CNAME 到外部域名 | 隐式 URL 转发 | 注意事项 |
| --- | --- | --- | --- |
| DNSPod（腾讯云） | ✅ 支持 | ✅（需备案） | 需完成域名备案；DNS 解析 TTL 最小可设为 60 秒 |
| 阿里云 DNS（云解析） | ✅ 支持 | ✅（需备案） | 建议开启 DNS 安全防护；免费版 TTL 最小 600 秒 |
| 华为云 DNS | ✅ 支持 | ❌ 不支持 | 企业版支持 `routing policy` 智能解析 |
| 火山引擎 DNS | ✅ 支持 | ❌ 不支持 | TTL 支持低至 1 秒（专业版） |

### 10.3 国内 ESP 典型配置示例

以下是一个适配国内邮件发送场景的典型配置示例：

```
; ========================================
; 国内 ESP 典型配置示例（以 SendCloud 为例）
; 组织域: example.com
; 营销子域: marketing.example.com
; 交易子域: transactional.example.com
; ========================================

; ---- SPF ----
; 方式一：直接设置（推荐，国内 ESP 通常提供具体 IP 段）
marketing.example.com.  IN  TXT  "v=spf1 include:spf.sendcloud.org -all"
transactional.example.com.  IN  TXT  "v=spf1 include:spf.sendcloud.org -all"

; 方式二：使用国内 ESP 的专用 SPF include
; SendCloud: include:spf.sendcloud.sc
; Submail:   include:spf.submail.me
; MailData:  include:spf.maildata.net

; ---- DKIM ----
; SendCloud 典型 DKIM 配置
s1._domainkey.marketing.example.com.  IN  TXT  "v=DKIM1; h=sha256; k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC..."
; SendCloud 建议选择器：s1 或 sc._domainkey

; ---- DMARC ----
_dmarc.example.com.  IN  TXT  "v=DMARC1; p=quarantine; sp=quarantine; rua=mailto:dmarc@example.com; ruf=mailto:dmarc-forensic@example.com"

; ---- MX 记录（必须有） ----
marketing.example.com.  IN  MX  10 mx.sendcloud.org.
```

### 10.4 国内邮箱收件方的特殊注意事项

* **QQ 邮箱**：QQ 邮箱对 SPF 的 `~all` 和 `-all` 均有严格要求。建议使用 `-all`（硬拒绝）以获取最高信任度。
* **163 邮箱**：163 邮箱的 DMARC 策略执行比较严格，建议在 `p=quarantine` 阶段充分验证后再升级到 `p=reject`。
* **阿里邮箱**：阿里邮箱支持 DMARC 对齐（strict 和 relaxed 模式），但对 DKIM 的有效性验证较为严格，需确保 DKIM 公钥与签名完全匹配。

### 10.5 国内备案与域名合规要求

在中国大陆运营邮件系统时，还需注意以下合规要求：

* 发送域名的网站（Web presence）需要完成 ICP 备案
* abuse@ 和 postmaster@ 邮箱需要有人工或自动化处理流程
* 大规模发送前建议完成发信资质备案（部分地区有要求）
* 涉及营销邮件需遵循《网络安全法》和《通信短信息和语音呼叫服务管理规定》关于用户同意和退订的要求

## 十一、参考文献与延伸阅读

### 📚 相关阅读

* [M3AAWG 电子邮件认证推荐最佳实践——SPF/DKIM/DMARC/ARC 配置检查清单](https://ztpop.net/kb/m3aawg-email-auth-best-practices.html)
* [M3AAWG DKIM 密钥轮转最佳常见实践——密钥生命周期管理指南](https://ztpop.net/kb/m3aawg-dkim-key-rotation-bcp.html)
* [DMARC p=reject 后邮件排错流程：从拒收到可送达](https://ztpop.net/kb/dmarc-reject-troubleshooting.html)
* [邮件认证生态全景：SPF/DKIM/DMARC/ARC/BIMI 协议链全解析](https://ztpop.net/kb/email-authentication-ecosystem.html)
* [M3AAWG 公共后缀列表（PSL）使用最佳实践](https://ztpop.net/kb/m3aawg-psl-guide.html)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/m3aawg-sending-domains-bcp.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
