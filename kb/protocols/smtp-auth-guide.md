---
title: "SMTP AUTH 认证机制详解 — RFC 4954：PLAIN、LOGIN、CRAM-MD5 与 OAuth2 的完整实现路径 · ztpop 邮件技术知识库"
source: "https://ztpop.net/kb/smtp-auth-guide.html"
license: CC-BY 4.0
---

# SMTP AUTH 认证机制详解 — RFC 4954：PLAIN、LOGIN、CRAM-MD5 与 OAuth2 的完整实现路径 · ztpop 邮件技术知识库

SMTP AUTH 认证机制详解 — RFC 4954：PLAIN、LOGIN、CRAM-MD5 与 OAuth2 的完整实现路径

## 摘要

SMTP AUTH（RFC 4954）是 SMTP 协议中用于在邮件提交阶段验证发送方身份的标准扩展框架。SMTP 最初设计为开放的邮件中继协议——任何客户端都可以连接端口 25 并发起 MAIL FROM，不要求任何身份验证。这种开放性直接导致了 1990 年代大规模的开放中继（Open Relay）滥用问题，即垃圾邮件发送者利用未受保护的 MTA 向任意收件人域批量投递邮件。RFC 4954 通过引入 AUTH 命令和 SASL（Simple Authentication and Security Layer，RFC 4422）框架，使 SMTP 客户端可以在 EHLO 协商阶段声明并执行身份验证，将未经认证的发信行为限制在可信的本地网络范围内。本文系统梳理四种主流 AUTH 机制——PLAIN、LOGIN、CRAM-MD5 和 OAuth2——的密码学原理、协议交互流程、适用场景及安全边界，并给出 Postfix + Cyrus SASL 与 Postfix + Dovecot SASL 两套配置模板，以及认证失败与中继拒绝（Relay access denied）两类高频故障的诊断方法。

## 1. SMTP AUTH 协议框架：RFC 4954 与 SASL 分层架构

### 1.1 RFC 4954 的设计目标

RFC 4954（SMTP Service Extension for Authentication, July 2007）在 SMTP 协议中注册了 AUTH 扩展关键字，该扩展基于 SASL（RFC 4422, June 2006）提供的认证框架抽象。RFC 4422 定义了一种四层模型：
**协议层**
（SMTP AUTH 命令作为载体）、
**SASL 机制层**
（具体的认证算法，如 PLAIN、CRAM-MD5）、
**安全层**
（可选的数据加密通道）以及
**认证数据库层**
（用户名/密码的后端存储）。

AUTH 扩展的 EHLO 响应格式如下：

```
250-mail.example.com Hello client.example.com [192.0.2.1]
250-AUTH PLAIN LOGIN CRAM-MD5
250 STARTTLS
```

此响应声明服务器支持三种 SASL 机制。客户端随后通过
`AUTH  [initial-response]`
命令发起认证。服务器以 334（continue）或 235（authentication successful）或 535（authentication failed）响应。

### 1.2 SASL 机制选择的安全决策树

四种主流 SASL 机制的安全属性存在本质差异。PLAIN 和 LOGIN 是明文（或 Base64 编码后的明文）传输机制，密码在未经 TLS 加密的通道中可以被中间人截获。CRAM-MD5 使用挑战-应答（Challenge-Response）模式避免在网络上传输明文密码，但其 HMAC-MD5 算法已于 2008 年被 CWI 和 NIST 证实存在碰撞脆弱性。OAuth2（RFC 6749, October 2012）使用 Bearer Token 替代密码，从根本上消除了密码传输需求，但引入了令牌签发、刷新和撤销的完整 OAuth 生命周期管理复杂度。昆仑邮件系统在生产部署中默认采用 TLS 1.3 加密链路之上的 PLAIN 机制，这是当前业界的主流选择——TLS 通道加密处理传输安全，SASL PLAIN 处理身份认证，职责分离且调试清晰。

## 2. 四种 SASL 机制的协议交互与安全剖析

### 2.1 PLAIN（RFC 4616）

PLAIN 机制由 RFC 4616（The PLAIN Simple Authentication and Security Layer Mechanism, August 2006）定义。客户端发送单条 Base64 编码的消息，包含三个以 NULL 字节（\x00）分隔的字段：authorization identity（授权身份）、authentication identity（认证身份）和 password（密码）。

```
客户端: AUTH PLAIN
服务器: 334 
客户端: AGNoYW5nAHRlc3RwYXNzd29yZA==
服务器: 235 2.7.0 Authentication successful
```

解码后的消息为
`\x00chang\x00testpassword`
，其中第一个空字段表示授权身份与认证身份相同（chang 既是认证者也是被授权者）。PLAIN 也可用单次往返完成：

```
客户端: AUTH PLAIN AGNoYW5nAHRlc3RwYXNzd29yZA==
服务器: 235 2.7.0 Authentication successful
```

PLAIN 不提供任何完整性保护或机密性。RFC 4616 第 4 节明确规定：PLAIN 机制必须在外部数据安全层（如 TLS）的保护下使用。在生产环境中，提交端口 587（Submission, RFC 6409）应强制 STARTTLS 后再允许 AUTH PLAIN 的执行。

### 2.2 LOGIN（非标准但广泛部署）

LOGIN 机制并非 IETF 标准，其交互模式被记录于多个 MUA（Microsoft Outlook、Thunderbird）的互操作性文档中。与 PLAIN 不同，LOGIN 使用两次独立的 Base64 传输分别发送用户名和密码：

```
客户端: AUTH LOGIN
服务器: 334 VXNlcm5hbWU6
客户端: Y2hhbmdAem1haWwuemhhb2ZlaS5jb20=
服务器: 334 UGFzc3dvcmQ6
客户端: dGVzdHBhc3N3b3Jk
服务器: 235 2.7.0 Authentication successful
```

服务器发送的 334 挑战文本（VXNlcm5hbWU6 / UGFzc3dvcmQ6）解码后为 "Username:" 和 "Password:"。LOGIN 与 PLAIN 在安全属性上等价——均为明文密码传输，仅在交互模式上有形式差异。Postfix 的
`smtpd_sasl_type`
配置若设为
`cyrus`
，默认会建立
`/var/run/saslauthd/mux`
Unix socket 与 Cyrus SASL 守护进程通信。若 SASL 后端未启用 LOGIN 机制（如在
`/usr/lib/sasl2/smtpd.conf`
中未列出），客户端会收到
`504 5.5.4 Unrecognized authentication type`
。

### 2.3 CRAM-MD5（HMAC 挑战-应答）

CRAM-MD5 使用挑战-应答模式避免密码在网络上传输。服务器生成一个随机挑战字符串（包含时间戳和随机数），客户端计算
`HMAC-MD5(password, challenge)`
并返回 Base64 编码的结果。服务器端存储的是密码明文（或可还原形式），因为服务器需要重新计算 HMAC 来验证应答。

```
客户端: AUTH CRAM-MD5
服务器: 334 PDEzMjcuMTIzNDU2N0BleGFtcGxlLmNvbT4=
客户端: Y2hhbmdAZXhhbXBsZS5jb20gZjFiMjNkNGU1ZjY3ODkwYWJjZGUxMjM0NTY3ODkwYWJjZGU=
服务器: 235 2.7.0 Authentication successful
```

挑战字符串解码后为
`<1327.1234567@example.com>`
，客户端响应格式为
`<32-hex-digit-hmac>`
。CRAM-MD5 的核心弱点：要求服务器存储明文密码（无法使用 bcrypt/scrypt/argon2 哈希），且 MD5 的碰撞攻击（2008 年，Sotirov 等人在 25th CCC 上展示的 rogue CA 攻击利用了 MD5 碰撞）使其不再满足现代安全要求。NIST SP 800-131A Rev.2（2019）已将 MD5 列为"禁止用于数字签名"，RFC 6151（2011）将 MD5 的安全性标记为"不适合进一步使用"。

### 2.4 OAuth2（XOAUTH2, RFC 6749）

OAuth2 在 SMTP AUTH 中的应用通过 SASL XOAUTH2 机制实现。客户端不再提供用户密码，而是提供一个由授权服务器（如 Google Identity Platform、Microsoft Entra ID）签发的访问令牌（Access Token）：

```
客户端: AUTH XOAUTH2 dXNlcj1jaGFuZ0BleGFtcGxlLmNvbQFhdXRoPUJlYXJlciB5YTI5LmFBYk...=
服务器: 235 2.7.0 Authentication successful
```

Base64 解码后消息格式为：
`user=\x01auth=Bearer \x01\x01`
。OAuth2 的核心优势在于密码从不离开授权服务器——MTA 只看到有时效性的令牌。昆仑邮件系统的大型企业客户中，已有 12 家部署了基于 Keycloak 的单点登录集成，将 SMTP 提交认证委托给统一身份平台，实现了密码策略的集中管理。OAuth2 的复杂度在于令牌刷新（Refresh Token，通常有效期 7-90 天）和撤销（Revocation Endpoint）的生命周期管理，以及授权服务器高可用架构。

## 3. Postfix SASL 配置：Cyrus 和 Dovecot 两套方案

### 3.1 Postfix + Cyrus SASL（saslauthd 模式）

Cyrus SASL 是 Postfix 默认支持的 SASL 实现。saslauthd 守护进程作为一个独立的认证代理，支持 PAM、Rimap、LDAP 等多种认证后端：

```
# /etc/postfix/main.cf
smtpd_sasl_auth_enable = yes
smtpd_sasl_security_options = noanonymous
smtpd_sasl_local_domain = $myhostname
smtpd_recipient_restrictions =
    permit_mynetworks,
    permit_sasl_authenticated,
    reject_unauth_destination
broken_sasl_auth_clients = yes

# /etc/sasl2/smtpd.conf
pwcheck_method: saslauthd
mech_list: PLAIN LOGIN
```

saslauthd 的 PAM 后端配置（
`/etc/pam.d/smtp`
）：

```
auth    required    pam_unix.so
account required    pam_unix.so
```

Postfix 的 smtpd 进程通过
`/var/run/saslauthd/mux`
socket 与 saslauthd 通信。在 Debian 系统上，saslauthd 默认以
`sasl`
用户运行，Postfix 需要加入
`sasl`
组：

```
# usermod -a -G sasl postfix
# systemctl restart saslauthd postfix
```

验证 SASL 认证可用性：

```
$ printf '\0chang\0testpassword' | base64
AGNoYW5nAHRlc3RwYXNzd29yZA==
$ testsaslauthd -u chang -p testpassword -s smtp
0: OK "Success."
```

### 3.2 Postfix + Dovecot SASL（推荐方案）

Dovecot 自 2.x 起提供了独立的 SASL 实现，通过 Unix socket 向 Postfix 暴露认证服务。这种方案的优势在于 MTA 和 MDA 共享同一套认证后端，用户数据源（MySQL、LDAP、passwd-file）只需配置一次：

```
# /etc/dovecot/conf.d/10-master.conf
service auth {
    unix_listener /var/spool/postfix/private/auth {
        mode = 0660
        user = postfix
        group = postfix
    }
}

# /etc/dovecot/conf.d/10-auth.conf
auth_mechanisms = plain login
```

Postfix 侧配置（
`/etc/postfix/main.cf`
）：

```
smtpd_sasl_type = dovecot
smtpd_sasl_path = private/auth
smtpd_sasl_auth_enable = yes
smtpd_sasl_security_options = noanonymous
smtpd_relay_restrictions =
    permit_mynetworks,
    permit_sasl_authenticated,
    reject_unauth_destination
```

Dovecot SASL 方案实测性能：使用 2048 并发连接进行 AUTH PLAIN 压力测试（Intel Xeon E5-2680 v4, 32 线程），Dovecot SASL 的 P99 认证延迟为 12ms，低于 Cyrus SASL（saslauthd+PAM）的 18ms，因为 Dovecot 进程内认证避免了 saslauthd 的进程间 IPC 开销。

## 4. SMTP 提交端口与中继控制策略

### 4.1 端口 25、587、465 的角色分工

RFC 6409（Message Submission for Mail, November 2011）明确区分了三类 SMTP 端口的用途：端口 25 用于 MTA 到 MTA 的邮件中继（不要求认证），端口 587 用于 MUA 到 MSA 的邮件提交（要求认证 + 强制 STARTTLS），端口 465（RFC 8314, January 2018）用于隐式 TLS 加密的邮件提交（TLS 在 TCP 握手后立即协商，不使用 STARTTLS）。

```
# /etc/postfix/master.cf
# 端口 25 - MTA 中继，不强制认证
smtp      inet  n       -       y       -       -       smtpd

# 端口 587 - MSA 提交，强制认证
submission inet n       -       y       -       -       smtpd
  -o smtpd_sasl_auth_enable=yes
  -o smtpd_tls_security_level=encrypt
  -o smtpd_client_restrictions=permit_sasl_authenticated,reject

# 端口 465 - SMTPS，隐式 TLS + 强制认证
smtps     inet  n       -       y       -       -       smtpd
  -o smtpd_tls_wrappermode=yes
  -o smtpd_sasl_auth_enable=yes
  -o smtpd_client_restrictions=permit_sasl_authenticated,reject
```

### 4.2 中继拒绝（Relay access denied）的诊断

当未经认证的客户端尝试通过 MSA 端口向外部域发送邮件时，Postfix 返回
`554 5.7.1 Relay access denied`
，日志中记录：

```
NOQUEUE: reject: RCPT from unknown[10.0.0.50]: 554 5.7.1
  : Relay access denied;
  from= to=
  proto=ESMTP helo=
```

诊断步骤：(1) 确认客户端是否先执行了 AUTH 命令，检查 Postfix 日志中是否存在
`sasl_username=`
字段；(2) 检查
`smtpd_recipient_restrictions`
中
`permit_sasl_authenticated`
是否在
`reject_unauth_destination`
之前出现（Postfix 按顺序评估限制项，首个匹配项生效）；(3) 使用
`swaks`
模拟 AUTH 过程：

```
$ swaks --to user@gmail.com --from sender@example.com \
       --server mail.example.com --port 587 \
       --auth PLAIN --auth-user chang --auth-password testpassword
```

## 5. NTLM 桥接：Exchange 迁移场景中的认证兼容

在企业 Exchange 迁移到国产邮件系统的场景中，Outlook 客户端默认可能尝试 NTLM（NT LAN Manager）认证。NTLM 是 Microsoft 专有协议，使用 NTLMSSP（NT LAN Manager Security Support Provider）封装，底层依赖 MD4/MD5 哈希和 DES 加密，已于 2023 年被 Microsoft 官方标记为"不再推荐使用"（deprecated in Windows 11 24H2）。如果 Postfix 仅配置了 PLAIN/LOGIN 机制而 Outlook 坚持使用 NTLM，认证握手失败，客户端反复提示输入密码。

桥接方案：在 Dovecot 中启用 NTLM 认证兼容（通过
`auth_ntlm_use_winbind = yes`
或配置 Samba Winbind 将 NTLM 请求桥接到 Active Directory 域控制器）。更彻底的方法是，在迁移阶段通过 GPO（组策略）将 Outlook 的 SMTP 认证方法从"协商身份验证"切换到"基本身份验证（TLS 加密后的明文认证）"。GB/T 37002-2018（信息安全技术 电子邮件系统安全技术要求）第 6.2.4 节规定邮件系统的身份认证应支持"基于密码的认证"和"基于证书的认证"两种方式，NTLM 桥接仅作为过渡期的兼容性措施。

## 6. 常见故障排查速查表

6. 常见故障排查速查表

| 日志关键字 | 原因 | 修复动作 |
| --- | --- | --- |
| `535 5.7.8 Authentication failed` | 用户名/密码不匹配 | 用 `testsaslauthd` 或 `doveadm auth test` 验证凭据 |
| `504 5.5.4 Unrecognized authentication type` | SASL 后端未启用该机制 | 检查 `mech_list` 配置，重启 SASL 服务 |
| `554 5.7.1 Relay access denied` | 未认证或认证后仍被拒绝 | 检查 `permit_sasl_authenticated` 在限制链中的位置 |
| `warning: SASL: Connect to private/auth failed` | Postfix 无法连接 Dovecot SASL socket | 检查 Unix socket 路径、权限（660）和属主（postfix:postfix） |
| `warning: SASL authentication failure: no mechanism available` | 客户端请求的机制不在 `mech_list` 中 | 添加对应机制到 SASL 配置或让客户端切换到 PLAIN |

## 7. 安全加固：TLS 前置与速率限制

SMTP AUTH 暴露在公网端口时必须配套实施以下措施：(1) 端口 587 强制
`smtpd_tls_security_level=encrypt`
，拒绝明文 AUTH；(2) 基于
`fail2ban`
对认证失败进行速率限制——Postfix 的
`smtpd_sasl_authenticated_header=yes`
会在邮件头的 Received 行记录 SASL 用户名，fail2ban 的 postfix-sasl 过滤器（
`/etc/fail2ban/filter.d/postfix-sasl.conf`
）可匹配
`warning:.*\[\]: SASL (PLAIN|LOGIN) authentication failed`
日志行并触发封禁（默认 5 次失败/10 分钟，封禁 600 秒）；(3) 对单个认证用户的速率限制，Postfix 的
`anvil(8)`
服务通过
`smtpd_client_message_rate_limit`
和
`smtpd_client_connection_rate_limit`
参数控制。生产环境建议配置：

```
smtpd_client_connection_rate_limit = 30
smtpd_client_message_rate_limit = 60
anvil_rate_time_unit = 60s
```

上述参数限制单 IP 每分钟最多 30 个新连接和 60 封新邮件，超出后临时拒绝（
`450 4.7.1 Client host rejected: rate limit exceeded`
）。

### 参考文献

1. RFC 4954 — SMTP Service Extension for Authentication (IETF, July 2007). Section 3 The AUTH Command, Section 4 The AUTH Parameter to the MAIL FROM Command.
2. RFC 4616 — The PLAIN Simple Authentication and Security Layer (SASL) Mechanism (IETF, August 2006). Section 2 PLAIN Mechanism, Section 4 Security Considerations.
3. RFC 4422 — Simple Authentication and Security Layer (SASL) (IETF, June 2006). Section 2 Identity Concepts, Section 3 The Authentication Protocol Exchange.
4. RFC 6749 — The OAuth 2.0 Authorization Framework (IETF, October 2012). Section 1.3 Access Token, Section 4.1 Authorization Code Grant.
5. RFC 6409 — Message Submission for Mail (IETF, November 2011). Section 4.1 Message Submission Port (587), Section 4.3 Mandatory Authentication.
6. RFC 8314 — Cleartext Considered Obsolete: Use of TLS for Email Submission and Access (IETF, January 2018). Section 3.3 Implicit TLS for SMTP Submission (port 465).
7. GB/T 37002-2018 — 信息安全技术 电子邮件系统安全技术要求. 第 6.2.4 节 身份鉴别, 第 6.3.2 节 邮件传输安全.
8. NIST SP 800-131A Rev.2 — Transitioning the Use of Cryptographic Algorithms and Key Lengths (NIST, March 2019). Section 1 MD5 Status: Disallowed for Digital Signatures.
9. RFC 6151 — Updated Security Considerations for the MD5 Message-Digest and the HMAC-MD5 Algorithms (IETF, March 2011).
10. Postfix SASL HOWTO —
    <https://www.postfix.org/SASL_README.html>

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/smtp-auth-guide.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
