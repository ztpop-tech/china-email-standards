---
title: "SRS (Sender Rewriting Scheme) 地址重写实践：SRS0/SRS1与SPF/DMARC对齐"
source: "https://ztpop.net/kb/srs-rewriting-guide.html"
license: CC-BY 4.0
---

# SRS (Sender Rewriting Scheme) 地址重写实践：SRS0/SRS1与SPF/DMARC对齐

#### 📑 目录

1. [SRS 的背景与问题域](#s1)
2. [SRS0 签名机制](#s2)
3. [SRS1 验证与逆写回](#s3)
4. [SRS 与 SPF 的转发对齐关系](#s4)
5. [SRS 与 DMARC 的对齐冲突](#s5)
6. [Postfix postsrsd 部署](#s6)
7. [排错与监控](#s7)

## 一、SRS 的背景与问题域

SRS（Sender Rewriting Scheme）解决邮件转发（mail forwarding / mailing list）场景下的 SPF 检查失败问题。RFC 7208（SPF）Section 2.5 明确说明——SPF 授权的是原始发件人域的 SMTP 发送者（MAIL FROM），而在邮件转发场景中，转发 MTA（Forwarder）的 IP 并未被原始发件域 SPF 所授权，因此收件 MTA 对转发邮件的 SPF 检查必然失败。

SPF 失败的后果在 DMARC 策略下被放大——RFC 7489（DMARC）Section 3.1 规定当 SPF 或 DKIM 任一通过且 **标识符对齐**（Identifier Alignment）满足时，DMARC 通过。但转发破坏了 SPF 的 `MAIL FROM` 域与 RFC 5322.From 域的对齐，导致 DMARC 失效，收件方可能将邮件标记为垃圾或直接拒绝。

SRS 的解决思路：在转发 MTA 上将 `MAIL FROM` 信封地址重写为转发域自己的地址，同时保留原始发件人信息在 SRS 签名中，使后续的 SPF 检查基于转发域的授权 IP 通过。

## 二、SRS0 签名机制

### 2.1 SRS0 地址格式

SRS 地址遵循以下结构（RFC 目前为 Informational 草案，Draft of SRS Specification by Shevek）：

```
SRS0+<hash>=<original_domain>=<original_local>@<forwarder_domain>

# 示例:
# 原始邮件: MAIL FROM: <alice@example.com>
# 转发域: forward.example.net
# SRS 重写后: MAIL FROM: <SRS0=HHH=example.com=alice@forward.example.net>
```

### 2.2 签名字段分解

表 1：SRS0 地址字段

| 字段 | 示例 | 说明 |
| --- | --- | --- |
| Prefix | `SRS0` | 版本标识，SRS0 = 第一代 |
| Hash | `HHH` | 基于密钥的 HMAC 签名（Base64 URL-safe，通常 3 字符） |
| Delimiter | `=` | 等号分隔（也可使用 `-` 或 `+`） |
| Original Domain | `example.com` | 原始发件人域 |
| Original Local | `alice` | 原始发件人 local-part |
| Forwarder Domain | `forward.example.net` | 转发域（@ 之后的部分） |

### 2.3 HMAC 签名计算

```
# postsrsd 使用的签名算法（HMAC-SHA1）
SRS_SECRET_KEY=$(cat /etc/srs_secret)
echo -n "SRS0=example.com=alice@forward.example.net" \
  | openssl dgst -sha1 -hmac "$SRS_SECRET_KEY" -binary \
  | openssl base64 | tr '+/' '-_' | cut -c1-3
# 输出 3 字符 hash，如 HHH

# 完整的 SRS0 地址构建
SRS_HASH=$(echo -n "SRS0=example.com=alice@forward.example.net" \
  | openssl dgst -sha1 -hmac "$SRS_SECRET_KEY" -binary \
  | openssl base64 | tr '+/' '-_' | cut -c1-3)
echo "SRS0=${SRS_HASH}=example.com=alice@forward.example.net"
```

## 三、SRS1 验证与逆写回

### 3.1 SRS1 的作用

当邮件经过**多级转发**时，SRS0 地址会被再次重写。SRS1 地址格式 `SRS1+<hash>=<forwarder>=<SRS0_address>@<next_forwarder>`，可以链式解包至原始 SRS0。

当收件 MTA 收到 bounce（退信/NDR）时，其 SMTP RCPT TO 指向 SRS 重写后的 `SRS0+...+...@forward.example.net`。最终转发 MTA（在 SRS 逆写端）需验证 hash 正确性，再将退信投递到原始发件人。

### 3.2 逆写（Decoding / Reverse）

```
# postsrsd 自动处理 SRS 逆写
# 验证流程:
# 1. 提取 hash 部分
# 2. 使用相同密钥重新计算期望 hash
# 3. 比较 hash 是否一致 (constant-time compare)
# 4. 一致则解包: alice@example.com
# 5. 不一致则丢弃（可能的伪造退信攻击）

# 手动验证（Debug 场景）
EXPECTED_HASH=$(echo -n "SRS0=example.com=alice@forward.example.net" \
  | openssl dgst -sha1 -hmac "$(cat /etc/srs_secret)" -binary \
  | openssl base64 | tr '+/' '-_' | cut -c1-3)

RECEIVED_HASH=$(echo "$SRS_ADDRESS" | cut -d'=' -f1 | cut -d'+' -f2)

if [ "$EXPECTED_HASH" = "$RECEIVED_HASH" ]; then
  echo "SRS 验证通过，原始发件人: alice@example.com"
else
  echo "SRS 验证失败，疑似伪造退信"
fi
```

### 3.3 密钥轮换策略

postsrsd 支持多密钥轮换：

```
# /etc/default/postsrsd
SRS_SECRET=/etc/postsrsd/srs_secret
SRS_SECRET_ROTATED=/etc/postsrsd/srs_secret.old
SRS_DOMAIN=forward.example.net
SRS_EXCLUDE_DOMAINS=example.net,forward.example.net
SRS_SEPARATOR==
# 旧密钥用于验证（接收时），新密钥用于签名（发送时）

# 密钥轮换步骤:
# 1. 生成新密钥
openssl rand -base64 32 > /etc/postsrsd/srs_secret.new
# 2. 将旧密钥移至 rotated
cp /etc/postsrsd/srs_secret /etc/postsrsd/srs_secret.old
# 3. 部署新密钥
cp /etc/postsrsd/srs_secret.new /etc/postsrsd/srs_secret
# 4. 重启 postsrsd
systemctl restart postsrsd
# 5. 7-14 天后删除旧密钥（确保所有 SRS bounce 已在 TTL 内超时）
rm /etc/postsrsd/srs_secret.old
```

## 四、SRS 与 SPF 的转发对齐关系

### 4.1 转发场景下的 SPF 断裂

```
原始发件域: example.com (SPF: include:_spf.example.com → IP: 198.51.100.1)
转发 MTA:    forward.example.net (IP: 203.0.113.50)
收件域:      target.com

未使用 SRS 的流程:
1. alice@example.com → SMTP MAIL FROM: <alice@example.com>
2. forward.example.net 转发: SMTP MAIL FROM: <alice@example.com> (不变)
3. target.com 做 SPF 检查: MAIL FROM 域 = example.com
   → 查询 example.com SPF: 授权 IP = 198.51.100.1
   → 实际连接 IP = 203.0.113.50 (转发 MTA)
   → SPF 检查: FAIL
4. DMARC 评估: SPF 未通过，DKIM 可能被转发 MTA 去除或无效 → DMARC FAIL

使用 SRS 后的流程:
1. forward.example.net SRS 重写 MAIL FROM: <SRS0=HHH=example.com=alice@forward.example.net>
2. target.com SPF 检查: MAIL FROM 域 = forward.example.net
   → 查询 forward.example.net SPF: 授权 IP = 203.0.113.50
   → 实际连接 IP = 203.0.113.50 → SPF: PASS
3. DMARC 评估: DKIM 通过 OR SPF pass with forward.example.net
   → 但 5322.From 仍是 alice@example.com → Alignment 检查
```

### 4.2 SPF 配置中对 SRS 的配合

转发域必须配置 SPF 授权本域的所有邮件服务器 IP，以便重写后的 SRS 地址通过 SPF：

```
# forward.example.net 的 SPF 记录
forward.example.net.  TXT  "v=spf1 mx a:relay1.forward.example.net -all"
# 确保所有转发 MTA 的 IP 在 SPF 授权列表中

# 如果转发 MTA 使用云服务，使用 include 机制
forward.example.net.  TXT  "v=spf1 include:_spf.forward.example.net -all"
```

## 五、SRS 与 DMARC 的对齐冲突

### 5.1 对齐冲突的根本原因

DMARC 的 SPF Identifier Alignment 要求 `MAIL FROM` 域与 `RFC 5322.From` 域在组织域（Organizational Domain）层面一致。SRS 将 MAIL FROM 域改写为转发域，导致：

* **SPF 通过**（基于重写后的 5321.MAIL FROM 域检查）
* **但 SPF 对齐失败**（因为 5321 域 ≠ 5322.From 域）
* **DMARC 依赖 DKIM 对齐**：如果转发 MTA 不重写 DKIM 签名（实际上必须不重写才能保持 DKIM 有效），且原始 DKIM 签名域的 d= 域与 5322.From 域对齐，则 DMARC 仍可通过

### 5.2 DKIM 对齐的关键性

RFC 7489 Section 3.1.1 定义 DMARC 的 SPF 对齐模式：  
`SPF 通过 + SPF 对齐` 或 `DKIM 通过 + DKIM 对齐`，满足任一即可通过 DMARC。

SRS 实施后，SPF 虽然通过但对齐必然失败。因此 DMARC 的通过完全依赖 **DKIM 签名在转发路径中不被剥离**。

```
# 配置转发 MTA 保留 DKIM 签名（不重写头部）
# /etc/postfix/main.cf
# 如果是 after-queue content_filter 方式转发，确保不要剥离 DKIM
# 以下参数确保 Postfix 不自动添加/修改 DKIM:
disable_mime_output_conversion = yes
# Do not canonicalize mail headers
canonical_maps = (不设置任何 canonical map)

# 配置 OpenDKIM milter 不对已有 DKIM 签名的邮件重新签名
# /etc/opendkim.conf:
Mode = sv                # sign + verify
SignatureAlgorithm = rsa-sha256
Canonicalization = relaxed/simple
# 已有 DKIM 签名的邮件不重新签名
SignHeaders = (未显式设置，使用默认集)
```

### 5.3 DMARC 报告中的表现

```
# 从 DMARC 聚合报告（RUA）中识别 SRS 影响
# DMARC 报告中 SPF 对齐失败但 DKIM 对齐通过的条目:
# <record>
#   <row>
#     <source_ip>203.0.113.50</source_ip>
#     <count>1250</count>
#     <policy_evaluated>
#       <disposition>none</disposition>  <!-- 未采取动作 -->
#       <dkim>pass</dkim>
#       <spf>pass</spf>
#     </policy_evaluated>
#   </row>
#   <identifiers>
#     <header_from>example.com</header_from>
#     <envelope_from>forward.example.net</envelope_from>  <!-- SRS 改写 -->
#   </identifiers>
# </record>
# 
# 从 XML 看出 SPF 对齐失败（header_from ≠ envelope_from）但 DKIM 对齐通过

# 使用 rmtree2json 解析报告
parse-dmarc-xml report.xml | jq '.records[].identifiers'
```

### 5.4 DMARC p=reject 域的 SRS 挑战

表 2：DMARC 策略对 SRS 的影响

| 发件域 DMARC 策略 | SRS 后 DKIM 状态 | DMARC 结果 | 收件域动作 |
| --- | --- | --- | --- |
| p=none | DKIM 有效且对齐 | 通过 | 正常投递 |
| p=none | DKIM 无效/丢失 | 未通过（仅 SPF failed alignment） | 根据本地策略 |
| p=quarantine | DKIM 有效且对齐 | 通过 | 正常投递 |
| p=quarantine | DKIM 无效/丢失 | 未通过 | 进入垃圾箱 |
| p=reject | DKIM 有效且对齐 | 通过 | 正常投递 |
| p=reject | DKIM 无效/丢失 | 未通过 | 被拒收（550 5.7.1） |

**核心结论**：在 DMARC p=reject 域广泛部署的今天，SRS 的实施必须确保原始 DKIM 签名在转发路径中完整保留。任何破坏 DKIM 签名的转发操作（如修改邮件 body、转换 MIME encoding、添加/删除头部）都将导致 DMARC 失败和邮件拒收。

## 六、Postfix postsrsd 部署

### 6.1 安装

```
# Debian / Ubuntu
apt-get install postsrsd

# CentOS / RHEL (EPEL)
yum install epel-release
yum install postsrsd

# 编译安装（获取最新版本）
git clone https://github.com/roehling/postsrsd.git
cd postsrsd
make
make install
```

### 6.2 配置

```
# /etc/default/postsrsd (Debian) / etc/sysconfig/postsrsd (RHEL)
SRS_SECRET=/etc/postsrsd/srs_secret
SRS_DOMAIN=forward.example.net
SRS_EXCLUDE_DOMAINS=localdomain,localhost.localdomain,example.net
SRS_SEPARATOR==
SRS_HASHLENGTH=4          # Hah length（字符数），默认 4
SRS_HASHMIN=4             # 最小 hash 长度

# 生成初始密钥
openssl rand -base64 32 > /etc/postsrsd/srs_secret
chmod 640 /etc/postsrsd/srs_secret
chown root:postsrsd /etc/postsrsd/srs_secret

# 启动
systemctl enable postsrsd
systemctl start postsrsd

# 验证监听
ss -tlnp | grep 10001
# postsrsd 监听 127.0.0.1:10001
```

### 6.3 Postfix 集成

```
# /etc/postfix/main.cf — postsrsd 集成

# SRS 正向（出站转发时重写 MAIL FROM）
sender_canonical_maps = tcp:127.0.0.1:10001
sender_canonical_classes = envelope_sender

# SRS 逆向（入站 bounce 时解包）
recipient_canonical_maps = tcp:127.0.0.1:10002
recipient_canonical_classes = envelope_recipient

# 排除不需要 SRS 重写的域
# 对于收件方的本域邮件，不应做 SRS
canonical_maps = (空或特定域)

# 重要：仅在转发链中启用 SRS，避免对本域出站邮件做 SRS
# /etc/postfix/transport 区分：
# 本域投递使用 local 而无需 SRS
# 外部域转发走 smtp 并使用 SRS
```

### 6.4 验证

```
# 验证 SRS 正向重写
echo "SRS forward test example.com alice" | nc -w1 127.0.0.1 10001
# 预期输出: SRS0=XXXX=example.com=alice@forward.example.net

# 验证 SRS 逆向解包
echo "SRS reverse SRS0=XXXX=example.com=alice@forward.example.net" \
  | nc -w1 127.0.0.1 10002
# 预期输出: alice@example.com

# 日志验证
tail -f /var/log/mail.log | grep "srs:"
# Jul 24 10:00:00 mx1 postsrsd[12345]: srs_forward: alice@example.com -> SRS0=YYYY=example.com=alice@forward.example.net
# Jul 24 10:00:05 mx1 postsrsd[12346]: srs_reverse: SRS0=YYYY=example.com=alice@forward.example.net -> alice@example.com
```

## 七、排错与监控

### 7.1 常见问题

表 3：SRS 常见问题与排查

| 问题 | 现象 | 原因 | 解决方法 |
| --- | --- | --- | --- |
| SRS 签名验证失败 | 退信进入转发域邮件管理员邮箱 | 密钥不一致（多台转发 MTA 使用不同密钥） | 所有转发 MTA 共享同一 SRS\_SECRET |
| DMARC 失败 | 转发邮件被拒收 | DKIM 签名在转发中被破坏 | 确认 MTA 不修改邮件体/头部；保留原始 DKIM |
| SRS hash 冲突 | 误将合法退信当作伪造 | hash 长度过短（默认 4 个字符碰撞概率） | 设置 `SRS_HASHLENGTH=8` |
| SRS exclude 不生效 | 本域邮件也被 SRS 改写 | SRS\_EXCLUDE\_DOMAINS 格式错误 | 确保域列表用逗号分隔，不含空格 |
| SRS 地址超长 | SMTP 会话拒绝 | RFC 5321 限制 MAIL FROM 长度 256 字符 | 限制 local-part 长度；放大 recipient\_limit |

### 7.2 监控建议

```
# Prometheus 文本收集器
cat > /etc/prometheus/srs-metrics.sh << 'SCRIPT'
#!/bin/bash
# postsrsd - 统计 SRS 重写次数
SRS_FORWARD=$(journalctl -u postsrsd --since "5 min ago" | grep -c "srs_forward")
SRS_REVERSE=$(journalctl -u postsrsd --since "5 min ago" | grep -c "srs_reverse")
SRS_VERIFY_FAIL=$(journalctl -u postsrsd --since "5 min ago" | grep -c "verification failed")

cat <
```

### 7.3 RFC 的 SRS 规范状态

SRS 的规范状态是 Informational 草案（Draft of SRS Specification），IETF 未将其 RFC 标准化。但 SRS 已成为邮件转发场景中解决 SPF 断裂的事实标准，被 postsrsd、opendmarc 和众多反垃圾引擎广泛采用。RFC 7208（SPF）Section 2.5 提到了 SRS 作为转发 SPF 问题的解决方案之一，并鼓励部署 SRS 的转发 MTA 为 SRS 地址添加对应的 SPF 授权。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/srs-rewriting-guide.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
