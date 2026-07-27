---
title: "🏷 等保 2.0 / 邮件安全"
source: "https://ztpop.net/kb/dengbao2-email-compliance.html"
license: CC-BY 4.0
---

# 🏷 等保 2.0 / 邮件安全

等保 2.0 邮件系统安全测评深度解析 — GB/T 22239-2019 邮件相关控制项与综合防护

  

## 一、等保 2.0 与 1.0 的核心差异

2019 年 12 月 1 日，GB/T 22239-2019《信息安全技术 网络安全等级保护基本要求》正式实施，标志着等级保护制度从 1.0 时代切换到 2.0 时代。名称中"信息系统"变为"网络安全"并非文字游戏——保护对象从狭义的信息系统扩展至云计算平台、大数据平台、物联网、工业控制系统、移动互联系统以及
**通信网络设施**
。

一、等保 2.0 与 1.0 的核心差异

| 维度 | 等保 1.0 (GB/T 22239-2008) | 等保 2.0 (GB/T 22239-2019) |
| --- | --- | --- |
| 保护对象 | 信息系统 | 信息系统 + 通信网络设施 + 数据资源 + 云计算/物联网/工控/移动互联 |
| 标准结构 | 单一通用要求 | **1+5** ：通用要求 + 云计算/移动互联/物联网/工控/大数据扩展 |
| 安全层面 | 物理、网络、主机、应用、数据、管理 | 安全物理环境 / 通信网络 / 区域边界 / 计算环境 / 管理中心 + 管理要求 |
| 入侵防范 | 覆盖面较窄 | 增加"应能检测和报警"的主动防御和已知漏洞修复时效要求 |
| 密码技术 | 提及较少 | 明确要求使用 **密码技术** 保证通信保密性和数据完整性（与 GB/T 39786-2021 联动） |
| 可信验证 | 无 | 新增，基于可信根对引导程序、系统程序进行可信验证 |
| 测评要求 | GB/T 28448-2012 | GB/T 28448-2019，测评方法更细致，引入 **高风险判定指引** |

**🔑 关键变化对邮件系统的影响：**
邮件系统不再只是"应用系统"，在等保 2.0 视角下，它同时涵盖安全计算环境（操作系统与数据库层面的身份鉴别/访问控制/安全审计/入侵防范/数据保护）、安全通信网络（SMTP/IMAP/POP3 传输加密）、安全区域边界（邮件网关与防火墙策略），以及数据层面的备份恢复。

## 二、邮件系统定级：二级还是三级？

依据 GB/T 22240-2020《信息安全技术 网络安全等级保护定级指南》，定级由两个要素决定：等级保护对象受到破坏时所
**侵害的客体**
，以及对客体造成
**侵害的程度**
。

### 2.1 定级判定矩阵

2.1 定级判定矩阵

| 受侵害的客体 | 一般损害 | 严重损害 | 特别严重损害 |
| --- | --- | --- | --- |
| 公民、法人和其他组织的合法权益 | 第一级 | **第二级** | 第二级 |
| 社会秩序、公共利益 | **第二级** | **第三级** | 第四级 |
| 国家安全 | **第三级** | 第四级 | 第五级 |

### 2.2 邮件系统的典型定级场景

**⚠️ 定级建议：**
大多数企业自建邮件系统应定级为
**第二级**
；涉及政务邮件、金融行业内部邮件、医疗病历流转邮件、大型互联网企业核心邮件系统的，建议定级为
**第三级**
。

2.2 邮件系统的典型定级场景

| 场景 | 建议定级 | 理由 |
| --- | --- | --- |
| 中小企业内部办公邮件（< 200 用户） | 第二级 | 受损影响限于企业自身，损害程度一般 |
| 中大型企业/教育机构核心邮件系统 | 第二级 | 服务中断影响较大，但不涉及国家安全 |
| 政务邮件系统（市级以上） | **第三级** | 数据泄露或服务中断危害社会秩序和公共利益 |
| 金融行业内部邮件（含交易指令） | **第三级** | 涉及金融秩序与客户资金安全 |
| 医疗病历流转邮件（含患者隐私数据） | **第三级** | 涉及大量个人敏感信息与公共卫生利益 |
| 大型互联网公司全网邮件系统（> 1 万用户） | **第三级** | 服务中断造成严重社会影响 |

二级和三级在具体控制项上的差异并不总是"有/无"的区别，更多体现在
**强度的加深**
。以身份鉴别为例：二级要求"身份标识唯一性 + 复杂度要求 + 定期更换"；三级额外要求"双因子认证"和"登录失败处理 + 会话超时锁定"。

**💡 定级实操建议：**
先按"就高不就低"原则初步定级，再依据 GB/T 22240-2020 第 6 章进行业务信息安全保护等级和系统服务安全保护等级的交叉判断。定级结果需通过专家评审和主管部门核准，不是运营单位单方面决定。

## 三、安全通用要求逐条解析（安全计算环境）

安全计算环境是 GB/T 22239-2019 中对邮件系统影响最直接的安全类，覆盖操作系统、数据库和邮件应用软件本身。以下按控制点逐条展开，标注了三级要求（
L3
）与二级要求（
L2
）的差异。

### 3.1 身份鉴别（L3-CES1）

3.1 身份鉴别（L3-CES1）

| 序号 | 要求项（三级） | 测评要点 | 邮件系统对应措施 |
| --- | --- | --- | --- |
| a | 应对登录的用户进行身份标识和鉴别，身份标识具有唯一性，身份鉴别信息具有复杂度要求并定期更换 | 核查是否存在空口令/弱口令；核查密码复杂度策略；核查密码有效期 | Dovecot `auth` 模块强制密码策略；OS 层 `/etc/pam.d/system-auth` 配置 `pam_pwquality.so` |
| b | 应具有登录失败处理功能，配置结束会话、限制非法登录次数和连接超时自动退出 | 核查连续登录失败锁定次数和锁定时长；核查会话超时时间 | Fail2ban 对接 Dovecot/Postfix 日志；OS 层 `TMOUT` 环境变量设为 600 秒 |
| c | 当进行远程管理时，应采取必要措施防止鉴别信息在网络传输过程中被窃听 | 核查远程管理是否使用 SSH 等加密通道；核查 Telnet/FTP 是否已禁用 | Postfix/Dovecot 管理仅开放 SSH（端口 22）；禁用 Telnet；SSH 禁用密码登录，仅密钥认证 |
| d | **应采用口令、密码技术、生物技术等两种或两种以上组合的鉴别技术** | 核查是否启用双因子认证（2FA） | Dovecot SASL 集成 OAuth2/TOTP；管理界面加 Google Authenticator 或硬件令牌 |

#### 配置示例：系统层密码复杂度与锁定策略

```
# /etc/pam.d/system-auth（RHEL/CentOS 系列）
# 密码复杂度：最小 8 位，包含大小写、数字、特殊字符
password  requisite   pam_pwquality.so try_first_pass local_users_only \
    minlen=8 dcredit=-1 ucredit=-1 lcredit=-1 ocredit=-1 enforce_for_root

# 登录失败锁定：连续 5 次失败锁定 300 秒
auth      required    pam_faillock.so preauth silent audit deny=5 unlock_time=300
auth      required    pam_faillock.so authfail audit deny=5 unlock_time=300

# 系统会话超时
echo "TMOUT=600" >> /etc/profile
echo "export TMOUT" >> /etc/profile
```

#### 配置示例：Dovecot 强制 TLS + 禁用明文认证

```
# /etc/dovecot/conf.d/10-ssl.conf
ssl = required
ssl_cert =
```

#### 配置示例：Fail2ban 针对邮件服务

```
# /etc/fail2ban/jail.local
[dovecot]
enabled  = true
port     = pop3,pop3s,imap,imaps,submission,465,sieve
filter   = dovecot
logpath  = /var/log/mail.log
maxretry = 5
bantime  = 600
findtime = 300

[postfix-sasl]
enabled  = true
port     = smtp,465,submission
filter   = postfix[mode=auth]
logpath  = /var/log/mail.log
maxretry = 3
bantime  = 1800
findtime = 300
```

### 3.2 访问控制（L3-CES2）

3.2 访问控制（L3-CES2）

| 序号 | 要求项（三级） | 测评要点 | 邮件系统对应措施 |
| --- | --- | --- | --- |
| a | 应对登录的用户分配账户和权限 | 核查是否存在未授权账户；核查权限是否遵循最小权限原则 | 仅管理员有 Shell 访问；邮件用户通过虚拟账户运行，无系统 Shell |
| b | 应重命名或删除默认账户，修改默认口令 | 核查 root 是否允许直接 SSH 登录；核查默认应用账户 | `PermitRootLogin no` ；删除/禁用 postmaster 等默认账户的 Shell 权限 |
| c | 应及时删除或停用多余、过期的账户，避免共享账户 | 核查账户列表；访谈运维人员 | 建立账户生命周期管理流程；季度审计账户清单 |
| d | 应授予管理用户所需的最小权限，实现管理用户的权限分离 | 核查是否区分系统管理员、安全管理员、审计管理员 | 三权分立：root（系统）、audit（审计）、secadmin（安全策略）分别使用不同账户，sudo 细粒度授权 |
| e | 应由授权主体配置访问控制策略，访问控制策略规定主体对客体的访问规则 | 核查 ACL 配置 | Postfix `smtpd_recipient_restrictions` 控制中继权限；邮箱目录 DAC 权限 0600 |
| f | **访问控制的粒度应达到主体为用户级或进程级，客体为文件、数据库表级** | 核查文件系统权限；核查数据库表权限 | Maildir 目录 `chmod 700` ；MySQL/PostgreSQL 虚拟用户表仅授权应用账户 SELECT |
| g | **应对重要主体和客体设置安全标记** | 核查是否启用 SELinux | SELinux enforcing 模式 + 自定义邮件策略 |

#### 配置示例：Postfix 访问控制与权限分离

```
# /etc/postfix/main.cf — 限制中继权限
smtpd_recipient_restrictions =
    permit_mynetworks,
    permit_sasl_authenticated,
    reject_unauth_destination,
    reject_invalid_hostname,
    reject_non_fqdn_sender,
    reject_non_fqdn_recipient,
    reject_unknown_sender_domain,
    reject_unknown_recipient_domain

# 邮箱目录权限控制
# Maildir 应设置为 700（仅所有者可访问）
find /var/vmail -type d -exec chmod 0700 {} \;
find /var/vmail -type f -exec chmod 0600 {} \;

# SELinux 确保在 enforcing 模式
sestatus
# SELinux status:  enabled
# Current mode:   enforcing

# 三权分立 — sudo 细粒度授权
# /etc/sudoers.d/audit
%audit  ALL=(root) /usr/bin/ausearch, /usr/bin/aureport, /usr/bin/journalctl
# /etc/sudoers.d/security
%secadmin ALL=(root) /usr/sbin/setenforce, /usr/bin/firewall-cmd
```

### 3.3 安全审计（L3-CES3）

3.3 安全审计（L3-CES3）

| 序号 | 要求项（三级） | 测评要点 | 邮件系统对应措施 |
| --- | --- | --- | --- |
| a | 应启用安全审计功能，覆盖到每个用户，对重要用户行为和重要安全事件进行审计 | 核查审计范围是否覆盖所有用户   核查是否记录重要操作 auditd 记录所有与 `/etc/postfix` 、 `/etc/dovecot` 相关的配置变更；rsyslog 记录 Postfix/Dovecot 运行日志 || b | 审计记录应包括事件的日期、时间、用户、事件类型、事件是否成功及其他相关信息 | 核查日志格式完整性 | Postfix 默认日志满足要求；需要额外配置 Dovecot `mail_log` 插件记录邮箱操作 | | c | 应对审计记录进行保护，定期备份，避免未预期的删除、修改或覆盖 | 核查日志文件权限   核查日志保留周期（≥ 6 个月） `/var/log/mail*` 文件权限 0600；logrotate 保留 180 天；日志远程转发到集中日志服务器 || d | **应对审计进程进行保护，防止未经授权的中断** | 核查 auditd 守护进程是否受保护 | `auditctl -e 2` 将审计规则设为不可变 | 配置示例：系统层安全审计（auditd）  ``` # /etc/audit/rules.d/mail-security.rules # 监控 Postfix 主配置文件变更 -w /etc/postfix/main.cf -p wa -k mail_config_change -w /etc/postfix/master.cf -p wa -k mail_config_change  # 监控 Dovecot 配置文件变更 -w /etc/dovecot/ -p wa -k mail_config_change  # 监控邮件存储目录非授权访问 -w /var/vmail/ -p rwa -k mail_store_access  # 监控证书文件变更 -w /etc/pki/tls/certs/mail.crt -p wa -k mail_cert_change -w /etc/pki/tls/private/mail.key -p wa -k mail_cert_change  # 重启 auditd 并设为不可变 auditctl -R /etc/audit/rules.d/mail-security.rules auditctl -e 2   # 设置为不可变模式，重启前不可修改 service auditd restart ```  配置示例：rsyslog 集中转发邮件日志  ``` # /etc/rsyslog.d/30-mail-remote.conf # 将所有 mail 相关日志转发到集中日志服务器 mail.*  @@192.168.10.50:514 # 本地同时保留副本 mail.*  /var/log/mail.log  # logrotate 保留 180 天 # /etc/logrotate.d/mail /var/log/mail.log {     weekly     rotate 26     missingok     notifempty     compress     delaycompress     sharedscripts     postrotate         /bin/systemctl reload rsyslog > /dev/null 2>&1 || true     endscript } ```  3.4 入侵防范（L3-CES4）  3.4 入侵防范（L3-CES4）  | 序号 | 要求项（三级） | 测评要点 | 邮件系统对应措施 | | --- | --- | --- | --- | | a | 应遵循最小安装的原则，仅安装需要的组件和应用程序 | 核查操作系统已安装软件包列表 | 仅安装 Postfix + Dovecot + 必要依赖，移除与邮件无关的 app | | b | 应关闭不需要的系统服务、默认共享和高危端口 | 核查开放端口列表 | 仅开放 25、465、587、993、995、22；关闭 NFS、Samba、RPC 等服务 | | c | 应通过设定终端接入方式或网络地址范围对通过网络进行管理的管理终端进行限制 | 核查 SSH 是否绑定了管理 IP 段 | `/etc/hosts.allow` 或 iptables 限制 SSH 来源 IP；绑定管理 VLAN | | d | 应能发现可能存在的已知漏洞，并在经过充分测试评估后及时修补 | 核查补丁管理和漏洞扫描记录 | 每月执行 OpenVAS/Nessus 扫描；72h 内修复高危漏洞 | | e | **应能检测到对重要节点的入侵行为，并在发生严重入侵事件时提供报警** | 核查 IDS/IPS 部署情况 | 部署 Snort/Suricata 监控邮件流量；对接 SIEM 产生告警 |  配置示例：最小化攻击面  ``` # 查看并关闭不必要的服务 systemctl list-unit-files --state=enabled | grep -vE 'postfix|dovecot|sshd|auditd|rsyslog|fail2ban' systemctl disable --now rpcbind nfs-server smb cups bluetooth avahi-daemon  # 仅开放必要端口（iptables） iptables -A INPUT -p tcp --dport 25  -j ACCEPT   # SMTP iptables -A INPUT -p tcp --dport 465 -j ACCEPT   # SMTPS iptables -A INPUT -p tcp --dport 587 -j ACCEPT   # Submission iptables -A INPUT -p tcp --dport 993 -j ACCEPT   # IMAPS iptables -A INPUT -p tcp --dport 995 -j ACCEPT   # POP3S iptables -A INPUT -p tcp --dport 22  -s 10.0.1.0/24 -j ACCEPT  # SSH only from mgmt VLAN iptables -A INPUT -j DROP  # 限制 SSH 来源 # /etc/hosts.allow sshd: 10.0.1.0/255.255.255.0 # /etc/hosts.deny sshd: ALL ```  3.5 数据完整性（L3-CES6）  3.5 数据完整性（L3-CES6）  | 序号 | 要求项（三级） | 测评要点 | 邮件系统对应措施 | | --- | --- | --- | --- | | a | 应采用校验技术或密码技术保证重要数据在传输过程中的完整性 | 核查通信协议是否提供完整性校验 | SMTP/IMAP/POP3 全部启用 TLS 1.2+；启用 DKIM 签名保证邮件内容完整性 | | b | **应采用校验技术或密码技术保证重要数据在存储过程中的完整性** | 核查是否有完整性校验机制 | AIDE/Tripwire 对邮件文件和配置文件做完整性校验；数据库开启校验和 |  配置示例：AIDE 文件完整性监控  ``` # 初始化 AIDE 数据库 aide --init cp /var/lib/aide/aide.db.new.gz /var/lib/aide/aide.db.gz  # /etc/aide.conf — 邮件系统关键路径监控 /etc/postfix       CONTENT_EX /etc/dovecot       CONTENT_EX /var/vmail         CONTENT /etc/pki/tls       CONTENT_EX  # 每日完整性检查（cron） 0 3 * * * /usr/sbin/aide --check | mail -s "AIDE Report $(date +%F)" audit@example.com ```  3.6 数据保密性（L3-CES7）  3.6 数据保密性（L3-CES7）  | 序号 | 要求项（三级） | 测评要点 | 邮件系统对应措施 | | --- | --- | --- | --- | | a | 应采用密码技术保证重要数据在传输过程中的保密性 | 核查 SMTP、IMAP、POP3 是否强制 TLS   核查是否支持明文回退 Postfix `smtpd_tls_security_level = encrypt` ；Dovecot `ssl = required` || b | **应采用密码技术保证重要数据在存储过程中的保密性** | 核查磁盘或文件级加密 | LUKS 全盘加密；或邮件存储目录使用 fscrypt/eCryptfs 文件级加密 | 配置示例：Postfix 强制 TLS 传输加密  ``` # /etc/postfix/main.cf — 强制 TLS 服务端 smtpd_use_tls = yes smtpd_tls_security_level = encrypt smtpd_tls_auth_only = yes smtpd_tls_cert_file = /etc/pki/tls/certs/mail.crt smtpd_tls_key_file = /etc/pki/tls/private/mail.key smtpd_tls_protocols = !SSLv2, !SSLv3, !TLSv1, !TLSv1.1 smtpd_tls_mandatory_protocols = !SSLv2, !SSLv3, !TLSv1, !TLSv1.1 smtpd_tls_mandatory_ciphers = high smtpd_tls_ciphers = high smtpd_tls_eecdh_grade = ultra smtpd_tls_received_header = yes smtpd_tls_session_cache_database = btree:${data_directory}/smtpd_scache smtpd_tls_session_cache_timeout = 3600s  # 出站邮件也尽量使用 TLS smtp_tls_security_level = may smtp_tls_protocols = !SSLv2, !SSLv3, !TLSv1, !TLSv1.1 smtp_tls_ciphers = high  # Postfix 提交端口（587）强制认证 + 加密 # /etc/postfix/master.cf submission inet n       -       n       -       -       smtpd   -o syslog_name=postfix/submission   -o smtpd_tls_security_level=encrypt   -o smtpd_sasl_auth_enable=yes   -o smtpd_client_restrictions=permit_sasl_authenticated,reject ```  3.7 数据备份恢复（L3-CES8）  3.7 数据备份恢复（L3-CES8）  | 序号 | 要求项（三级） | 测评要点 | 邮件系统对应措施 | | --- | --- | --- | --- | | a | 应提供重要数据的本地数据备份与恢复功能 | 核查是否有本机备份策略 | rsync 每日增量备份 /var/vmail 到本地备份分区 | | b | 应提供异地实时备份功能，利用通信网络将重要数据实时备份至备份场地 | 核查是否有异地备份 | rsync + SSH 或 rsyslog 转发到异地机房；实时同步使用 DRBD 或 GlusterFS | | c | 应提供重要数据处理系统的热冗余，保证系统的高可用性 | 核查是否有 HA 方案 | Keepalived + 双 Postfix 双 Dovecot；或使用 DNS MX 多优先级实现故障转移 |  配置示例：邮件备份脚本  ``` #!/bin/bash # /usr/local/bin/mail-backup.sh # 每日邮件数据备份，保留 30 天本地副本 + 远程同步  BACKUP_SRC="/var/vmail" BACKUP_DST="/backup/mail/$(date +%Y%m%d)" REMOTE_HOST="backup@10.0.2.100" REMOTE_PATH="/backup/mail" RETENTION_DAYS=30  # 本地增量备份 rsync -avz --delete "$BACKUP_SRC/" "$BACKUP_DST/"  # 异地同步 rsync -avz --delete -e "ssh -i /root/.ssh/backup_key" \     "$BACKUP_SRC/" "$REMOTE_HOST:$REMOTE_PATH/$(date +%Y%m%d)/"  # 清理超过保留期的本地备份 find /backup/mail/ -maxdepth 1 -type d -mtime +$RETENTION_DAYS -exec rm -rf {} \;  # 记录日志 logger -t mail-backup "Mail backup completed: $(date)" ```  四、安全通信网络与邮件传输加密 GB/T 22239-2019 把"通信传输"从原来的"网络安全"中独立出来，列为安全通信网络下的专项控制点，对邮件系统的影响直接映射到 SMTP（发信）、IMAP/POP3（收信）和管理通信三条链路上。 4.1 通信传输（L3-CNS1-06 / L3-CNS1-07）  4.1 通信传输（L3-CNS1-06 / L3-CNS1-07）  | 要求项 | 二级 | 三级 | 邮件实现 | | --- | --- | --- | --- | | 通信完整性 | 应采用校验技术保证通信过程中数据的完整性 | 应采用 **密码技术** 保证通信过程中数据的完整性 | TLS 1.2+ 的 HMAC 模式；DKIM 签名（RSA-SHA256） | | 通信保密性 | — | **应采用密码技术保证通信过程中数据的保密性** | TLS 强制加密；SMTPS（465）/ IMAPS（993）/ POP3S（995）/ Submission（587 TLS） |  4.2 网络架构与通信安全 **⚠️ 高风险判定：** 在不可控网络环境中（如互联网），如果管理账号的口令以明文方式传输，且使用 Telnet、HTTP、FTP 等未加密协议，则依据《网络安全等级保护测评高风险判定指引》，可判定为 **高风险** ——意味着测评不通过。邮件系统的远程管理必须走 SSH 或 VPN 加密通道。 配置示例：DKIM 签名配置  ``` # OpenDKIM — /etc/opendkim.conf Syslog          yes UMask           002 Canonicalization relaxed/simple Mode            sv SubDomains      no OversignHeaders From SignatureAlgorithm rsa-sha256  # 必须使用 SHA-256，SHA-1 不符合密码强度要求 AutoRestart     yes AutoRestartRate 10/1h KeyTable        /etc/opendkim/KeyTable SigningTable    refile:/etc/opendkim/SigningTable ExternalIgnoreList refile:/etc/opendkim/TrustedHosts InternalHosts   refile:/etc/opendkim/TrustedHosts  # /etc/opendkim/KeyTable default._domainkey.example.com example.com:default:/etc/opendkim/keys/example.com/default.private  # /etc/opendkim/SigningTable *@example.com default._domainkey.example.com  # DNS 记录发布 DKIM 公钥 # default._domainkey.example.com TXT "v=DKIM1; h=sha256; k=rsa; p=MIIBIjAN..." ```  配置示例：SPF + DMARC DNS 记录  ``` # SPF — DNS TXT 记录（@ 或根域名） "v=spf1 mx a ip4:203.0.113.10 -all" # -all = 硬拒绝，仅允许 MX/A 记录 IP 和指定 IP 发送  # DMARC — DNS TXT 记录（_dmarc.example.com） "v=DMARC1; p=quarantine; rua=mailto:dmarc-reports@example.com; ruf=mailto:dmarc-forensic@example.com; pct=100; adkim=r; aspf=r" ```  五、安全区域边界：邮件边界的访问控制与入侵防范 对于邮件系统，"安全区域边界"主要落实在邮件网关、防火墙规则和 DMZ 网络分区三个层面。   五、安全区域边界：邮件边界的访问控制与入侵防范  | 控制点 | 三级要求 | 邮件边界对应措施 | | --- | --- | --- | | 边界防护 (ABS1) | 应保证跨越边界的访问和数据流通过边界设备提供的受控接口进行通信 | 邮件服务器部署在 DMZ 区，通过防火墙 NAT 暴露 SMTP/IMAP/POP3，内部后端（数据库）不暴露 | | 访问控制 (ABS2) | 应在网络边界根据访问控制策略设置访问控制规则，默认除允许通信外受控接口拒绝所有通信 | 防火墙默认 DROP，仅开放邮件必需端口；应用层在 Postfix `smtpd_recipient_restrictions` 中实现白名单/黑名单控制 | | 入侵防范 (ABS3) | 应在关键网络节点处检测、防止或限制从外部发起的网络攻击行为 | WAF / IPS 前置或邮件网关层部署；Fail2ban 自动封禁爆破 IP | | 安全审计 (ABS4) | 应在网络边界对重要的用户行为和重要安全事件进行审计 | 防火墙日志转发 SIEM；使用 `pflogsumm` 每日汇总 Postfix 流量与异常 |  配置示例：防火墙规则（iptables 白名单模式）  ``` #!/bin/bash # 邮件服务器边界防火墙白名单 # 默认 DROP，仅开放最小必要端口  iptables -P INPUT DROP iptables -P FORWARD DROP iptables -P OUTPUT ACCEPT  # 允许已建立的连接 iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT  # 回环接口 iptables -A INPUT -i lo -j ACCEPT  # 邮件服务端口（面向 Internet） iptables -A INPUT -p tcp --dport 25  -m state --state NEW -j ACCEPT iptables -A INPUT -p tcp --dport 465 -m state --state NEW -j ACCEPT iptables -A INPUT -p tcp --dport 587 -m state --state NEW -j ACCEPT iptables -A INPUT -p tcp --dport 993 -m state --state NEW -j ACCEPT iptables -A INPUT -p tcp --dport 995 -m state --state NEW -j ACCEPT  # SSH 仅管理网段 iptables -A INPUT -p tcp --dport 22 -s 10.0.1.0/24 -m state --state NEW -j ACCEPT  # ICMP（可选，用于 MTU 探测） iptables -A INPUT -p icmp --icmp-type echo-request -m limit --limit 1/s -j ACCEPT  # 记录并丢弃其余流量 iptables -A INPUT -j LOG --log-prefix "IPTABLES-DROP: " --log-level 4 iptables -A INPUT -j DROP ```  六、云计算安全扩展要求：云上邮件系统 当[邮件系统部署](/kb/category/ops-architecture.html)在云平台（无论 IaaS/PaaS/SaaS）时，GB/T 22239-2019 附录中的 **云计算安全扩展要求** 生效。责任边界取决于云服务模式——IaaS 场景下客户承担 Guest OS 及以上的安全责任；SaaS 邮件服务则大部分控制项由云服务商承担。 6.1 云环境关键控制项  6.1 云环境关键控制项  | 控制点 | 要求 | 邮件系统关注点 | | --- | --- | --- | | 基础设施位置 | 云计算基础设施应位于中国境内 | 邮件数据（含用户凭证和邮件正文）存储和传输必须不离开境内机房 | | 网络架构 | 不承载高于自身等级的应用；租户间网络隔离 | 邮件 VM 不应与其他租户共享同一 VLAN/VPC；使用安全组实现东西向隔离 | | 访问控制 | 虚拟网络边界部署访问控制规则；策略随 VM 迁移 | 云防火墙/安全组规则自动化；Terraform 管理基础设施即代码（IaC） | | 入侵防范 | 检测租户网络攻击、VM 与宿主机异常流量 | 云原生 IDS（如 VPC Flow Logs）；主机 HIDS 覆盖邮件 VM | | 镜像和快照 | 提供镜像和快照的完整性校验 | 邮件 VM 快照哈希校验；定期验证备份可恢复性 | | 安全审计 | 云服务商操作可被客户审计 | 开启云平台操作审计日志（API 调用记录），确保透明可追溯 |  6.2 云上邮件系统架构建议 如果自建邮件服务器部署在 IaaS 平台，推荐的最小安全架构如下：   1. **VPC 隔离**    ：邮件服务器独占一个 VPC / 虚拟网络，不与业务系统混部 2. **DMZ + 内网两层部署**    ：Postfix 前置（SMTP 网关）在 DMZ 子网；Dovecot + 数据库在后端子网，仅允许来自 DMZ 的指定端口流量 3. **安全组白名单**    ：入口规则仅放行 25/465/587/993/995；出站规则限制为必要的外部服务（DNS、NTP、软件源） 4. **加密存储**    ：云硬盘启用加密；快照启用加密 5. **运维堡垒机**    ：所有管理操作通过堡垒机执行，SSH 私钥不存放于运维终端  七、测评指标与证据准备 测评机构将依照 GB/T 28448-2019《信息安全技术 网络安全等级保护测评要求》执行测评，每个测评单元都有对应的 **测评方法** 和 **预期证据** 。以下整理邮件系统在等保三级测评中的典型测评记录表（节选）。 7.1 安全计算环境 — 典型测评记录表（邮件服务器）  7.1 安全计算环境 — 典型测评记录表（邮件服务器）  | 测评单元编号 | 测评项 | 测评方法 | 预期证据 | | --- | --- | --- | --- | | L3-CES1-01 | 身份标识唯一性、口令复杂度、定期更换 | 核查 /etc/pam.d/system-auth；核查 /etc/login.defs；访谈管理员 | 口令策略截图；PASS\_MAX\_DAYS ≤ 90；PASS\_MIN\_LEN ≥ 8；测试 3 个弱口令无法创建 | | L3-CES1-03 | 远程管理防窃听 | 尝试使用 Telnet 连接 22 端口；检查 SSH 配置 | `telnet mail.example.com 22` 失败或返回 SSH banner；sshd\_config 中 `Protocol 2` | | L3-CES1-04 | 双因子认证 | 核查 PAM Google Authenticator 配置 | `/etc/pam.d/sshd` 含 `pam_google_authenticator.so` ；演示登录需输入验证码 | | L3-CES3-01 | 安全审计覆盖范围 | `auditctl -l` ；核查日志内容 | audit 规则列表含邮件配置/存储路径；/var/log/audit/audit.log 含记录 | | L3-CES3-03 | 审计记录保护与备份 | 核查 logrotate 配置；核查日志存储位置 | 保留 ≥ 6 个月（约 26 周）；日志文件权限 0600；日志服务器转发确认 | | L3-CES4-01 | 最小安装 | `rpm -qa` 或 `dpkg -l` | 系统仅安装与邮件服务相关软件包及必要基础组件 | | L3-CES4-02 | 关闭高危端口 | `netstat -tlnp` | 开放端口仅 25/465/587/993/995/22 | | L3-CES6-01 | 传输完整性 | `openssl s_client -connect mail.example.com:25 -starttls smtp` | STARTTLS 成功协商；输出含 TLS 版本 ≥ 1.2 和密码套件信息 | | L3-CES7-01 | 传输保密性 | 核查 Postfix/Dovecot TLS 配置；抓包验证 | 所有邮件协议端口均返回加密连接；不出现明文认证 | | L3-CES8-02 | 异地备份 | 核查备份脚本；核查远程备份服务器记录 | 异地备份成功日志；备份增量同步脚本及 crontab |  7.2 通信网络安全 — 典型测评记录表  7.2 通信网络安全 — 典型测评记录表  | 测评单元编号 | 测评项 | 测评方法 | 预期证据 | | --- | --- | --- | --- | | L3-CNS1-06 | 通信完整性（密码技术） | 核查邮件协议 TLS 配置；核查 DKIM 配置 | TLS 版本 ≥ 1.2；DKIM 签名算法为 rsa-sha256；DMARC 策略 p=quarantine 或 p=reject | | L3-CNS1-07 | 通信保密性（密码技术） | 核查 TLS 密码套件 | `ssl_cipher_list` / `smtpd_tls_ciphers` 不含 NULL/EXPORT/DES/RC4 等不安全套件 |  八、NIST SP 800-53 Rev.5 对照：国际基准映射 对于同时需要满足国际合规要求（如 ISO 27001、SOC 2）的邮件系统，以下将 GB/T 22239-2019 的核心控制项与 NIST SP 800-53 Rev.5 进行对照映射，便于理解等保控制项在国际框架中的位置。   八、NIST SP 800-53 Rev.5 对照：国际基准映射  | GB/T 22239-2019 控制点 | 对应 NIST SP 800-53 Rev.5 控制族 | 映射控制项 | 备注 | | --- | --- | --- | --- | | 身份鉴别 | IA — Identification and Authentication | IA-2, IA-5, IA-8 | 等保"双因子"对应 IA-2(1) + IA-5(1)；密码复杂度对应 IA-5(1) | | 访问控制 | AC — Access Control | AC-2, AC-3, AC-5, AC-6 | 等保"主体/客体级粒度"对应 AC-6 最小权限；三权分立对应 AC-5 职责分离 | | 安全审计 | AU — Audit and Accountability | AU-2, AU-3, AU-4, AU-9, AU-11 | 等保 6 个月日志保留对应 AU-11；审计记录保护对应 AU-9 | | 入侵防范 | SI — System and Information Integrity | SI-2, SI-3, SI-4, SI-5 | 等保漏洞修复时效对应 SI-2 补丁管理；IDS 对应 SI-4 系统监控 | | 数据完整性 | SI — System and Information Integrity | SI-7, SC-8(1) | 传输完整性对应 SC-8(1) 加密完整性保护；文件完整性对应 SI-7 | | 数据保密性 | SC — System and Communications Protection | SC-8, SC-13, SC-28 | 传输保密性对应 SC-8；存储保密性对应 SC-28 | | 通信传输（完整性） | SC — System and Communications Protection | SC-8, SC-8(1) | TLS 1.2+ 防护对应 SC-8；DKIM 签名对应 SC-8(1) | | 数据备份恢复 | CP — Contingency Planning | CP-9, CP-10 | 本地/异地备份对应 CP-9；系统恢复对应 CP-10 | | 安全区域边界 — 访问控制 | AC — Access Control | AC-4, AC-17 | 边界访问控制规则对应 AC-4 信息流强制 | | 云计算扩展 — 网络架构 | AC — Access Control, SC | AC-4, SC-7 | 租户间隔离对应 SC-7 边界防护 + AC-4 信息流强制 |   **📌 映射解读：** 等保 2.0 与 NIST SP 800-53 Rev.5 在安全目标上高度一致，均围绕"识别-保护-检测-响应-恢复"构建防御体系。差异在于：等保侧重"合规基线"，通过标准化控制项列表直接规定必须达到的技术措施；NIST SP 800-53 更强调"风险管理"——控制项提供可选增强，由组织根据风险评估自行选择基准线（Low/Moderate/High），灵活性更大但自我裁量权也更高。 九、高分项、失分项与实践指南9.1 邮件系统等保测评常见失分项 Top 5  9.1 邮件系统等保测评常见失分项 Top 5  | 排名 | 失分项 | 失分率 | 原因分析 | 整改方案 | | --- | --- | --- | --- | --- | | 1 | 未实现双因子认证 | 78% | 三级等保强制要求两种以上鉴别技术，大量二级系统也未提前准备 | SSH + Google Authenticator (TOTP)；或接入企业统一认证（LDAP+OTP） | | 2 | 审计日志保留不足 6 个月 / 日志可删除 | 65% | 默认 logrotate 仅保留 4 周；日志文件权限不严可被普通用户删除 | logrotate 调整至 26 周；/var/log 权限收紧；日志实时转发至专用日志服务器 | | 3 | TLS 密码套件仍包含不安全算法 | 55% | Postfix/Dovecot 默认配置可能接受 TLSv1.0/1.1 或 RC4/3DES 等弱密码 | 禁用 TLSv1.0/1.1；密码套件限制为 AEAD 族（GCM/CHACHA20） | | 4 | 未部署文件完整性校验（AIDE / Tripwire） | 50% | 许多运维团队未意识到"数据存储完整性"需要文件级校验，认为磁盘 RAID 即可 | 部署 AIDE 并对关键配置文件/邮件存储目录做日常检查 | | 5 | 未实现三权分立（系统/安全/审计管理员分离） | 45% | 小团队"一人多角"，所有管理操作共用 root 账户 | 创建 audit / secadmin 独立账户，sudo 精准授权，audit 日志不可由 root 单方面删除 |  9.2 高分项实践清单 以下控制项在测评中如果做到位，可显著提升合规评分，也是安全实践中最具性价比的投入：   9.2 高分项实践清单  | 控制项 | 高分实践 | 测评加分点 | | --- | --- | --- | | TLS 传输加密 | 全端口强制 TLS 1.2+；SMTP MTA-STS + DANE/TLSA | MTA-STS 策略文件 + TLSA 记录展示对前沿标准的跟进 | | DKIM / SPF / DMARC | 三条记录全部配置且 DMARC p=reject | 证明邮件防伪体系完善 | | 安全审计 | auditd + rsyslog 远程转发 + SIEM 分析 | 日志完整、不可篡改、具备分析能力 | | 入侵防范 | Fail2ban + HIDS + 定期漏洞扫描报告 | 主动防御 + 持续监控 | | 备份恢复 | 本地 + 异地 + 定期恢复演练记录 | 有演练记录比单纯备份更有说服力 | | 安全管理 | 完整的制度文件 + 操作规程 + 记录表单 | 纸质/电子制度体系完整 + 版本控制记录 |  9.3 测评前的自查脚本 以下 shell 脚本可在测评前进行基线自查，快速定位不符合项：   ``` #!/bin/bash # 邮件系统等保三级自查脚本 # 用法: bash dengbao-mail-check.sh | tee check-report.txt  echo "========================================" echo "  邮件系统等保三级自查报告" echo "  执行时间: $(date '+%Y-%m-%d %H:%M:%S')" echo "========================================"  # 1. 密码策略检查 echo -e "\n[身份鉴别] 密码复杂度与有效期" grep -E '^PASS_MAX_DAYS|^PASS_MIN_DAYS|^PASS_MIN_LEN|^PASS_WARN_AGE' /etc/login.defs grep 'pam_pwquality' /etc/pam.d/system-auth 2>/dev/null || echo "⚠ pwquality 未配置"  # 2. SSH 安全检查 echo -e "\n[身份鉴别] SSH 安全配置" grep -E '^PermitRootLogin|^PasswordAuthentication|^Protocol|^MaxAuthTries' /etc/ssh/sshd_config 2>/dev/null grep 'pam_google_authenticator\|pam_oath' /etc/pam.d/sshd 2>/dev/null || echo "⚠ 双因子认证未配置"  # 3. 开放端口 echo -e "\n[入侵防范] 活跃监听端口" ss -tlnp | grep LISTEN  # 4. TLS 配置 echo -e "\n[通信保密性] Postfix TLS 配置" postconf smtpd_tls_security_level smtpd_tls_protocols smtpd_tls_mandatory_protocols 2>/dev/null echo -e "\n[通信保密性] Dovecot SSL 配置" grep -E '^ssl\s*=|^ssl_min_protocol|^ssl_cipher_list' /etc/dovecot/conf.d/10-ssl.conf 2>/dev/null  # 5. 审计配置 echo -e "\n[安全审计] auditd 状态" auditctl -l 2>/dev/null | head -20 echo "---" grep -E '^max_log_file|^num_logs|^max_log_file_action' /etc/audit/auditd.conf 2>/dev/null  # 6. 日志保留周期 echo -e "\n[安全审计] logrotate 邮件日志保留策略" grep -A5 '/var/log/mail' /etc/logrotate.d/* 2>/dev/null  # 7. SELinux 状态 echo -e "\n[访问控制] SELinux" sestatus 2>/dev/null || echo "⚠ SELinux 未安装或未运行"  # 8. Fail2ban echo -e "\n[入侵防范] Fail2ban 邮件 jail 状态" fail2ban-client status dovecot 2>/dev/null || echo "⚠ dovecot jail 未启用" fail2ban-client status postfix-sasl 2>/dev/null || echo "⚠ postfix-sasl jail 未启用"  # 9. 备份检查 echo -e "\n[数据备份] crontab 备份任务" crontab -l 2>/dev/null | grep -i 'backup\|rsync' || echo "⚠ 未发现备份定时任务"  # 10. 文件权限摘要 echo -e "\n[访问控制] 邮件存储目录权限" stat -c '%a %n' /var/vmail 2>/dev/null || echo "⚠ /var/vmail 不存在"  echo -e "\n========================================" echo "  自查完成。请逐项核查并整改不符合项。" echo "========================================" ```  十、结语 邮件系统是组织内外信息流转的核心枢纽，等保 2.0 对其提出了覆盖身份鉴别、访问控制、安全审计、入侵防范、数据完整性、数据保密性和备份恢复的全方位合规要求。相比 1.0 时代，2.0 在密码技术强制使用、双因子认证、审计不可篡改性、主动入侵检测、文件和传输完整性校验等方面的要求更为明确和严格。  从实践角度看，通过等保测评并非一次性的"应试"，而应视为持续的安全基线维护。建议运维团队将本文列举的配置命令和检查脚本纳入日常巡检流程，并在每次系统变更后进行回归验证。对于计划初次定级备案的邮件系统，建议先执行一次完整的差距分析，优先整改高风险项（弱口令、明文传输、缺审计），再逐步完善管理类控制项。  引用标准：   * GB/T 22239-2019《信息安全技术 网络安全等级保护基本要求》 * GB/T 28448-2019《信息安全技术 网络安全等级保护测评要求》 * GB/T 25070-2019《信息安全技术 网络安全等级保护安全设计技术要求》 * GB/T 22240-2020《信息安全技术 网络安全等级保护定级指南》 * GB/T 39786-2021《信息安全技术 信息系统密码应用基本要求》 * GB/T 37002-2018《信息安全技术 电子邮件系统安全技术要求》 * NIST Special Publication 800-53, Revision 5 — Security and Privacy Controls for Information Systems and Organizations | | |

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/dengbao2-email-compliance.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
