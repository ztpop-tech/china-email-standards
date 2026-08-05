---
title: "M3AAWG 停放域名保护最佳实践——防止域名被滥用为邮件发送源"
source: "https://ztpop.net/kb/m3aawg-parked-domains-bcp.html"
license: CC-BY 4.0
---

# M3AAWG 停放域名保护最佳实践——防止域名被滥用为邮件发送源

## 1. 停放域名的定义与安全风险

### 1.1 什么是停放域名

停放域名是指已被注册但未被实际用于网站托管或邮件通信的域名。典型的停放域名使用场景包括：

* **防御性注册**：企业注册自身品牌的多种变体（如correct-brand.com、correct-brand.cn），防止他人抢注
* **未来项目储备**：为尚未启动的产品线预留域名
* **拼写相似域名**：注册常见拼写错误版本，重定向至主站
* **域名投资**：持有待售

共同特征：域名注册有效，但无邮件服务器（MX）、无发送源（SPF/DKIM/DMARC），持有人无意收发邮件。

### 1.2 未保护停放域名的安全风险

未声明任何DNS记录的停放域名面临三大风险：

1. **第三方伪造发送**：攻击者注册与你停放域名相似的域名（如将example.com注册为examp1e.com），自建邮件服务器使用该域名发送垃圾邮件
2. **DMARC 验证干扰**：在部署了严格DMARC策略（p=reject）的邮件环境中，拼写相似域名的认证失败可能被视为源自你主域的攻击，触发不必要的告警
3. **SPF 宽松匹配误判**：RFC 7208 定义的 SPF 验证机制中，如果停放域名未发布任何SPF记录，接收MTA可能使用宽松解释（neutral/softfail），无法明确拒绝伪造邮件 [1]

## 2. 保护机制总览

M3AAWG BCP 建议通过以下五类DNS记录的协同配合，向接收MTA明确声明停放域名不参与任何邮件通信：

| 记录类型 | 功能 | 发布策略 |
| --- | --- | --- |
| SPF | 声明不授权任何IP发送邮件 | `v=spf1 -all` |
| DKIM | 不发布任何DKIM公钥 | 不创建任何 `_domainkey` 记录 |
| DMARC | 声明严格的邮件认证策略并接收报告 | `p=reject; rua=mailto:...;` |
| MX (Null MX) | 声明不收邮件 | `MX 0 .` |
| SOA | 传递联系信息 | 在SOA的RNAME字段设置 hostmaster |

## 3. DNS 记录详细配置

### 3.1 SPF：发布 `v=spf1 -all`

根据RFC 7208，SPF记录声明哪些IP地址被授权使用该域名发送邮件。对于停放域名，应发布最严格的形式：

```
example.com.  TXT  "v=spf1 -all"
```

`-all` 表示"所有未明确授权的发送方都应被拒绝"（hard fail）。由于停放域名没有任何授权IP，每一封冒用该域名发送的邮件都会被接收MTA判定为SPF失败。比较其他可用选项：

* `~all`（softfail）：仅标记为可疑但接受——不够严格
* `?all`（neutral）：不表达任何立场——完全无效
* 无SPF记录：接收方自行解释——存在歧义风险

有些人可能担心发布SPF记录会增加DNS查询。实际上，`-all` 匹配机制直接终止查询流程，不会产生额外的DNS开销 [1] §5.2。

### 3.2 DKIM：不发布任何记录

M3AAWG BCP 明确建议停放域名**不发布任何** `_domainkey` 子域下的TXT记录。原因：

* DKIM签名验证依赖于与签名头中 selector 匹配的公钥记录
* 若停放域名没有发布任何 `selector._domainkey` TXT记录，任何声称来自该域名的DKIM签名都会因找不到公钥而验证失败
* DKIM的 `d=` 标签必须与签名域名一致，不存在公钥即无法通过验证

```
; 不添加任何类似下面的记录：
; default._domainkey.example.com.  TXT  "v=DKIM1; p=..."
```

### 3.3 DMARC：发布 `p=reject`

DMARC 是声明停放域名不参与邮件通信的最重要的策略记录。M3AAWG BCP 推荐配置：

```
_dmarc.example.com.  TXT  "v=DMARC1; p=reject; sp=reject; rua=mailto:dmarc-rua@example.com; rf=afrf; pct=100"
```

关键参数：

* `p=reject`：声明该域名的所有邮件认证失败应被拒收——即使冒用者通过了SPF或DKIM验证
* `sp=reject`：子域名同样适用reject策略，防止子域名被滥用
* `rua=mailto:...`：接收聚合报告，用于监控是否有第三方尝试使用该停放域名发送邮件[1](/kb/dmarc-aggregate-reporting.html)
* `pct=100`：对所有流量执行策略

国内域名持有者应注意：rua邮箱应设置为能够接收大量自动化报告的企业邮箱地址，且应配置独立的邮件过滤规则防止聚合报告被误判为垃圾邮件。对于拥有大量停放域名的组织，建议使用专用报告聚合平台 [2]。此外，发信人应定期检查 DMARC 聚合报告中的发送源 IP——这是发现第三方滥用停放域名的最直接手段。

### 3.4 Null MX：通过 `MX 0 .` 声明不收邮件

RFC 7505 定义了 Null MX 机制，通过将MX记录指向一个裸点（.）来声明域名不接受任何邮件：

```
example.com.  MX  0  .
```

这一配置告诉所有发送MTA：该域名不提供任何邮件接收服务，任何尝试投递都应被回退。Null MX 的优势：

* 明确消除了与停用MX记录的歧义（未设置MX vs 故意不接受邮件）
* 发件MTA可立即判定无法投递，减少重试和退信
* 降低了反向散射（backscatter）攻击的风险——如果停放域名没有MX但发件人仍尝试发送，退信可能发回伪造的MAIL FROM地址 [3]

### 3.5 SOA 联系信息

虽然SOA记录不是为了邮件安全而设计的，但M3AAWG BCP建议在SOA的RNAME字段（通常格式为 hostmaster.example.com.）中设置有效联系方式，以便邮件系统管理员在发现滥用时联系域名持有者：

```
example.com.  SOA  ns1.example.com. hostmaster.example.com. (2026072501 3600 900 604800 86400)
```

## 4. 完整配置示例

### 4.1 场景A：纯停放域名（无A/AAAA记录）

最典型的停放域名——仅用于防御性注册，没有任何基础架构：

```
; DNS 区域文件：example.com
$TTL 3600

@  IN  SOA  ns1.example.com. hostmaster.example.com. (2026072501 3600 900 604800 86400)
@  IN  NS   ns1.example.com.
@  IN  NS   ns2.example.com.

; 不发送邮件 → SPF -all
@  IN  TXT  "v=spf1 -all"

; 不接收邮件 → Null MX
@  IN  MX  0  .

; DMARC 策略 → p=reject
_dmarc  IN  TXT  "v=DMARC1; p=reject; sp=reject; rua=mailto:dmarc-rua@example.com; pct=100"
```

### 4.2 场景B：有A记录的停放域名

停放域名配置了A记录（用于展示简单着陆页或停车页），但依然不用于邮件：

```
; DNS 区域文件：example.com
$TTL 3600

@  IN  SOA  ns1.example.com. hostmaster.example.com. (2026072501 3600 900 604800 86400)
@  IN  NS   ns1.example.com.
@  IN  NS   ns2.example.com.

; 用于HTTP服务（停车页）
@  IN  A    203.0.113.10
@  IN  AAAA 2001:db8::10

; 但绝不用于邮件
@  IN  TXT  "v=spf1 -all"
@  IN  MX   0  .
_dmarc  IN  TXT  "v=DMARC1; p=reject; sp=reject; rua=mailto:dmarc-rua@example.com; pct=100"
```

### 4.3 场景C：多域名通配保护

对于拥有数十到数百个停放域名（如品牌变体和国际化域名）的企业，可考虑在DNS模板中统一配置：

```
; 模板：brand-protection-domains.template
; 适用于所有防御性注册域名
$DOMAIN = DOMAIN_PLACEHOLDER
$DOMAIN.  IN  SOA  ns1.parentcompany.com. hostmaster.parentcompany.com. (NOW 3600 900 604800 86400)
$DOMAIN.  IN  NS   ns1.parentcompany.com.
$DOMAIN.  IN  NS   ns2.parentcompany.com.
$DOMAIN.  IN  TXT  "v=spf1 -all"
$DOMAIN.  IN  MX   0  .
_dmarc.$DOMAIN.  IN  TXT  "v=DMARC1; p=reject; sp=reject; rua=mailto:dmarc-rua@parentcompany.com; pct=100"
```

使用DNS API自动化此流程，可确保新增的停放域名不会因遗漏配置而被利用。

## 5. 进阶保护：DNSBL 登录

M3AAWG BCP 还建议在确认域名永远不发送邮件的前提下，考虑将停放域名主动提交到域名黑名单（DNSBL）。尽管这听起来反直觉，但目的是：

* 如果域名被列入RHSBL（Right-Hand Side Block List），接收MTA会立即拒绝声称来自该域名的邮件
* 这为停放域名增加了一道独立于SPF/DKIM/DMARC的防线
* 提交前必须书面确认**任何时候都不会**使用该域名发送合法邮件

常用的域名黑名单：

* URIBL — 关注邮件正文中的域名
* Spamhaus DBL — 域名级别的垃圾邮件数据库
* SURBL — 垃圾邮件URI实时黑名单

注意：若未来计划启用停放域名用于邮件发送，必须先申请从这些黑名单中移除，处理周期可能长达数周。

## 6. 验证配置是否生效

配置完成后应执行以下验证：

```
# 验证 SPF
dig txt example.com +short
# 预期输出： "v=spf1 -all"

# 验证 Null MX
dig mx example.com +short
# 预期输出： "0 ."

# 验证 DMARC
dig txt _dmarc.example.com +short
# 预期输出： "v=DMARC1; p=reject; ..."

# 验证 DKIM 缺失
dig txt default._domainkey.example.com +short
# 预期输出： （无输出，表示记录不存在）

# 使用第三方工具
# https://www.mail-tester.com 检查域名
# https://dmarcly.com/tools/dmarc-checker DMARC验证
```

## 7. 结论

停放域名作为品牌保护和战略储备的重要资产，不应被邮件安全策略忽视。M3AAWG BCP 提供了清晰、可操作的四步方案：发布 `v=spf1 -all`、不发布DKIM记录、发布 `p=reject` 的DMARC记录、设置 Null MX。这些措施不仅保护域名免于被第三方滥用，也减少了接收MTA因域名状态不明确而产生的额外安全检查开销。对于[邮件服务器](/mail-server.html)运维团队来说，在品牌保护清单中加入停放域名的 DNS 安全配置，是一项低成本高回报的[邮件安全](/mailgate.html)基础工作。

## 参考文献

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/m3aawg-parked-domains-bcp.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
