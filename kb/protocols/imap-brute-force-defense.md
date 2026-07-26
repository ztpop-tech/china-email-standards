---
title: "IMAP 暴力破解防御实战指南：fail2ban 规则配置、速率限制与多因子认证"
source: "https://ztpop.net/kb/imap-brute-force-defense.html"
license: CC-BY 4.0
---

# IMAP 暴力破解防御实战指南：fail2ban 规则配置、速率限制与多因子认证

#### 📑 目录

1. [攻击面分析：邮件系统认证入口](#s1)
2. [Dovecot 速率限制与 fail2ban 集成](#s2)
3. [Postfix SMTP AUTH 攻击面与防御](#s3)
4. [smtpd\_delay\_reject 与 smtpd\_client\_restrictions 联动](#s4)
5. [Postfix 缺少认证日志时的替代检测方案](#s5)
6. [smtpd\_client\_restrictions 深度配置与 postscreen 联动](#s6)
7. [Honeypot 蜜罐诱捕策略](#s7)
8. [纵深防御体系与自动化运维](#s8)

## 攻击面分析：邮件系统认证入口

邮件系统的 IMAP/IMAPS、POP3S、SMTP Submission/SMTPS、Webmail 登录页面，是暴力破解攻击的主要目标。攻击者使用 `hydra`、`medusa`、`nmap smtp-brute` 等工具，对常见用户名和弱口令进行批量尝试。一次完整的防御方案应覆盖上述所有入口。

表1 邮件系统暴力破解攻击面总览

| 端口/服务 | 端口号 | 加密方式 | 认证机制 | 风险等级 |
| --- | --- | --- | --- | --- |
| SMTP Submission | 587 | STARTTLS | SASL PLAIN/LOGIN | 高 |
| SMTPS | 465 | Implicit TLS | SASL PLAIN/LOGIN | 高 |
| IMAPS | 993 | Implicit TLS | Dovecot 密码认证 | 高 |
| POP3S | 995 | Implicit TLS | Dovecot 密码认证 | 高 |
| Webmail 登录 | 443 | HTTPS | 表单认证 | 极高（需额外 WAF 防护） |

应对暴力破解，需要采用**纵深防御**（Defense in Depth）策略，从网络层、传输层、应用层和审计层构建多层防线：

1. **网络层：**iptables/nftables 黑名单 + fail2ban + knockd
2. **传输层：**smtpd\_delay\_reject + smtpd\_client\_restrictions + Dovecot auth\_failure\_delay
3. **应用层：**密码策略 + 多因子认证 + Honeypot 蜜罐
4. **审计层：**auditd + pam\_unix 日志 + 异常检测

## Dovecot 速率限制与 fail2ban 集成

### 2.1 Dovecot 内置速率限制

Dovecot 从 2.2 版本开始内置 `auth_failure_delay` 参数，2.3 版本引入更完善的 auth\_penalty 机制，可在应用层直接减缓暴力破解速率：

```
# /etc/dovecot/conf.d/10-auth.conf

# 每个认证失败后等待 2 秒再允许下次尝试
auth_failure_delay = 2 secs

# Dovecot 2.3+ 启用 auth_penalty 插件
# 对同一 IP 的失败次数指数级增加延迟
# delay = auth_failure_delay * min(log2(failure_count), max_multiplier)
# max_multiplier 默认 16，建议设为 32

# 确保 SQL 认证查询正确返回
auth_verbose = yes
auth_verbose_passwords = no    # 避免密码明文记录
auth_debug_passwords = no      # 生产环境建议关闭

# 账号锁定机制（可选）
# /etc/dovecot/conf.d/auth-sql.conf.ext
# password_query 中检查 active 和 locked_until 字段
password_query = SELECT username AS user, password AS password,   'maildir:/var/mail/%d/%n' AS userdb_mail   FROM mailbox   WHERE username = '%u' AND active = '1' AND locked_until IS NULL

# 若 locked_until > NOW() 则认证失败，实现账号临时锁定
```

### 2.2 Dovecot + fail2ban 配置

fail2ban 监控 Dovecot 认证日志，发现多次失败后通过 iptables/nftables 封禁 IP。**注意：这是封禁动作最直接的检测路径。**

```
# /etc/fail2ban/filter.d/dovecot-auth.conf
# 过滤 Dovecot 认证失败日志
[Definition]
failregex = ^%(__prefix_line)s(?:pop3|imap)-login: (?:Info|Debug):              (?:Aborted login|Authentication failed)              .*rip=(?P\S+).*$

# 匹配 Dovecot 断开连接消息
            ^%(__prefix_line)s(?:pop3|imap)-login:              (?:Info )?(?:Disconnected):.*rip=(?P\S+),.*failed$

ignoreregex = 

# /etc/fail2ban/jail.d/dovecot.conf
[dovecot]
enabled  = true
port     = imap,imaps,pop3,pop3s
filter   = dovecot-auth
logpath  = /var/log/dovecot.log
          /var/log/mail.log
maxretry = 5
findtime = 600   # 10 分钟内
bantime  = 86400 # 1 天
banaction = nftables-multiport  # 或 iptables-multiport

# 动作执行优化
action_ = %(action_)s
action_dovecot_block = %(banaction)s[name=%(__name__)s, port="%(port)s", protocol="tcp"]
action_mw = %(action_mw)s[dovecot_alert]
           [mail action=%(action_)s[name=%(__name__)s, dest="%(destemail)s", logpath="%(logpath)s", chain="%(chain)s"]]

# 正则验证（调试用）
fail2ban-regex /var/log/dovecot.log /etc/fail2ban/filter.d/dovecot-auth.conf   --print-all-matched
```

### 2.3 Dovecot 2.3+ 高级 auth\_penalty 策略

Dovecot 2.3 引入了 auth\_penalty 插件，可以在应用层进行智能延迟，与 fail2ban 的网络层封禁形成互补：

```
# /etc/dovecot/conf.d/10-auth.conf
# 启用 auth policy 服务器策略联动
auth_policy_server_url = http://localhost:8080/policy
auth_policy_server_api_header = X-Api-Key: your-api-key
auth_policy_hash_nonce = some-random-string
auth_policy_hash_user = %u
auth_policy_hash_domain = %d
auth_policy_hash_remote = %r

# 启用 auth_penalty 服务
# 在 10-master.conf 中配置 auth-penalty 服务
service auth-penalty {
  unix_listener auth-penalty {
    mode = 0600
    user = $default_internal_user
  }
  # 自定义进程数
  # penalty 数据持久化
  # 内存 + SQLite 持久化存储}
```

## Postfix SMTP AUTH 攻击面与防御

### 3.1 Postfix 认证失败日志分析

Postfix 通过 Dovecot SASL 代理实现 SMTP AUTH 认证，认证失败会同时在 Postfix 和 Dovecot 日志中留下记录：

```
# Postfix + Dovecot SASL 认证失败日志示例
Jul 20 14:23:45 mx postfix/smtpd[12345]: warning: unknown[203.0.113.5]:   SASL LOGIN authentication failed: authentication failure

Jul 20 14:23:46 mx postfix/smtpd[12345]: warning: unknown[203.0.113.5]:   SASL PLAIN authentication failed: generic failure

# 对应的 Dovecot SASL 日志
Jul 20 14:23:45 mx dovecot: auth-worker(12346):   pam(user@example.com,203.0.113.5):   unknown user

Jul 20 14:23:46 mx dovecot: auth-worker(12346):   pam(sales@example.com,203.0.113.5):   password mismatch
```

### 3.2 标准 fail2ban 配置

```
# /etc/fail2ban/filter.d/postfix-auth.conf
[Definition]
failregex = ^%(__prefix_line)swarning: .*\[\]: SASL (?:LOGIN|PLAIN)              authentication failed(?:, .*)?$

ignoreregex = 

# 匹配 Postfix 详细失败原因
            ^%(__prefix_line)swarning: .*\[\]: SASL (?:LOGIN|PLAIN)              authentication failed: authentication failure$

            ^%(__prefix_line)swarning: .*\[\]: SASL (?:LOGIN|PLAIN)              authentication failed: generic failure$

            ^%(__prefix_line)swarning: .*\[\]: SASL (?:LOGIN|PLAIN)              authentication failed: no mechanism available$

# 兼容旧版 Postfix 的日志格式
            ^%(__prefix_line)swarning: .*\[\]: SASL LOGIN authentication failed:              server didn't send SASL mechanisms$

# /etc/fail2ban/jail.d/postfix-auth.conf
[postfix-auth]
enabled  = true
port     = smtp,submission,submissions,smtps
filter   = postfix-auth
logpath  = /var/log/mail.log
maxretry = 5
findtime = 600
bantime  = 86400
# 联动 Dovecot IP 阻断脚本
action_   = %(action_)s
           dovecot-block-ip.sh[name=%(__name__)s, ip="<ip>"]
```

### 3.3 Dovecot IP 阻断联动脚本

```
# 当 fail2ban 检测到 SMTP AUTH 攻击时，同步阻断 Dovecot 端口
cat > /usr/local/bin/dovecot-block-ip.sh << 'SH'
#!/bin/bash
# 用法: dovecot-block-ip.sh <ip> <action>
# 由 fail2ban action_ 调用

IP="$2"
ACTION="$3"  # ban / unban
BLOCKLIST="/etc/dovecot/blocked-ips.conf"

case "$ACTION" in
  ban)
    echo "$IP" >> "$BLOCKLIST"
    # 发送 SIGHUP 重启 Dovecot 以生效
    # 或通过 Dovecot auth policy API 实时同步
    sort -u -o "$BLOCKLIST" "$BLOCKLIST"
    logger -t dovet-block "IP blocked: $IP"
    ;;
  unban)
    sed -i "/^${IP}$/d" "$BLOCKLIST"
    logger -t dovet-block "IP unblocked: $IP"
    ;;
esac
SH
chmod 755 /usr/local/bin/dovecot-block-ip.sh

# Dovecot 加载 blocked-ips 配置
# 在 auth policy 配置中引用
# auth_policy_server_url = http://127.0.0.1:8080/policy
# 或使用 passdb checkpassword 脚本实现
```

## smtpd\_delay\_reject 与 smtpd\_client\_restrictions 联动

### 4.1 smtpd\_delay\_reject 机制

Postfix 的 `smtpd_delay_reject` 参数控制是否在 EHLO/HELO 阶段立即拒绝。默认值 `yes` 表示 Postfix 会将所有拒绝推迟到 RCPT TO 阶段才返回 `553` 或 `554` 错误码。这意味着**认证日志可能不会为 EHLO 阶段的失败生成 SASL 记录**：

表2 smtpd\_delay\_reject 参数对比

| 参数值 | 行为 | 对认证日志的影响 |
| --- | --- | --- |
| `yes`（默认值） | HELO/EHLO 阶段的检查（如 `reject_unknown_client_hostname`）不会立即拒绝，推迟到 RCPT TO 阶段才返回错误 | 认证失败的 EHLO 连接不会产生 SASL 失败日志，fail2ban 可能漏检 |
| `no` | 各阶段的检查立即执行，HELO 阶段的 `reject_unknown_client_hostname` 会立即返回 `504` 错误 | 所有失败都会生成日志，fail2ban 可准确检测 EHLO 阶段的攻击 |

```
# 标准配置：delay_reject=yes 时注意日志覆盖范围
# /etc/postfix/main.cf

# 参数默认值
smtpd_delay_reject = yes

# smtpd_client_restrictions 在 EHLO/HELO 阶段执行
# 但 delay_reject 为 yes 时失败推迟
smtpd_client_restrictions =
    # 优先检查 fail2ban 维护的客户端黑名单
    # 可使用 postscreen 替代
    check_client_access cidr:/etc/postfix/client_access.cidr,
    permit_mynetworks,
    reject_unknown_client_hostname,
    # 启用 DNSBL 检查（会延迟到 EHLO 之后）
    # reject_rbl_client zen.spamhaus.org,
    permit

# smtpd_recipient_restrictions 在 RCPT TO 阶段执行
smtpd_recipient_restrictions =
    permit_mynetworks,
    reject_unauth_destination,
    # 允许 SASL 已认证用户
    permit_sasl_authenticated,
    reject_unauth_destination,
    reject

# smtpd_relay_restrictions 自 Postfix 2.10+ 引入
# 优先于 recipient_restrictions
smtpd_relay_restrictions =
    permit_mynetworks,
    permit_sasl_authenticated,
    reject_unauth_destination

# delay_reject 为 yes 时的检查顺序：
# 1. smtpd_client_restrictions (EHLO 阶段检查，但错误推迟)
# 2. smtpd_helo_restrictions (HELO 检查)
# 3. smtpd_sender_restrictions (MAIL FROM)
# 4. smtpd_recipient_restrictions (RCPT TO 实际拒绝)
```

### 4.2 smtpd\_delay\_reject = no 的应用场景

将 `smtpd_delay_reject` 设为 `no` 可以改变这一行为，让你的认证日志更加完整：

**设置 delay\_reject=no 的优势：**

* 攻击者在 SMTP 会话的 EHLO 阶段即暴露真实来源，便于早期阻断
* 配合 `reject_unknown_client` 等检查，可在 EHLO 阶段直接拒绝可疑客户端
* 所有认证失败都会生成标准格式的日志条目，fail2ban 可准确匹配
* 配合 `reject_rbl_client` 等 DNSBL 检查，在 EHLO 阶段拒绝已知恶意 IP 来源

**需要注意的代价：**

* **日志可能大量增加：**mail.log 中每一行 EHLO 拒绝都会产生日志条目，fail2ban 需要更高的处理能力
* 合法客户端的 RCPT TO 阶段异常减少，可能需要调整监控指标
* Postfix 的 smtpd 进程可能因 EHLO 阶段拒绝频率过高而产生额外负载

```
# 在 submission/smtps 端口上启用 delay_reject=no
# /etc/postfix/master.cf
submission inet n - n - - smtpd
  -o syslog_name=postfix/submission
  -o smtpd_delay_reject=no          # 立即拒绝策略
  -o smtpd_client_restrictions=    permit_sasl_authenticated,    reject

smtps inet n - n - - smtpd
  -o syslog_name=postfix/smtps
  -o smtpd_delay_reject=no
  -o smtpd_tls_wrappermode=yes
  -o smtpd_client_restrictions=    permit_sasl_authenticated,    reject

# 端口 25 保留 MTA-MTA 通信，delay_reject=yes
# 避免因过早拒绝影响正常邮件投递
```

## Postfix 缺少认证日志时的替代检测方案

### 5.1 问题背景

某些部署场景下，Postfix 本身可能不直接记录 SASL 认证失败的详细信息，`/var/log/mail.log` 中只包含通用警告而无具体用户名。此时需要通过替代方案获取认证失败证据：

* 确认是否启用了 SASL 认证日志的详细级别
* 检查 `smtpd_sasl_authenticated_header = yes` 是否启用
* 查看 `smtpd_pw_server_security = none` 是否需要调整
* 确认 Dovecot 的 auth\_verbose 日志是否已正确输出到 syslog

如果 fail2ban 无法从 Postfix 日志中提取认证失败特征，可以参考以下三种替代方案：

### 5.2 方案 A：pam\_unix 日志

如果 Dovecot SASL 使用 PAM 认证方式，则 `pam_unix` 模块会将每次认证结果写入 `/var/log/auth.log`。这可以作为 Postfix 日志不完整的补充信息来源：

```
# pam_unix 认证失败日志示例
# auth.log:
# Jul 20 14:23:45 mx postfix/smtpd: pam_unix(smtp:auth): #   authentication failure; logname= uid=0 euid=0 tty= #   ruser= rhost=203.0.113.5 user=user@example.com

# fail2ban 针对 pam_unix 的过滤规则
cat > /etc/fail2ban/filter.d/pam-generic.conf << 'CONF'
[Definition]
failregex = ^%(__prefix_line)%(__pam_auth)s[^:]*authentication failure;.*rhost=<HOST>\s

ignoreregex = 
CONF

# 对应的 PAM jail 配置
cat > /etc/fail2ban/jail.d/pam-auth.conf << 'CONF'
[pam-auth]
enabled  = true
filter   = pam-generic
logpath  = /var/log/auth.log
maxretry = 5
findtime = 600
bantime  = 86400
port     = smtp,submission,submissions,smtps,imap,imaps,pop3,pop3s
CONF

# 确认 Postfix 使用 PAM 方式
# /etc/dovecot/conf.d/auth-system.conf.ext
passdb {
  driver = pam
  args = session=yes dovecot
}
# 或通过 saslauthd 使用 PAM
# /etc/default/saslauthd
START=yes
MECHANISMS="pam"
```

### 5.3 方案 B：auditd 审计日志

**auditd** 是 Linux 内核级审计框架，可以捕获 `pam_unix` 对 `pam_sm_authenticate` 的每次调用。即使 Postfix 自身不记录用户名，audit 子系统也能记录完整认证上下文：

```
# 安装 auditd
apt install auditd audispd-plugins

# 配置 audit 规则，监控 pam 认证过程
cat >> /etc/audit/rules.d/50-mail-auth.rules << 'RULES'
# 监控 pam_unix.so 的 pam_sm_authenticate 调用
-w /lib/x86_64-linux-gnu/security/pam_unix.so -p x -k mail-auth

# 监控 postfix/smtpd 执行
-w /usr/sbin/smtpd -p x -k smtpd-exec
RULES

# 重新加载规则
auditctl -R /etc/audit/rules.d/50-mail-auth.rules

# 查看认证失败事件
ausearch -k mail-auth -ts today -i | grep -E "success=no|failed"

# fail2ban 针对 auditd 的过滤规则
cat > /etc/fail2ban/filter.d/audit-mail-auth.conf << 'CONF'
[Definition]
failregex = ^type=USER_AUTH.*msg=audit\(.*\):.*\sres=failed.*\sacct="[^"]+"\s.*\shostname=\S+\saddr=<HOST>\s.*exe="/usr/sbin/smtpd"

ignoreregex = 
CONF

# auditd fail2ban jail 配置
cat > /etc/fail2ban/jail.d/audit-mail-auth.conf << 'CONF'
[audit-mail-auth]
enabled  = true
filter   = audit-mail-auth
logpath  = /var/log/audit/audit.log
maxretry = 5
findtime = 600
bantime  = 86400
port     = smtp,submission,submissions,smtps
CONF
```

### 5.4 方案 C：Dovecot 日志兜底

如果其他方案都不可行，Dovecot 日志本身也能提供足够信息——因为 Dovecot 是最终的 SASL 认证执行者，Postfix 只是通过 Unix Socket 委托给 Dovecot：

```
# /etc/dovecot/conf.d/10-master.conf
# 确认 Dovecot 的 auth socket 路径
service auth {
  unix_listener /var/spool/postfix/private/auth {
    mode = 0660
    user = postfix
    group = postfix
  }
  # 启用详细日志
  verbose = yes
}

# /etc/dovecot/conf.d/10-logging.conf
# 启用认证详细日志
auth_verbose = yes
auth_verbose_passwords = no   # 避免密码明文记录
auth_debug = no               # 生产环境不建议开启 debug

# 邮件会话日志配置
mail_log_prefix = "%s(%u): "
plugin {
  mail_log_events = delete undelete expunge copy mailbox_create mailbox_delete
  mail_log_fields = uid box msgid size
}

# 将 Dovecot 日志纳入 fail2ban 监控
# 在 /etc/fail2ban/jail.d/postfix-auth.conf 中
# logpath 添加 /var/log/dovecot.log
# dovecot.log 中同时包含 smtp 和 imap 的认证记录
```

## smtpd\_client\_restrictions 深度配置与 postscreen 联动

### 6.1 全局 IP 访问控制

Postfix 的 `smtpd_client_restrictions` 提供连接阶段的访问控制，可以在 SMTP 会话早期就拒绝已知恶意 IP。配合 postscreen 模块，能够在 10 个数据包之内完成 5 项检测，被称为"零数据包拒绝"架构：

```
# 策略 1：CIDR 白名单/黑名单
# /etc/postfix/client_access.cidr
# 已知攻击来源网段
203.0.113.0/24     REJECT  Known attack source
198.51.100.0/24    REJECT  Known attack source
# fail2ban 动态添加的 IP
# 通过 fail2ban action 追加到文件末尾
# 建议同时使用 iptables/nftables 封禁

# 策略 2：postscreen — Postfix 内置的 SMTP 前置过滤器
# /etc/postfix/main.cf
# 启用 postscreen
postscreen_access_list = permit_mynetworks,
    cidr:/etc/postfix/postscreen_access.cidr
postscreen_blacklist_action = drop

# postscreen 自 Postfix 2.11+ 可用
postscreen_dnsbl_threshold = 2
postscreen_dnsbl_sites =
    zen.spamhaus.org=127.0.0.[2..11]*3
    b.barracudacentral.org=127.0.0.2*2
postscreen_greet_action = enforce

# postscreen 监听端口 25，将 clean 流量转发到 2525
# 确保 SMTP 端口 25 由 postscreen 管理
```

### 6.2 Postfix 内置 postscreen 模块

```
# /etc/postfix/main.cf 中 postscreen 的完整配置
# 端口 25 由 postscreen 监听，端口 2525 由 smtpd 监听
# postscreen 完成"预检"后，干净流量转发到 smtpd

# postscreen 基础配置
postscreen_access_list =
    permit_mynetworks,
    cidr:/etc/postfix/postscreen_access.cidr
postscreen_dnsbl_reply_map = texthash:/etc/postfix/dnsbl_reply
postscreen_cache_map = btree:$data_directory/postscreen_cache
postscreen_dnsbl_action = enforce

# postscreen 的速率限制参数
# 基于 cache_map 的 IP 历史行为评估
postscreen_reject_frequency = 3   # 每 60 秒允许 3 次连接
postscreen_reject_limit = 5        # 每 60 秒拒绝阈值 5 次

# SMTP 端口 2525 作为实际 smtpd 的监听端口
# 端口 25 由 postscreen 预检
2525  inet  n  -  n  -  -  smtpd
  -o smtpd_tls_security_level=may
  -o smtpd_sasl_auth_enable=yes

# postscreen + fail2ban 联动
# postscreen 的拒绝行为会写入日志，fail2ban 可另行检测
```

### 6.3 自适应速率限制脚本

```
# 自适应速率限制脚本
cat > /usr/local/bin/adaptive-rate-limit.sh << 'SH'
#!/bin/bash
# 根据近期失败频率动态调整封禁策略
# 可作为 fail2ban 的后备或补充机制

DATA_FILE="/var/lib/rate-limit/stats.json"
mkdir -p "$(dirname "$DATA_FILE")"

# 统计最近 15 分钟内的失败 IP
cd /tmp
TMP=$(mktemp)

grep "$(date -d '15 minutes ago' '+%Y-%m-%d %H')" /var/log/mail.log |   grep "authentication failed" |   sed 's/.*\[\([0-9.]*\)\].*//' | sort | uniq -c | sort -rn > "$TMP"

# 根据失败次数分级处理
while read count ip; do
  if [ "$count" -gt 50 ]; then
    # 高频攻击：iptables 封禁 7 天
    iptables -A INPUT -s "$ip" -p tcp --dport 25,587,465,993,995 -j DROP
    logger -t rate-limit "HIGH: $ip blocked for 7 days ($count attempts)"
  elif [ "$count" -gt 20 ]; then
    # 中频攻击：加入 postscreen 黑名单
    echo "$ip	REJECT Excessive authentication failures" >>       /etc/postfix/postscreen_access.cidr
    logger -t rate-limit "MEDIUM: $ip added to postscreen blocklist ($count attempts)"
  elif [ "$count" -gt 5 ]; then
    # 低频尝试：记录到日志，由 fail2ban 常规处理
    logger -t rate-limit "LOW: $ip noted for repeated failures ($count)"
  fi
done < "$TMP"

# 7 天后自动清理 iptables 规则
# 生产环境建议使用 ipset 带超时的集合
SH
chmod 755 /usr/local/bin/adaptive-rate-limit.sh
```

## Honeypot 蜜罐诱捕策略

Honeypot（蜜罐）是一种主动诱捕策略，通过部署一个看似真实但实际受监控的邮件账户，吸引攻击者尝试登录。一旦该账户被尝试登录，即可判定为恶意行为并自动封禁攻击者 IP：

### 7.1 Honeypot 部署方案

```
# 创建蜜罐账户（用于诱捕扫描行为）
useradd -m -s /sbin/nologin honeypot@example.com
passwd honeypot@example.com <<< "$(openssl rand -base64 48)"

# 确认 /var/mail/example.com/honeypot 目录存在
# 确保 Dovecot 可访问该账户的 IMAP/POP3 邮箱

# 使用 passwd-file 方式添加
echo "honeypot@example.com:{SHA512-CRYPT}\$6\$$(openssl rand -base64 16):" >> /etc/dovecot/users

# 配置 fail2ban 蜜罐规则
cat > /etc/fail2ban/filter.d/dovecot-honeypot.conf << 'CONF'
[Definition]
failregex = ^%(__prefix_line)s(?:imap|pop3)-login: (?:Info )?Disconnected:              .*user=<honeypot@example\.com>.*rip=<HOST>.*$

ignoreregex = 
CONF

# 蜜罐 jail 配置（maxretry=1，一次即封禁）
cat > /etc/fail2ban/jail.d/dovecot-honeypot.conf << 'CONF'
[dovecot-honeypot]
enabled  = true
filter   = dovecot-honeypot
logpath  = /var/log/dovecot.log
maxretry = 1
findtime = 31536000  # 1 年有效窗口
bantime  = 864000    # 10 天
port     = imap,imaps,pop3,pop3s
action   = %(action_)s
CONF

# 建议同时创建多个蜜罐用户名
# 常见被尝试的用户名：admin, postmaster, info, support, test, backup, root
for user in admin info support test root; do
  if ! id "${user}@example.com" &>/dev/null; then
    # 检查是否已存在该用户
    echo "建议创建蜜罐: ${user}@example.com"
  fi
done
```

### 7.2 Honeypot 触发告警与自动阻断

```
cat > /usr/local/bin/honeypot-alert.sh << 'SH'
#!/bin/bash
# 蜜罐触发时的告警和自动响应脚本
IP="$1"
USER="$2"

# 1. 发送告警邮件
echo "Honeypot triggered by IP: $IP, attempted user: $USER at $(date)" |   mail -s "[ALERT] 蜜罐触发告警 - $IP" security@example.com

# 2. 在所有邮件端口封禁该 IP
for port in 25 587 465 993 995; do
  iptables -A INPUT -s "$IP" -p tcp --dport $port -j DROP
done

# 3. 写入 Postfix 黑名单
echo "$IP  REJECT Honeypot trigger" >> /etc/postfix/client_access.cidr
postfix reload

# 4. 发送日志到 SIEM
logger -t honeypot -p local0.alert "HONEYPOT_TRIGGER: $IP attempted $USER"
SH
chmod 755 /usr/local/bin/honeypot-alert.sh
```

## 纵深防御体系与自动化运维

### 8.1 防护层次总览

表3 纵深防御层次对比

| 层次 | 技术手段 | 防护方式 | 运营成本 |
| --- | --- | --- | --- |
| 0 网络层 | iptables/nftables + ipset | 已知恶意 IP 黑名单 | 低 |
| 1 连接层 | postscreen | DNSBL 查询、握手延迟检测 | 低 |
| 2 连接控制 | smtpd\_client\_restrictions | CIDR 白名单与动态黑名单 | 低 |
| 3 EHLO检查 | smtpd\_delay\_reject=no (Submission) | EHLO 阶段立即失败日志 | 需调整配置 |
| 4 应用限速 | Dovecot auth\_failure\_delay | 认证失败间隔延迟 | 配置简单 |
| 5 封禁层 | fail2ban（Postfix + Dovecot + auditd） | 自动封禁攻击 IP | 需维护规则 |
| 6 蜜罐诱捕 | Honeypot 账户 | 诱捕并封禁扫描行为 | 需监控 |
| 7 审计检测 | auditd + 异常检测 | 记录所有认证事件 | 需维护 |

### 8.2 健康检查脚本

```
echo "=== 暴力破解防护状态检测 ==="

echo "1. 检测 iptables/nftables 限速规则"
nft list ruleset 2>/dev/null | grep -q "thash" && echo "  OK: nftables hashlimit 已启用" || echo "  WARN: nftables 限速未配置"

echo ""
echo "2. postscreen 状态"
postconf -n 2>/dev/null | grep -q "^postscreen" && echo "  OK: postscreen 已启用" || echo "  WARN: postscreen 未启用"

echo ""
echo "3. fail2ban 状态检查"
for jail in postfix-auth dovecot dovecot-honeypot; do
  systemctl is-active fail2ban &>/dev/null
  if [ $? -eq 0 ]; then
    STATUS=$(fail2ban-client status "$jail" 2>/dev/null | grep -E "Status|Total banned")
    if [ -n "$STATUS" ]; then
      echo "  OK $jail: $STATUS"
    else
      echo "  WARN $jail: jail 未定义或未启用"
    fi
  else
    echo "  ERROR: fail2ban 未运行"
    break
  fi
done

echo ""
echo "4. Dovecot auth_failure_delay"
doveconf -n 2>/dev/null | grep -q "auth_failure_delay" && echo "  OK: auth_failure_delay 已配置" || echo "  WARN: 未配置"

echo ""
echo "5. SMTP 端口 delay_reject 状态"
postconf -M submission 2>/dev/null | grep -q "smtpd_delay_reject=no" && echo "  OK: submission 端口 delay_reject=no" || echo "  WARN: submission 未配置 delay_reject=no"

echo ""
echo "6. 蜜罐账户"
id honeypot@example.com &>/dev/null && echo "  OK: honeypot 账户已存在" || echo "  WARN: 蜜罐账户不存在"

echo ""
echo "7. auditd 规则"
auditctl -l 2>/dev/null | grep -q "mail-auth" && echo "  OK: auditd mail-auth 规则已加载" || echo "  WARN: 未配置 auditd 规则"

echo ""
echo "8. 综合评分"
SCORE=0
[ "$(systemctl is-active fail2ban)" = "active" ] && ((SCORE++))
postconf -n 2>/dev/null | grep -q "^postscreen" && ((SCORE++))
doveconf -n 2>/dev/null | grep -q "auth_failure_delay" && ((SCORE++))
[ -f /etc/postfix/client_access.cidr ] && ((SCORE++))
auditctl -l 2>/dev/null | grep -q "mail-auth" && ((SCORE++))

echo ""
echo "综合评分: $SCORE/5"
echo "评级: $([ "$SCORE" -ge 4 ] && echo '优秀' || echo '需要改进')"
```

### 8.3 每日报表脚本

```
# 生成暴力破解防护日报
cat > /usr/local/bin/brute-force-daily-report.sh << 'SH'
#!/bin/bash
# 汇总每日 fail2ban 封禁的 IP 信息
REPORT="/var/reports/brute-force-$(date +%Y%m%d).txt"
mkdir -p /var/reports

echo "=== 暴力破解防护日报: $(date +%Y-%m-%d) ===" > "$REPORT"
echo "" >> "$REPORT"

# 各 jail 统计
for jail in postfix-auth dovecot dovecot-honeypot pam-auth audit-mail-auth; do
  banned=$(fail2ban-client status "$jail" 2>/dev/null |     grep "Total banned" | awk '{print $4}')
  [ -n "$banned" ] && echo "$jail: 累计 $banned 个 IP 被封禁" >> "$REPORT"
done

echo "" >> "$REPORT"
echo "--- 当前封禁状态 ---" >> "$REPORT"
for jail in postfix-auth dovecot dovecot-honeypot; do
  fail2ban-client status "$jail" 2>/dev/null |     grep "Currently banned" >> "$REPORT"
done

echo "" >> "$REPORT"
echo "--- iptables 封禁规则数 ---" >> "$REPORT"
iptables -L INPUT -n 2>/dev/null | grep "DROP" | wc -l >> "$REPORT"

echo "" >> "$REPORT"
echo "--- 今日 Top 5 攻击源 IP ---" >> "$REPORT"
cat /var/log/mail.log | grep "authentication failed" |   sed 's/.*\[\([0-9.]*\)\].*//' | sort | uniq -c | sort -rn |   head -5 | while read count ip; do
    echo "  $count 次尝试: $ip" >> "$REPORT"
  done

mail -s "[SECURITY] 暴力破解防护日报 $(date +%Y%m%d)"   security@example.com < "$REPORT"
SH
chmod 755 /usr/local/bin/brute-force-daily-report.sh

# crontab 每天早上 9 点执行
echo "0 9 * * * /usr/local/bin/brute-force-daily-report.sh" > /etc/cron.d/brute-force-report
```

### 8.4 集中日志与 SIEM 集成

对于大规模邮件系统，建议将所有认证日志集中到 SIEM 平台（如 Elasticsearch + Kibana），实现全局可视化和自动化响应：

```
# Filebeat 配置示例
# /etc/filebeat/filebeat.yml
filebeat.inputs:
- type: log
  enabled: true
  paths:
    - /var/log/mail.log
    - /var/log/dovecot.log
    - /var/log/auth.log
  fields:
    service: mail-security
  fields_under_root: true

# Elasticsearch Watcher 示例（暴力破解检测）：
# POST /_watcher/watch/mail_brute_force
# {
#   "trigger": { "schedule": { "interval": "5m" } },
#   "input": {
#     "search": {
#       "request": {
#         "indices": ["filebeat-*"],
#         "body": {
#           "query": {
#             "bool": {
#               "filter": [
#                 { "range":  { "@timestamp": { "gte": "now-5m" } } },
#                 { "terms":  { "event.type": ["authentication_failure"] } }
#               ]
#             }
#           },
#           "aggs": {
#             "attacker_ips": {
#               "terms": { "field": "source.ip", "min_doc_count": 5 }
#             }
#           }
#         }
#       }
#     }
#   },
#   "actions": {
#     "webhook": {
#       "webhook": {
#         "host": "alertmanager.example.com",
#         "port": 9093,
#         "path": "/api/v2/alerts",
#         "method": "POST"
#       }
#     }
#   }
# }
```

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/imap-brute-force-defense.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
