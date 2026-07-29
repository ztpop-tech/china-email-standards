---
title: "Gmail递送工程：Google发件人要求的技术实现"
source: "https://ztpop.net/kb/gmail-deliverability-engineering.html"
license: CC-BY 4.0
---

# Gmail递送工程：Google发件人要求的技术实现

## 1. Google 发件人合规框架

自 2024 年 2 月 1 日起，Google 对日均向 Gmail 个人用户地址发送超过 5,000 封邮件的发件人执行四项强制技术要求。未达标者的递送将被递增式抑制：初期表现为批量邮件路由至垃圾邮件文件夹，中期触发 421 4.7.0 临时连接拒绝，后期导致发件 IP 进入 Google 内部信誉黑名单。Google Email Sender Guidelines 将这四项要求定义为不可拆解的合规基线：

1. 发件域具有有效的 SPF 或 DKIM DNS 认证记录。
2. 发件域发布 p=none 以上的 DMARC 策略记录——最低要求为 p=none，但强烈建议逐步提升至 p=quarantine 或 p=reject。
3. From 头中的域（RFC 5322 From）必须与 SPF 验证域（Return-Path 信封发件人）或 DKIM 签名域（d= 标签值）对齐——通过 DMARC relaxed 或 strict 对齐检查。
4. 邮件结构符合 RFC 5322 消息格式规范，包括有效的 Message-ID、Date 头及正确的 MIME 边界。

基于 Gmail 的递送量级，发件人被分为两类：日发送量不足 5,000 封的 "低量发件人" 不受强制要求约束（但仍获益于完整配置的递送优势）；日发送量超越此阈值的 "批量发件人" 必须完全满足所有四项要求。Google 额外要求批量发件人支持 List-Unsubscribe 一键退订（RFC 8058）、维持垃圾邮件投诉率低于 0.3%（建议 < 0.1%）、出站 TLS 加密率不低于 95%，且配置有效的正向和反向 DNS 记录。

## 2. DNS 认证记录三层配置

### 2.1 SPF 记录（RFC 7208）

SPF 通过 TXT 类型 DNS 记录声明有权以该域名义发送邮件的 IP 地址和主机名集合。规范记录必须始于 `v=spf1` 并以机制（`ip4`、`ip6`、`mx`、`a`、`include`、`ptr`）或修饰符（`redirect`、`exp`）结尾。DNS 查询计数受 SPF 规范的 10 次限制——每项 include、mx、a、ptr 机制计为一次查询。

```
# 标准 SPF 记录包含第三方 ESP
example.com.  IN  TXT  "v=spf1 mx ip4:203.0.113.10 ip6:2001:db8::25
  include:_spf.google.com include:spf.thirdparty-esp.com ~all"

# 验证 SPF 记录
$ dig +short TXT example.com | grep 'v=spf1'
$ python3 -c "
import spf
r = spf.check2('203.0.113.10', 'sender@example.com', 'example.com')
print(r[0], r[1])
"
```

经常发生的配置错误：(a) DNS 查询次数超限——当 include 链展开后总查询数超过 10 次时，SPF 评估返回 permerror（永久错误），大多数 MTA 将其视为 fail；(b) `~all`（softfail）被许多接收方（含 Google）处理为等效于 neutral 而非 fail——DMARC 对齐时 neutral 不触发失败；(c) 同一域存在多条 SPF TXT 记录——根据 RFC 7208 §4.5，多条记录导致 permerror；(d) 使用已废弃的 `ptr` 机制——该机制在 RFC 7208 中被明确标为 "不推荐使用" 且消耗大量 DNS 查询。

### 2.2 DKIM 签名（RFC 6376）

DKIM 使用非对称密钥对选定邮件头（From、To、Subject、Date 等）和邮件体进行哈希签名。签名嵌入 DKIM-Signature 头中，包含选择器（`s=`）、签名域（`d=`）、头覆盖列表（`h=`）、规范算法（`c=`）和过期时间（`x=`）。验证方使用 `<selector>._domainkey.<domain>` 的 DNS TXT 查询获取公钥。

2.2 DKIM 签名（RFC 6376）

| 参数 | 建议值 | 原因 |
| 密钥长度 (RSA) | 2048 bits | Google 最低要求 1024 bits；NIST SP 800-57 推荐 ≥ 2048 bits |
| 签名头部覆盖 (h=) | From:To:Subject:Date:Message-ID | 至少覆盖 From；增加 Date 可有效防止重放攻击 |
| 规范化算法 (c=) | relaxed/relaxed | 允许中间 MTA 对空白字符和大小写的微小改写，减少签名断裂 |
| 签名过期 (x=) | 当前时间 + 7 天 | 限制已签名邮件的有效重放窗口 |

```
# DKIM 公钥记录示例
google._domainkey.example.com.  IN  TXT  "v=DKIM1; k=rsa;
  p=MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA..."

# 验证 DKIM 记录语法
$ opendkim-testkey -d example.com -s google -vvv
```

密钥轮换策略：每年生成新密钥对并在 DNS 中同时发布当前密钥和新密钥（使用不同选择器）。旧选择器在过渡期（30 天）后移除。轮换期间两个选择器并存可确保途中的邮件不被误标记为 DKIM 失败。

### 2.3 DMARC 策略发布（RFC 7489）

DMARC 声明域对未通过 SPF 和 DKIM 认证加对齐检查的邮件应采取的处置措施，并通过 `rua`（聚合报告）和 `ruf`（取证报告）标签指定报告接收地址。

```
# 三步渐进 DMARC 部署
# Step 1: 监控模式 (p=none) — 收集 1-2 周基线数据
_dmarc.example.com.  IN  TXT  "v=DMARC1; p=none;
  rua=mailto:dmarc@example.com; ruf=mailto:dmarc-forensic@example.com;
  fo=1"

# Step 2: 隔离模式 (p=quarantine) + 逐步覆盖
_dmarc.example.com.  IN  TXT  "v=DMARC1; p=quarantine; pct=25;
  rua=mailto:dmarc@example.com"
# → pct=25 → 50 → 100 (每步监控 1 周)

# Step 3: 拒绝模式 (p=reject) — 完整合规
_dmarc.example.com.  IN  TXT  "v=DMARC1; p=reject; pct=100;
  rua=mailto:dmarc@example.com; aspf=r; adkim=r"
```

DMARC 对齐采用两条独立路径：(a) SPF 对齐——Return-Path 域的组织域（组织的 .com/.org 等公共后缀上一级）与 RFC 5322 From 域的组织域匹配；(b) DKIM 对齐——DKIM-Signature 头中 `d=` 标签的组织域与 From 域的组织域匹配。二者满足其一即通过 DMARC。`aspf=r` / `adkim=r` 指定 relaxed 对齐（组织域匹配即可），`aspf=s` / `adkim=s` 要求 strict 对齐（完全相同的子域）。Google 和大多数接收方接受 relaxed 对齐。

使用第三方 ESP（如 Mailchimp、SendGrid）时，Return-Path 默认属于 ESP 的 bounce 域（如 `bounce.sendgrid.net`），与发件人的 From 域不匹配导致 SPF 对齐失败。必须在 ESP 侧配置自定义 Return-Path 域（custom bounce domain），使 Return-Path 的组织域与 From 域一致。

## 3. 邮件格式合规

### 3.1 RFC 5322 消息结构

每封邮件必须包含单一的 From 头（不得多值）、Date 头和全局唯一的 Message-ID 头。MIME 多部分消息必须包含 `MIME-Version: 1.0` 头，multipart 部分的 boundary 参数在消息内部唯一。缺少 text/plain 部分的 multipart/alternative 邮件将在纯文本客户端上完全不可读，Google 将其视为格式缺陷而降低投递优先级。

```
From: Sender Name <sender@example.com>
To: recipient@gmail.com
Date: Tue, 15 Jul 2026 14:30:00 +0800
Message-ID: <20260715143000.a1b2c3d4@mx1.example.com>
Subject: =?UTF-8?B?6YKu5Lu25oqV6YCS5bel56iL?=
MIME-Version: 1.0
Content-Type: multipart/alternative; boundary="=-alt-001-20260715"
List-Unsubscribe: <mailto:unsub@example.com?subject=unsub-abc123>,
    <https://example.com/unsub?token=abc123>
List-Unsubscribe-Post: List-Unsubscribe=One-Click
```

Subject 头涉及非 ASCII 字符时使用 RFC 2047 编码字（Encoded-Word）：`=?charset?encoding?encoded_text?=`。From 头的显示名（display-name）若有非 ASCII 字符，同样需要编码，但地址部分（`<email@domain>`）始终为纯 ASCII。

### 3.2 List-Unsubscribe 与 RFC 8058 一键退订

批量邮件必须在头中包含 `List-Unsubscribe` 字段，同时提供 mailto URI（退订邮箱）和 HTTPS URI（退订网页）。RFC 8058 扩展了此机制，添加 `List-Unsubscribe-Post: List-Unsubscribe=One-Click` 辅助头，使 Gmail 等客户端可通过单次 HTTPS POST 请求完成退订而无需用户在网页上再操作。

```
List-Unsubscribe: <https://example.com/unsub/{{unique-token}}>
List-Unsubscribe-Post: List-Unsubscribe=One-Click
```

HTTPS 退订端点必须满足：(a) 接收 POST 请求后立即执行退订——不得要求登录、输入密码或任何形式的二次确认；(b) 退订令牌（token）须为加密强度的不可猜测随机值，有效期不少于 90 天；(c) 退订后立即从该收件人的后续发送列表中移除，延迟不得超过 48 小时。Gmail 对不满足这些条件的退订端点会降低邮件的收件箱投递概率。

## 4. TLS 传输加密强制

Google 要求发件方出站 SMTP TLS 加密率 ≥ 95%——这一指标在 Postmaster Tools 仪表盘中以 "TLS inbound encryption rate" 形式反映。Postfix 出站加密配置的关键参数：

```
# Postfix main.cf — 出站 TLS 合规配置
smtp_tls_security_level = may
smtp_tls_protocols = !SSLv2, !SSLv3, !TLSv1, !TLSv1.1
smtp_tls_mandatory_protocols = !SSLv2, !SSLv3, !TLSv1, !TLSv1.1
smtp_tls_ciphers = high
smtp_tls_mandatory_ciphers = high
smtp_tls_CAfile = /etc/ssl/certs/ca-certificates.crt
smtp_tls_session_cache_database = btree:${data_directory}/smtp_scache
```

`smtp_tls_security_level = may`（机会性 TLS，即 STARTTLS 方式）在不支持 TLS 的对端上回退明文传输。`encrypt` 级别强制要求 TLS 否则放弃投递——适合对特定域实施策略，但不适合通用互联网递送。TLS 1.0 和 1.1 已于 2021 年 3 月通过 RFC 8996 正式废弃，MTA 必须通过协议排除指令予以禁用。

## 5. 投诉率控制与反馈环

Google 的 Feedback Loop（FBL）将 Gmail 用户标记为垃圾邮件的投诉数据以 ARF（Abuse Reporting Format，RFC 5965）格式反馈给已注册的发件人。投诉率是所有递送信号中最敏感的一项。

5. 投诉率控制与反馈环

| 投诉率范围 | Gmail 响应 | 恢复周期 |
| < 0.1% | 收件箱优先，递送正常 | — |
| 0.1% – 0.3% | 垃圾箱路由比例上升 | 降至 < 0.1% 后 3–7 天恢复 |
| > 0.3% | 全量垃圾箱路由，域/IP 信誉急剧下降 | 降至 < 0.1% 后 2–4 周 |
| 持续 > 0.5% | 连接级拒绝 (421 4.7.0 / 550 5.7.1) | 降至 < 0.1% 后 4–12 周 |

低投诉率的核心操作手段：(a) 采用确认性订阅（confirmed opt-in / double opt-in）而非隐式获取地址；(b) 退订链接放置于邮件正文顶部（非页脚仅），与主要 CTA 按钮等视觉权重；(c) 对超过 90 天无任何互动（开信、点击）的收件人执行灰度休眠——降低发送频率或暂停发送；(d) 退订请求在 48 小时内批量处理完毕。

## 6. Postmaster Tools KPI 解读

域所有权验证完成后，Postmaster Tools 提供 7 天滚动窗口的六组数据面板：

* **垃圾邮件率** — 核心指标。由 `用户标记为垃圾邮件数 / 送达收件箱总数` 计算。面板中的红色区域为 ≥ 0.3% 的高风险区间。
* **IP 信誉** — 基于发件 IP 的历史递送行为评分（Bad / Low / Medium / High）。"Bad" 评分的典型恢复路径：停止从该 IP 发送 48 小时（冷却期），之后以极低量（< 500 封/天）重新开始，仅发送给已知活跃收件人。
* **域信誉** — 独立于 IP 的域级评分，受 SPF/DKIM/DMARC 配置完整性、邮件被转发后的认证链完整性（ARC 协议，RFC 8617）以及域历史年龄综合影响。新注册域（< 30 天）的域信誉起始分显著低于已建立域。
* **递送错误** — 按临时和永久错误分类，支持按日期和增强状态码过滤。每日应检查此面板以发现新错误类型。
* **加密率** — 入站至 Gmail 的 TLS 占比。目标是 ≥ 95%。低于此阈值的常见原因：发件 MTA 的 `smtp_tls_security_level` 设为 `none` 或配置的密码套件与 Google MX 不相交。
* **反馈环** — 投诉量趋势和按 IP/日期聚合。若不订阅 FBL，该面板为空。

## 7. 新 IP 预热策略

新发件 IP 地址不存在历史信誉数据——Google 的反垃圾引擎对其施加隐含的每日递送上限和更严格的垃圾邮件判定阈值。预热的目的在于逐日递增发送量，使引擎积累正面信号（低投诉、高互动）而非中性或负面信号。

7. 新 IP 预热策略

| 日期 | 每日目标量 | 收件人策略 |
| Day 1–2 | ≤ 2,000 | 仅最近 7 天有互动的用户 |
| Day 3–5 | 5,000 – 10,000 | 最近 30 天有互动的用户 |
| Day 6–10 | 20,000 – 50,000 | 最近 90 天有互动的用户 |
| Day 11–15 | 100,000 – 200,000 | 所有活跃用户 |
| Day 16–30 | 线性递增至目标量 | 剩余基数 |

预热期三不可：(a) 不可突然切换邮件内容类型——预热期发送的邮件在主题、发件人、内容模板上须与正式期完全一致；(b) 不可在投诉率超过 0.1% 时继续增加日发送量——应暂停增长而非削减已计划的量以保持基数稳定；(c) 不可在单个预热周期内变更 SPF/DKIM/DMARC 配置——DNS 变更引起的暂时认证波动会错误触发反垃圾引擎的负面评分。

本站技术文章采用 CC-BY 4.0 许可，可自由引用，仅需标注来源 [ztpop.net](https://www.ztpop.net)。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/gmail-deliverability-engineering.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
