---
title: "信创邮件系统安全加固指南：从等保合规到纵深防御"
source: "https://ztpop.net/kb/xinchuang-security-hardening-guide.html"
license: CC-BY 4.0
---

# 信创邮件系统安全加固指南：从等保合规到纵深防御

## 摘要

信创邮件系统在承担党政机关和关键基础设施的日常通信职能时，其安全等级保护水平直接关系到国家信息安全。本文对照 GB/T 22239-2019《网络安全等级保护基本要求》的三级安全控制点，结合 GM/T 系列国密算法标准，系统阐述信创邮件系统的安全加固工程实践。内容覆盖等保三级控制点的邮件系统映射、国密 SM2/SM3/SM4 算法的邮件加密部署、审计日志体系构建、入侵检测规则制定、备份加密策略以及应急响应流程设计。

## 一、等保 2.0 三级要求与邮件系统的映射

GB/T 22239-2019 将等保三级的安全要求划分为技术和管理两大类，共 10 个安全类、76 个控制项。以下筛选出与邮件系统直接相关的关键控制点并进行映射：

### 1.1 技术层面控制点映射

1.1 技术层面控制点映射

| 等保三级控制项 | 要求内容 | 邮件系统加固措施 |
| 安全通信网络-通信传输 | 应采用密码技术保证通信过程中数据的完整性、保密性 | SMTP/IMAP/POP3 强制 STARTTLS，WebMail 强制 HTTPS，证书使用国密 SM2 或 RSA-2048 |
| 安全区域边界-访问控制 | 应在网络边界部署访问控制设备，启用访问控制功能 | iptables/nftables 白名单策略，仅开放 SMTP(25)、Submission(587)、IMAPS(993)、POP3S(995)、HTTPS(443) |
| 安全区域边界-入侵防范 | 应在关键网络节点处检测和限制外部发起的网络攻击行为 | 部署 Fail2ban 防暴力破解，配置 Snort/Suricata 邮件协议异常检测规则 |
| 安全计算环境-身份鉴别 | 应对登录用户进行身份标识和鉴别，口令应具有复杂度要求并定期更换 | WebMail 双因子认证(TOTP)、口令长度≥8位含大小写数字特殊字符、90天强制更换 |
| 安全计算环境-数据保密性 | 应采用密码技术保证重要数据在存储过程中的保密性 | 邮件正文 SM4 加密存储、数据库敏感字段 AES-256/SM4 加密 |
| 安全计算环境-数据备份恢复 | 应提供重要数据的本地数据备份与恢复功能 | 每日全量备份+每小时增量备份，备份文件 SM4 加密，异地离线存储 |
| 安全管理中心-集中管控 | 应划分出特定管理区域，对分布在网络中的安全设备进行集中管控 | 统一审计日志平台（ELK/Loki），所有安全事件汇聚至安全管理中心 |
| 安全管理中心-审计管理 | 应对审计记录进行保护，定期备份，避免受到未预期的删除、修改或覆盖 | 审计日志写入 syslog 远程服务器，本地日志文件只追加、不可修改 |

## 二、国密算法在邮件系统中的部署

国家密码管理局发布的 GM/T 系列标准定义了适用于商用密码的算法体系。在信创邮件系统中，国密算法主要用于三个场景：传输层加密（SM2 证书）、邮件内容加密（SM4）、和完整性校验（SM3）。

### 2.1 SM2 椭圆曲线公钥密码算法（GM/T 0003）

SM2 基于 256 位椭圆曲线，安全强度等效于 RSA-3072，优于 RSA-2048。在邮件系统中，SM2 主要用于 TLS 证书。OpenSSL 1.1.1+ 已通过 GM/T 引擎支持国密算法，部署步骤如下：

```
# 1. 安装国密 OpenSSL 引擎（麒麟 V10 / 统信 UOS 通用）
dnf install -y openssl gmssl gmssl-devel
# 或从源码编译
wget https://github.com/guanzhi/GmSSL/archive/refs/tags/v3.1.0.tar.gz
tar xzf v3.1.0.tar.gz && cd GmSSL-3.1.0
mkdir build && cd build
cmake .. -DCMAKE_INSTALL_PREFIX=/opt/gmssl
make -j$(nproc) && make install

# 2. 生成 SM2 密钥对（用于邮件服务器 TLS 证书）
/opt/gmssl/bin/gmssl sm2keygen \
    -out /etc/pki/tls/private/mail_sm2.key \
    -pubout /etc/pki/tls/certs/mail_sm2.pub

# 3. 生成 SM2 自签名证书（生产环境应使用 CFCA 等 CA 签发的国密证书）
/opt/gmssl/bin/gmssl req \
    -x509 -sm3 -days 365 \
    -key /etc/pki/tls/private/mail_sm2.key \
    -out /etc/pki/tls/certs/mail_sm2.crt \
    -subj "/C=CN/ST=Beijing/L=Beijing/O=XinChuang/CN=mail.xinchuang.local"

# 4. 配置 MTA 使用 SM2 证书（Postfix 示例）
postconf -e 'smtpd_tls_cert_file = /etc/pki/tls/certs/mail_sm2.crt'
postconf -e 'smtpd_tls_key_file = /etc/pki/tls/private/mail_sm2.key'
postconf -e 'smtpd_tls_mandatory_protocols = TLSv1.2,!TLSv1.1,!TLSv1,!SSLv2,!SSLv3'
postconf -e 'smtpd_tls_mandatory_ciphers = high'
systemctl reload postfix
```

### 2.2 SM4 分组密码算法（GM/T 0002）

SM4 是对称加密算法，分组长度和密钥长度均为 128 位，适用于邮件正文和附件在服务器端的存储加密。在信创邮件系统中，可在邮件到达 MDA（Mail Delivery Agent）后对邮件正文执行 SM4 加密，仅在使用者通过 WebMail 读取时实时解密。这种"加密存储、透明读取"的模式兼顾了安全性与用户体验。

```
#!/usr/bin/env python3
# SM4 邮件存储加密封装（调用 GmSSL 命令行工具）
import subprocess
import os

def sm4_encrypt_mail(plaintext_path, key_hex, output_path):
    """对邮件文件进行 SM4-CBC 加密"""
    iv_hex = os.urandom(16).hex()  # 128-bit 随机 IV
    subprocess.run([
        '/opt/gmssl/bin/gmssl', 'sm4_cbc',
        '-key', key_hex,
        '-iv', iv_hex,
        '-in', plaintext_path,
        '-out', output_path,
        '-enc'
    ], check=True)
    # 将 IV 附加到加密文件头部供解密时使用
    with open(output_path, 'rb') as f:
        ciphertext = f.read()
    with open(output_path, 'wb') as f:
        f.write(bytes.fromhex(iv_hex) + b'\n' + ciphertext)

def sm4_decrypt_mail(encrypted_path, key_hex, output_path):
    """对 SM4 加密的邮件文件进行解密"""
    with open(encrypted_path, 'rb') as f:
        content = f.read()
    iv_line, ciphertext = content.split(b'\n', 1)
    iv_hex = iv_line.decode()
    # 写入纯净密文到临时文件
    tmp_cipher = encrypted_path + '.tmp'
    with open(tmp_cipher, 'wb') as f:
        f.write(ciphertext)
    subprocess.run([
        '/opt/gmssl/bin/gmssl', 'sm4_cbc',
        '-key', key_hex,
        '-iv', iv_hex,
        '-in', tmp_cipher,
        '-out', output_path,
        '-dec'
    ], check=True)
    os.unlink(tmp_cipher)

# 实际使用时，key_hex 应从密钥管理服务（KMS）中安全获取
# key_hex = kms_client.get_key('mail_encryption_key')
```

### 2.3 SM3 密码杂凑算法（GM/T 0004）

SM3 输出 256 位摘要值，安全性与 SHA-256 相当。在邮件系统中，SM3 的主要用途包括：邮件完整性校验、审计日志链式哈希（防止篡改）、以及用户口令哈希存储。

```
# 计算邮件文件的 SM3 摘要
/opt/gmssl/bin/gmssl sm3 /var/vmail/domain/user/new/msg_12345.eml

# 在数据库中存储 SM3 口令哈希（配合 salt）
# SQL 示例（达梦 DM8）
UPDATE mail_sys.t_user
SET password_enc = CONCAT('$SM3$', HEXTORAW(sm3_hash(CONCAT(salt, password))))
WHERE user_id = 10001;
```

## 三、审计日志体系构建

等保三级要求对用户登录、邮件收发、管理员操作等关键行为保留完整的审计记录，日志保存期限不少于 180 天。信创邮件系统的审计日志架构应遵循"本地生成、远程汇聚、不可篡改"的原则。

### 3.1 Syslog 远程日志配置

将邮件服务的所有操作日志以 syslog 格式实时发送至专用日志服务器。麒麟 V10 使用 rsyslog，配置如下：

```
# /etc/rsyslog.d/30-mail-audit.conf
# 定义邮件审计日志的本地文件
$template MailAuditLog, "/var/log/mail/audit_%$YEAR%%$MONTH%%$DAY%.log"

# 将 mail 设施的所有日志写入本地审计文件
mail.*  -?MailAuditLog

# 同时转发到远程日志服务器（TLS 加密传输）
$DefaultNetstreamDriver gtls
$DefaultNetstreamDriverCAFile /etc/pki/tls/certs/ca-bundle.crt
$ActionSendStreamDriverMode 1
$ActionSendStreamDriverAuthMode anon

mail.*  @@(o)log-collector.xinchuang.local:6514

# 配置轮转——保留 180 天
# /etc/logrotate.d/mail-audit
/var/log/mail/audit_*.log {
    daily
    rotate 180
    compress
    delaycompress
    missingok
    notifempty
    create 0600 root root
    postrotate
        /usr/bin/systemctl kill -s HUP rsyslog.service
    endscript
}
```

### 3.2 审计日志内容规范

邮件系统的审计日志应至少包含以下事件类型，每条日志应记录时间戳、用户标识、源 IP、操作类型、操作对象和结果：

```
# 审计日志格式示例（结构化 JSON）
{
  "timestamp": "2026-07-14T10:23:45.123+08:00",
  "event_type": "user.login",
  "user": "zhangsan@xinchuang.local",
  "src_ip": "192.168.10.100",
  "user_agent": "Mozilla/5.0 (X11; Linux aarch64)",
  "auth_method": "password+totp",
  "result": "success"
}
{
  "timestamp": "2026-07-14T10:24:12.456+08:00",
  "event_type": "mail.send",
  "user": "zhangsan@xinchuang.local",
  "message_id": "<20260714102412.a1b2c3@xinchuang.local>",
  "recipient": "lisi@example.gov.cn",
  "size_bytes": 245678,
  "has_attachment": true,
  "result": "queued"
}
```

## 四、入侵检测与防护规则

邮件系统面临的主要攻击类型包括 SMTP 认证暴力破解、IMAP 目录遍历、邮件炸弹和恶意附件投递。针对这些威胁，应在网络层和主机层分别部署检测规则。

### 4.1 Fail2ban 防暴力破解

```
# /etc/fail2ban/jail.d/mail.conf
[smtp-auth]
enabled  = true
port     = smtp,submission,465
filter   = smtp-auth
logpath  = /var/log/maillog
maxretry = 5
bantime  = 3600
findtime = 600

[imap-auth]
enabled  = true
port     = imap,imaps,pop3,pop3s
filter   = imap-auth
logpath  = /var/log/maillog
maxretry = 5
bantime  = 3600
findtime = 600

[webmail-auth]
enabled  = true
port     = http,https
filter   = webmail-auth
logpath  = /var/log/nginx/mail_access.log
maxretry = 8
bantime  = 1800
findtime = 300
```

### 4.2 Snort 邮件协议检测规则

在邮件服务器前端部署 Snort 3 并加载邮件相关检测规则，可拦截 SMTP 协议异常、恶意 MIME 结构和已知漏洞利用：

```
# /etc/snort/rules/local-mail.rules
# 检测 SMTP 命令注入尝试
alert tcp $EXTERNAL_NET any -> $HOME_NET 25 (
    msg:"SMTP Command Injection Attempt";
    flow:to_server,established;
    content:"|0d 0a|"; depth:2; offset:0;
    pcre:"/^(?!EHLO|HELO|MAIL|RCPT|DATA|QUIT|RSET|NOOP|VRFY|EXPN|HELP|AUTH|STARTTLS)[A-Z]/i";
    classtype:attempted-admin;
    sid:1000001; rev:1;
)

# 检测超大邮件头（邮件炸弹特征）
alert tcp $EXTERNAL_NET any -> $HOME_NET 25 (
    msg:"Oversized SMTP Header - Possible Mail Bomb";
    flow:to_server,established;
    content:"Subject:"; nocase;
    byte_test:4,>,2048,0,relative;
    classtype:denial-of-service;
    sid:1000002; rev:1;
)

# 检测可疑附件 MIME 类型
alert tcp $EXTERNAL_NET any -> $HOME_NET 25 (
    msg:"Suspicious MIME Attachment Type";
    flow:to_server,established;
    content:"Content-Type:"; nocase;
    pcre:"/Content-Type:\s*(application\/(x-msdownload|x-executable|x-dosexec|octet-stream))/i";
    classtype:suspicious-filename-detect;
    sid:1000003; rev:1;
)
```

## 五、备份加密与数据保护

根据等保三级"数据备份恢复"控制点的要求，邮件系统的备份策略需同时满足完整性、可用性和保密性。实践方案为"3-2-1 + 加密"原则：3 份拷贝、2 种介质、1 个异地副本，且所有副本均经过加密。

```
#!/bin/bash
# 邮件系统加密备份脚本
# 备份对象：Maildir 存储、数据库、配置文件
BACKUP_DIR="/backup/mail"
DATE_TAG=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/mail_full_${DATE_TAG}.tar.gz"
KEY_FILE="/etc/backup/key/backup.key"  # 32 字节 SM4 密钥

# 1. 压缩打包
tar -czf "${BACKUP_FILE}" \
    /var/vmail \
    /etc/postfix /etc/dovecot \
    /opt/mta/config 2>/dev/null

# 2. 计算 SM3 摘要（备份完整性基准）
SM3_HASH=$(/opt/gmssl/bin/gmssl sm3 "${BACKUP_FILE}")
echo "${SM3_HASH}  ${BACKUP_FILE}" >> "${BACKUP_DIR}/backup_manifest.sm3"

# 3. SM4 加密备份文件
/opt/gmssl/bin/gmssl sm4_cbc \
    -key $(cat "${KEY_FILE}") \
    -iv $(head -c 16 /dev/urandom | od -A n -t x1 | tr -d ' ') \
    -in "${BACKUP_FILE}" \
    -out "${BACKUP_FILE}.enc" \
    -enc

# 4. 删除未加密版本，仅保留加密备份
shred -u "${BACKUP_FILE}"

# 5. 复制到异地存储（通过 rsync over SSH）
rsync -avz --remove-source-files \
    "${BACKUP_FILE}.enc" \
    "backup@offsite-storage.xinchuang.local:/archive/mail/"

echo "Backup complete: ${BACKUP_FILE}.enc → offsite"
echo "SM3: ${SM3_HASH}"

# 6. 清理 30 天前的本地加密备份
find "${BACKUP_DIR}" -name "mail_full_*.tar.gz.enc" -mtime +30 -delete
```

## 六、应急响应流程

信创邮件系统的安全应急响应应参照 GB/T 37002 和等保三级关于应急响应的要求，建立标准化的"检测→分析→遏制→根除→恢复→复盘"六阶段流程。

### 6.1 邮件系统特有安全事件分类

6.1 邮件系统特有安全事件分类

| 事件等级 | 事件类型 | 响应时限 | 处置优先级 |
| I 级（特别重大） | 核心邮件数据泄露、认证体系被突破、系统被完全控制 | 15 分钟内启动 | 最高，全体应急小组 |
| II 级（重大） | 邮件服务大面积中断（超过 500 用户）、垃圾邮件大规模中继滥用 | 30 分钟内启动 | 高 |
| III 级（较大） | 单个用户账号被异常登录、定向钓鱼邮件攻击 | 2 小时内启动 | 中 |
| IV 级（一般） | 邮件延迟投递、单个客户端异常行为 | 4 小时内启动 | 常规 |

### 6.2 邮件数据泄露应急处置脚本

```
#!/bin/bash
# 邮件服务紧急隔离脚本
# 用途：在确认安全事件后迅速隔离受影响服务，保留现场证据

INCIDENT_ID="$1"
EVIDENCE_DIR="/var/log/incidents/${INCIDENT_ID}_$(date +%Y%m%d_%H%M%S)"

echo "[$(date)] 启动应急响应: ${INCIDENT_ID}"

# 1. 保存当前网络连接状态（证据保全）
mkdir -p "${EVIDENCE_DIR}"
ss -tuanp > "${EVIDENCE_DIR}/network_connections.txt"
iptables-save > "${EVIDENCE_DIR}/iptables_rules.txt"
ps auxf > "${EVIDENCE_DIR}/process_tree.txt"

# 2. 抓取 60 秒网络流量样本（tcpdump）
timeout 60 tcpdump -i any -w "${EVIDENCE_DIR}/traffic_sample.pcap" \
    port 25 or port 587 or port 993 or port 143

# 3. 备份当前邮件队列（供事后分析）
cp -a /var/spool/mta/deferred "${EVIDENCE_DIR}/deferred_queue"

# 4. 备份最新审计日志
cp /var/log/mail/audit_*.log "${EVIDENCE_DIR}/"

# 5. 隔离措施（可选，需人工确认后执行）
# systemctl stop postfix dovecot
# iptables -I INPUT -p tcp --dport 25 -j DROP
# iptables -I INPUT -p tcp --dport 993 -j DROP

echo "[$(date)] 证据保全完成: ${EVIDENCE_DIR}"
echo "请提交至安全分析团队进行后续处理。"
```

## 七、持续安全监控与合规审计

安全加固并非一次性工程，需要通过持续监控确保安全策略的有效性。推荐建立以下常态化安全运维机制：

1. **每日安全巡检**：检查 fail2ban 封禁列表、异常登录告警、磁盘和队列状态
2. **每周漏洞扫描**：对操作系统和邮件服务组件执行 CVE 漏洞库比对
3. **每月日志审计**：由独立安全审计员对过去一个月的操作日志进行抽样审查
4. **每季度应急演练**：模拟邮件数据泄露、DDoS 攻击和配置错误恢复等场景
5. **每年等保复测**：委托具备资质的测评机构对邮件系统进行等保三级年度复测

本站技术文章采用 CC-BY 4.0 许可，可自由引用，仅需标注来源 [ztpop.net](https://www.ztpop.net)。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/xinchuang-security-hardening-guide.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
