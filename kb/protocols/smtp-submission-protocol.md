---
title: "SMTP Submission 协议深度解析 — RFC 6409 与 RFC 8314：端口 587/465 的投稿与加密演进"
source: "https://ztpop.net/kb/smtp-submission-protocol.html"
license: CC-BY 4.0
---

# SMTP Submission 协议深度解析 — RFC 6409 与 RFC 8314：端口 587/465 的投稿与加密演进

## 1. MSA 与 MTA 的角色分离

RFC 6409 §2 明确定义了 Message Submission Agent (MSA) 的角色 [1]。MSA 与 MTA 的关键区别在于：

表1：MSA vs MTA 角色对比

| 属性 | MTA（端口 25） | MSA（端口 587） |
| RFC | RFC 5321 §2.3.8 | RFC 6409 §2 |
| 认证要求 | 不强制（开放中继已禁用） | MUST 要求 AUTH（RFC 4954） |
| 连接来源 | 对方 MTA（出站端口 25） | 终端用户 MUA |
| 策略执行 | 反垃圾/反病毒筛选 | 合成检查（From/Date/Message-ID）、配额检查、域名验证 |
| 修改权限 | 不得修改信头 | 可自动补全缺失的信头 |
| 默认端口 | 25 | 587（STARTTLS）或 465（隐式 TLS） |

MSA 通常位于网络边界内部（如公司内网），或通过 SMTP AUTH 接受来自外部的经过认证的连接。成功认证后，MSA 会将经过筛选和修订的邮件转发给同一台机器（或内网中）的 MTA，由 MTA 负责后续的 MX 路由和出站投递。

## 2. 端口 587 与 465 的演进

### 2.1 端口 587：RFC 6409 的标准 Submission 端口

RFC 6409 (2011) 将 Submission 端口标准化为 587，协议约束如下 [1]：

* 必须使用 SMTP AUTH（默认）
* MUST 要求 STARTTLS（后来由 RFC 8314 升级为隐式 TLS）
* MUST 验证发件人身份
* MAY 自动补全缺失的 Date、Message-ID、From 等信头
* MUST NOT 为开放的 SMTP 中继（仅限经过认证的用户）

### 2.2 端口 465：隐式 TLS 的前世今生

端口 465 有一段曲折的历史。1997 年，多个邮件客户端供应商（Netscape、Microsoft、Eudora）非标准地注册了 `smtps` 端口 465，用于以隐式 TLS（Implicit TLS）模式封装整个 SMTP 会话——即建立 TCP 连接后立即开始 TLS 握手，而非 STARTTLS 式的协议升级 [2]。

1998 年，IANA 撤销了对 `smtps` 的端口分配，转为分配给 `urd`（一个未使用的协议）。但供应商实现已经固化——大量邮件客户端将 465 视为隐式 TLS submission 端口。这种事实标准与 IANA 官方分配之间的拉锯持续了整整 20 年。

2018 年，RFC 8314 正式承认了这一事实状态，按已实际用法的相反方向做出了明确裁决：不仅承认 465 为隐式 TLS 的 SMTP Submission 端口，还将隐式 TLS 列为 MUA→MTA 通信的推荐加密模式 [3]。

RFC 8314 的核心结论 [3, §3]：

* 端口 465 正式注册为 `submissions` 的隐式 TLS submission 端口
* 端口 587 继续用于 STARTTLS submission
* 明文（cleartext）的 MUA→MTA 通信已被弃用（considered obsolete）
* 所有新的 MUA 实现应优先使用隐式 TLS（端口 465 或 993/995 对应 IMAP/POP3）

## 3. RFC 6409 的 MSA 行为规范

### 3.1 信头处理规则

RFC 6409 §5 定义了 MSA 对 RFC 5322 信头的处理规则 [1]：

* **Date：** 如果缺失，MSA 必须添加当前时间戳
* **From：** 如果缺失，MSA 必须使用认证用户地址添加；如果存在但不匹配认证身份，MSA 应拒绝邮件（550 5.7.1）
* **Message-ID：** 如果缺失，MSA 必须生成唯一 ID 并添加
* **Return-Path：** MSA 最后的 MTA 跳负责设置（通常由 MSA 自身设置）
* **Received：** MSA 必须添加自己的 Received 头

### 3.2 命令限制

Submission 场景下，MSA 不对以下 SMTP 扩展负责：

* ETRN（RFC 1985）— 队列触发命令，仅限 MTA 使用
* ATRN — 同上
* VRFY — 用户验证命令，Submission 端口应禁用
* EXPN — 邮件列表展开命令，应禁用

## 4. Postfix Submission 配置实战

### 4.1 端口 587（STARTTLS）配置

```
# /etc/postfix/master.cf
# submission 服务定义（端口 587）
submission inet n       -       y       -       -       smtpd
  -o syslog_name=postfix/submission
  -o smtpd_tls_security_level=encrypt
  -o smtpd_tls_wrappermode=no
  -o smtpd_sasl_auth_enable=yes
  -o smtpd_relay_restrictions=permit_sasl_authenticated,reject
  -o smtpd_recipient_restrictions=
      permit_sasl_authenticated,reject_unauth_destination
  -o milter_macro_daemon_name=ORIGINATING
  -o smtpd_client_connection_count_limit=10
  -o smtpd_client_message_rate_limit=60
  -o strict_rfc821_envelopes=yes

# SASL 配置
smtpd_sasl_type = dovecot
smtpd_sasl_path = private/auth
smtpd_sasl_auth_enable = yes
broken_sasl_auth_clients = yes
```

### 4.2 端口 465（隐式 TLS）配置

```
# /etc/postfix/master.cf
# smtps 服务（端口 465，隐式 TLS）
smtps     inet  n       -       y       -       -       smtpd
  -o syslog_name=postfix/smtps
  -o smtpd_tls_wrappermode=yes
  -o smtpd_sasl_auth_enable=yes
  -o smtpd_relay_restrictions=permit_sasl_authenticated,reject
  -o smtpd_recipient_restrictions=
      permit_sasl_authenticated,reject_unauth_destination
  -o milter_macro_daemon_name=ORIGINATING
  -o smtpd_client_connection_count_limit=10
  -o smtpd_client_message_rate_limit=60
  -o strict_rfc821_envelopes=yes

# master.cf 中 smtps 的 TLS 配置
# 隐式 TLS 无需 smtpd_tls_security_level=encrypt 或 may
# wrappermode=yes 自动接管 TLS
```

### 4.3 信头补全配置（现代 Postfix）

```
# 自动补全缺失的 Date、Message-ID 等信头
smtpd_header_checks = pcre:/etc/postfix/submission_header_checks

# /etc/postfix/submission_header_checks
/^Received:.*/                  IGNORE
/^$/ ADD Received: from [auth_user] with SUBMISSION (Postfix)
/^$/ ADD Date: <time>
/^$/ ADD Message-ID: <unique>
```

以上实现较为基础。更完整的信头补全可借助始终开启的 milter（如 OpenDKIM 和 OpenDMARC）实现。

## 5. 4444 端口与其他非标准端口

除了 587 和 465，部分服务商使用非标准端口（2525、4444、5870 等）作为 Submission 端口。这些端口主要用于以下场景：

* 避免某些网络环境下（如公共 Wi-Fi、酒店网络）对 25/587/465 的 TCP 端口封锁
* 备用 Submission 通道，用于紧急情况

非标准端口的使用建议：

* 作为备选的 submit 端口，不应取代 587/465
* 强制要求 STARTTLS 或隐式 TLS
* 强制要求 AUTH
* 在客户端配置中优先级最低

## 6. Submission 场景的常见问题

### 6.1 认证失败

客户端端口 587 连接正常但发送邮件被拒：

```
# 日志定位
$ grep "submission" /var/log/mail.log | grep "SASL" | tail -5
postfix/submission[12345]: warning: SASL authentication failure:
  no mechanism available for user@example.com
postfix/submission[12345]: lost connection after AUTH from
  [192.0.2.1]

# 常见原因：
# 1. Dovecot SASL socket 权限问题
# 2. 客户端使用了不支持的认证机制（如 CRAM-MD5 但服务器未开启）
# 3. 密码中包含了 SMTP 协议的冲突字符（如空格、冒号）

# 排查
$ ls -la /var/spool/postfix/private/auth  # 确认 socket 存在且权限 666
```

### 6.2 中继拒绝

```
# submission 端口上的中继拒绝
postfix/submission[12346]: NOQUEUE: reject:
  RCPT from [192.0.2.1]:55545: 554 5.7.1 Relay access denied

# 检查 relay_restrictions 策略：
# permit_sasl_authenticated 必须在 reject 之前
```

### 6.3 TLS 版本不匹配

某些老旧客户端仅支持 TLS 1.0/1.1。RFC 8996 已弃用这两者，但如需兼容：

```
# 仅在 Submission 端口上同时启用 TLS 1.0/1.1/1.2/1.3
# 用于老旧客户端兼容
submission ... smtpd
  -o smtpd_tls_protocols=!SSLv2,!SSLv3
```

但强烈建议在兼容期过后立即移除 TLS <1.2 支持。

## 7. 隐式 TLS vs STARTTLS 的工程争议

RFC 8314 的发布在工程社区中引发了一场持续至今的辩论。STARTTLS 的优势在于端口号复用和渐进式升级——同一端口（587）可同时处理 TLS 和非 TLS 连接（虽然在 Submission 场景中必须要求 STARTTLS）。隐式 TLS 的优势在于协议栈清晰——一旦 TCP 连接建立，立即开始 TLS 握手，不存在 STRIPTLS 中间人攻击的可能 [2]。

IMAP 和 POP3 的隐式 TLS 端口（993/995）从 1990 年代起就一直稳定运行，RFC 8314 将同一模式应用到 SMTP Submission。目前主流邮件客户端的默认行为是：优先尝试 465（隐式 TLS），失败后回退到 587（STARTTLS）。Postfix 的双端口部署是最佳实践。

对于服务端引擎来说，隐式 TLS 的实现更简单——没有 STARTTLS 命令的解析阶段，TLS 状态机与 TCP 连接状态直接绑定。这减少了协议实现中因状态转换错误导致的安全漏洞。

## 参考文献

1. IETF RFC 6409 (2011) — Message Submission for Mail, R. Gellens, J. Klensin
2. IETF RFC 8314 (2018) — Cleartext Considered Obsolete: Use of TLS for Email Submission and Access, P. Hoffman, C. Newman
3. IETF RFC 4954 (2007) — SMTP Service Extension for Authentication, R. Siemborski, A. Melnikov
4. IETF RFC 5321 (2008) — Simple Mail Transfer Protocol, J. Klensin
5. IETF RFC 8996 (2021) — Deprecating TLS 1.0 and TLS 1.1
6. Postfix Documentation — SASL\_README, <https://www.postfix.org/SASL_README.html>
7. Postfix Documentation — master(5), <https://www.postfix.org/master.5.html>

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/smtp-submission-protocol.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
