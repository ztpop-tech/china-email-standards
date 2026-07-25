---
title: "邮件系统利旧迁移中的 DNS 过渡策略"
source: "https://ztpop.net/kb/email-migration-dns-transition-strategy.html"
license: CC-BY 4.0
---

# 邮件系统利旧迁移中的 DNS 过渡策略

## 摘要

邮件系统迁移过程中，DNS 配置的平滑过渡是决定切换成败的关键环节。MX 记录的缓存生存期（TTL）、SPF include 与 DMARC 策略的同步更新、混合场景下的双向路由配置，任何一项处理不当都可能导致邮件投递延迟、退信或触发反垃圾策略。本文系统阐述 DNS 过渡策略的三个核心阶段——预发布期、并行期和切换期，涵盖 MX 记录 TTL 的逐步递降方法、DNS 记录变更的原子化发布顺序、混合场景下 SPF include 的渐进式控制以及迁移完成后的 DMARC 策略调整。全文引用 RFC 5321（SMTP）、RFC 7208（SPF）[2]、RFC 7489（DMARC）[3] 及 RFC 1035（DNS 协议）。

## 1. DNS 过渡三阶段模型

```
┌───────────┐     ┌───────────┐     ┌───────────┐
│  预发布期   │ ──→ │   并行期   │ ──→ │   切换期   │
│  TTL 递降  │     │ 双 MX 共存 │     │  MX 迁移  │
│  记录预置  │     │  SPF 过渡  │     │  DMARC 调整│
│  验证测试  │     │  双向路由  │     │  清理回退 │
└───────────┘     └───────────┘     └───────────┘
```

1. DNS 过渡三阶段时间线与关键操作

| 阶段 | 周期 | 核心操作 | 风险评估 |
| 预发布期（T-14~T-7 天） | 1 周 | 降低 MX 记录 TTL；预发布目标系统 A 记录；测试 MX/SPF/DMARC | 低 |
| 并行期（T-7~T+0 天） | 1 周 | 追加目标系统 MX；更新 SPF include；部署双向连接器 | 中 |
| 切换期（T+0~T+7 天） | 1 周 | 调整 MX 优先级；验证 SPF 完整性；DMARC 策略降级→恢复 | 高 |

## 2. 预发布期：TTL 逐步递降

### 2.1 TTL 递降策略

MX 记录的 TTL 决定了 DNS 解析结果在递归服务器和客户端缓存中的存活时间。RFC 1035 §2.3.4 [1] 定义的 TTL 字段单位为秒。在迁移准备阶段，TTL 应从常规的 3600 秒（1 小时）逐步降低：

```
# TTL 递降时序

# T-14 天（2 周前）— 第一轮递降
# 原 TTL: 3600 (1 小时)
dig example.com MX
# example.com.  3600  IN  MX  10 mail.example.com.

# T-10 天 — 降至 1800 (30 分钟)
# 操作: 将 MX 记录的 TTL 从 3600 改为 1800
# 等待: 原 TTL 有效期结束（3600 秒内全球递归服务器更新）

# T-7 天 — 降至 600 (10 分钟)
# 操作: 将 MX 记录的 TTL 从 1800 改为 600
# 等待: 原 TTL 有效期结束（1800 秒内）

# T-3 天 — 降至 300 (5 分钟，最低建议值)
# 操作: 将 MX 记录的 TTL 从 600 改为 300
# 等待: 原 TTL 有效期结束（600 秒内）
```

### 2.2 TTL 递降原理

RFC 1034 §4.3.5 规定了递归名称服务器在 TTL 到期前不会重新查询权威服务器。直接将 3600 秒 TTL 的记录瞬间切为新 MX 会导致：

* 全球约 50% 的邮件服务器在 3600 秒内继续连接旧服务器
* 高流量接收端的队列策略偏差导致邮件分配不均
* 收信失败的发送方可能将旧服务器 IP 添加到黑名单

递降策略在 T-14 天启动，利用 14 天窗口 "冷却" 全球 DNS 缓存，在切日前确保所有解析器缓存 TTL ≤ 300 秒。

### 2.3 DNS 预发布验证

```
# 预发布期验证检查清单

# 1. 新邮件系统的 A/AAAA 记录可解析
dig A mx-new.example.com
dig AAAA mx-new.example.com

# 2. 新系统的 SMTP 端口可达
timeout 5 bash -c 'echo "EHLO test" | openssl s_client -connect mx-new.example.com:25 -starttls smtp 2>/dev/null'
# 预期返回 250 欢迎消息

# 3. 新系统的 TLS 证书有效
openssl s_client -connect mx-new.example.com:25 -starttls smtp 2>/dev/null | \
  openssl x509 -noout -dates

# 4. 测试邮件
# 从外部服务器发送测试邮件至新 MX（直接指定 IP 绕过 DNS）
swaks --to user@example.com --server mx-new.example.com --port 25 --tls
```

## 3. 并行期：双 MX + SPF 过渡

### 3.1 双 MX 共存配置

并行期内，域名同时指定新旧系统的 MX 记录，通过优先级（Preference）值控制邮件投递的优先级顺序。RFC 5321 §5.1 定义了 MX 优先级机制——值越小优先级越高。

```
# 并行期 MX 记录（T-7 ~ T+0）
# 旧系统优先级较高（10），新系统优先级较低（20）
# → 发送者优先尝试旧系统，旧系统将收件人在新系统的邮件中继过去
example.com.  300  IN  MX  10 mail-old.example.com.
example.com.  300  IN  MX  20 mail-new.example.com.

# 对于依赖 "connect to MX with lowest preference" 的实现，
# 如果发送者连接旧系统但目标用户已在新的系统，
# 则需要配置旧系统到新系统的 SMTP 中继（双向路由）
```

**重要：** 双 MX 的优先级配置方式取决于迁移策略：

* **批次迁移（Staged Migration）：** 旧系统优先级高（10），新系统优先级低（20）。旧系统将已迁移用户的邮件中继至新系统（反向中继同样配置）。此模式下旧系统保持主要接收角色。
* **一次性 Cutover：** 在切换时刻前，新系统的优先级已降至与旧系统相同（并列 10）。在切换时刻，将旧优先级撤除或置为更高（如 30），同时将新系统设为唯一 10。

### 3.2 SPF include 过渡策略

SPF（Sender Policy Framework）记录定义了允许代表域名发送邮件的 IP 地址范围。RFC 7208 [2] §5.2 定义了 `include` 机制的语义。迁移场景下，SPF 记录的过渡关键点：

```
# 并行期 SPF 记录 — 同时 include 新旧系统的发送源

# 旧 SPF（迁移前）:
# example.com.  TXT  "v=spf1 ip4:203.0.113.0/24 -all"

# 第一阶段 SPF（并行期开始）:
example.com.  600  TXT  "v=spf1 ip4:203.0.113.0/24 include:_spf-new.example.com -all"

# 第二阶段 SPF（并行期中期，测试确认新系统可正常发信后）:
example.com.  600  TXT  "v=spf1 include:_spf-old.example.com include:_spf-new.example.com -all"

# 切换阶段 SPF（新系统为主，旧系统为备）:
example.com.  600  TXT  "v=spf1 include:_spf-new.example.com include:_spf-old.example.com -all"

# 迁移完成后 SPF（仅保留新系统）:
example.com.  600  TXT  "v=spf1 include:_spf-new.example.com -all"

# SPF include 记录示例（_spf-new.example.com）:
_spf-new.example.com.  600  TXT  "v=spf1 ip4:198.51.100.0/24 ip6:2001:db8::/32 -all"
```

### 3.3 SPF DNS 查找次数约束

RFC 7208 §4.6.4 规定 SPF 评估过程中 DNS 查询次数不得超过 10 次（包括 `include`、`redirect`、`mx` 等机制的展开）。在过渡期，额外 include 一个新系统可能会增加查询计数。建议：

* 将新系统的发送 IP 封装为独立的 SPF 子记录（如 `_spf-new.example.com`），此 include 计为 1 次查询
* 避免在过渡期内同时 include 超过 3 个外部域
* 使用 `ip4`/`ip6` 机制直接列出 IP 段以减少查询次数

## 4. 切换期：MX 转移与 DMARC 策略调整

### 4.1 MX 优先级切换

```
# 切换时刻（T+0）— 将 MX 优先级反转
# 旧系统从 10→30（备份角色），新系统从 20→10（主要角色）
example.com.  300  IN  MX  10 mail-new.example.com.
example.com.  300  IN  MX  30 mail-old.example.com.

# 切换后 48 小时 — 移除旧 MX（确认所有旧邮箱已迁移）
# example.com.  300  IN  MX  10 mail-new.example.com.

# 验证切换后的 MX 记录
dig example.com MX +short | sort -n
# 10 mail-new.example.com.
# 等待：原 MX 缓存 TTL 全部过期（300 秒）
# 确认: 从外部发送测试邮件，确保正常接收
```

### 4.2 DMARC 策略过渡

DMARC 策略（RFC 7489 [3]）在迁移期需要特别关注。迁移初期新旧系统的 DKIM/DMARC 签名可能存在不一致：

```
# 迁移前 DMARC — 严格策略
# _dmarc.example.com.  TXT  "v=DMARC1; p=reject; sp=reject; pct=100; rua=mailto:dmarc@example.com; ruf=mailto:dmarc-forensic@example.com"

# 迁移准备期 DMARC — 降级为隔离策略（便于识别新旧系统问题）
_dmarc.example.com.  600  TXT  "v=DMARC1; p=quarantine; sp=quarantine; pct=25; rua=mailto:dmarc@example.com"

# 并行期 DMARC — 逐步提高采样率
_dmarc.example.com.  600  TXT  "v=DMARC1; p=quarantine; sp=quarantine; pct=50; rua=mailto:dmarc@example.com"

# 切换稳定期 — 确认 DKIM 签名正常后恢复
_dmarc.example.com.  600  TXT  "v=DMARC1; p=quarantine; sp=quarantine; pct=100; rua=mailto:dmarc@example.com"

# 迁移完全稳定后 — 恢复 reject 策略
_dmarc.example.com.  3600  TXT  "v=DMARC1; p=reject; sp=reject; pct=100; rua=mailto:dmarc@example.com; ruf=mailto:dmarc-forensic@example.com"
```

### 4.3 DKIM 密钥部署与验证

```
# 在迁移准备期提前部署新系统的 DKIM 密钥到 DNS
# selector: s202607
s202607._domainkey.example.com.  600  TXT  "v=DKIM1; h=sha256; k=rsa; p=MIGfMA0GCSqGSIb4DQEBAQUAA4GNADCBiQKBgQC4..."

# 在并行期启用双重签名（新旧系统各自签名）
# 旧系统继续使用 s202507 签名，新系统使用 s202607 签名
# DMARC 策略宽松，接受任一签名通过

# 切换后移除旧 DKIM 记录
# 保留 s202607 为新系统的唯一签名
```

## 5. 混合场景下的双向路由配置

### 5.1 SMTP 连接器配置

在并行期内，用户邮箱分布在两个系统中。邮件流需能正确跨系统投递：

```
# Postfix 示例 — 并行期双向路由

# 旧系统的 Postfix 配置（mail-old）
# 将发送至新系统的邮件中继
# /etc/postfix/transport
new.example.com   smtp:[mail-new.example.com]:25

# 新系统的 Postfix 配置（mail-new）
# 将发送至旧系统的邮件中继
# /etc/postfix/transport
old.example.com   smtp:[mail-old.example.com]:25

# 回退路由配置（防止 5.1.1 退信）
# 默认传输方式 — 发送者未在新/旧系统找到收件人时回退至 MX 查询
default_transport = smtp

# 邮件流日志监控
tail -f /var/log/mail.log | grep "status=sent (250 2.0.0 Ok)"
```

### 5.2 SRS（Sender Rewriting Scheme）配置

当邮件从一个系统中继到另一个系统时，SPF 检查可能失败。SRS（RFC 修改草案）通过重写信封发件人解决这一问题：

```
# Postfix 集成 SRS (通过 postsrsd)
# 安装并配置 postsrsd
# 在 master.cf 中配置 SRS 过滤

# 并行期 SRS 配置
# 旧系统出站中继时 — 将 SRS0= 前缀添加到信封发件人
# 示例: SRS0=XXXX=YY=old.example.com=user@old.example.com

# SRS 密钥配置（两侧系统需共享密钥）
# /etc/default/postsrsd
SRS_DOMAIN=example.com
SRS_EXCLUDE_DOMAINS=new.example.com,old.example.com
SRS_SECRET=/etc/postsrsd/srs_secret
SRS_HASH_LENGTH=4
SRS_HASH_MIN_LENGTH=4

# SRS 逆向 — 新系统收到的 SRS 邮件还原为原始发件人
# postsrsd 自动处理正向和逆向转换
```

## 6. 回滚方案

即使在有序过渡后，迁移仍可能遇到不可预见的问题。DNS 回滚方案应作为备份计划：

```
# 回滚 MX 记录 — 恢复旧系统的优先级
example.com.  300  IN  MX  10 mail-old.example.com.
example.com.  300  IN  MX  20 mail-new.example.com.

# 回滚 SPF 记录
example.com.  600  TXT  "v=spf1 ip4:203.0.113.0/24 include:_spf-new.example.com -all"

# 回滚 DMARC 策略
_dmarc.example.com.  600  TXT  "v=DMARC1; p=quarantine; pct=25; rua=mailto:dmarc@example.com"

# 验证回滚后的正常服务
# 检查邮件流是否回到旧系统
# 验证 SPF 检查结果
# 确认旧系统队列情况

# 回滚触发条件（任一满足立即执行）
# 1. 新系统 5.2.2 退信率超过 5%
# 2. SPF/DKIM/DMARC 通过率在 12 小时内低于 90%
# 3. 新用户无法在 30 分钟内成功收发
```

## 7. 完整过渡清单

2. DNS 过渡执行清单

| 步骤 | 操作内容 | 完成标记 |
| 1 | 降低 MX 记录 TTL 至 300 秒（至少迁移前 7 天完成） | □ |
| 2 | 预发布目标邮件系统的 A/AAAA 记录 | □ |
| 3 | 预部署新系统的 DKIM 公钥 DNS 记录 | □ |
| 4 | 配置旧系统→新系统的 SMTP 中继连接器 | □ |
| 5 | 配置新系统→旧系统的 SMTP 中继连接器 | □ |
| 6 | 配置并测试 SRS 双向转换 | □ |
| 7 | 追加 target MX 记录（和旧 MX 同时存在） | □ |
| 8 | 更新 SPF include 加入新系统发送源 | □ |
| 9 | 降级 DMARC 策略为 quarantine (pct=25) | □ |
| 10 | 测试并行双向邮件流（内部+外部） | □ |
| 11 | DMARC pct 逐步提升至 50→100 | □ |
| 12 | 切换 MX 优先级（新系统为主） | □ |
| 13 | 稳定 48 小时后移除旧 MX | □ |
| 14 | 清理 SPF 移除旧 include | □ |
| 15 | DMARC 恢复 reject 策略 | □ |
| 16 | 移除旧的 DKIM 公钥记录 | □ |
| 17 | MX TTL 恢复正常值（3600+） | □ |

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-migration-dns-transition-strategy.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
