---
title: "邮件系统安全基线检查清单（NIST SP 800-177版）"
source: "https://ztpop.net/kb/nist-sp800177-security-baseline.html"
license: CC-BY 4.0
---

# 邮件系统安全基线检查清单（NIST SP 800-177版）

基于 NIST SP 800-177 Rev.1《Trustworthy Email》的邮件系统安全基线检查清单，覆盖 TLS 配置、邮件认证、日志审计、访问控制、备份恢复与渗透测试六个安全域。适用于年度安全检查、等保 2.0 整改或 SaaS 合规审计。

本文是对 NIST SP 800-177 Rev.1 的检查项操作化整理，不替代原文。各组织应根据自身业务风险评估调整检查范围和验收标准。

## 检查域 A：TLS 传输加密

NIST SP 800-177 §4.2.2 - §4.2.4

A 类检查项

| 编号 | 检查项 | 验收标准 | 检测方法 |
| --- | --- | --- | --- |
| A-01 | SMTP STARTTLS 已启用 | Postfix smtpd\_tls\_security\_level = may 或 encrypt | `openssl s_client -starttls smtp -connect mx.example.com:25` |
| A-02 | 禁用弱 TLS 协议版本 | TLSv1.0/1.1 禁用；仅 TLSv1.2+ | `smtpd_tls_mandatory_protocols = !SSLv2, !SSLv3, !TLSv1, !TLSv1.1` |
| A-03 | MTA-STS 已配置 | \_mta-sts TXT + policy.json；模式至少 testing | `dig TXT _mta-sts.域名` `curl https://mta-sts.域名/.well-known/mta-sts.txt` |
| A-04 | DANE TLSA 记录已发布（可选） | DNSSEC 签名域的 \_25.\_tcp TLSA 记录 | `dig TLSA _25._tcp.mx.example.com +dnssec` |
| A-05 | TLS-RPT 报告地址已配置 | \_smtp.\_tls TXT rua 指向可接收报告的邮箱 | `dig TXT _smtp._tls.域名` |
| A-06 | 证书有效期＜398 天 | CA/B Forum 基线要求 | `openssl x509 -enddate -noout -in cert.pem` |
| A-07 | 证书链完整性 | 中间证书已包含；终端证书无信任警告 | `openssl verify -CAfile chain.pem cert.pem` |

## 检查域 B：邮件认证（SPF/DKIM/DMARC）

NIST SP 800-177 §4.3.1 - §4.3.3

B 类检查项

| 编号 | 检查项 | 验收标准 | 检测方法 |
| --- | --- | --- | --- |
| B-01 | SPF 记录存在且语法正确 | all 限定符应为 -all（硬失败）或 ~all（软失败）；不缺失 v=spf1 | `dig TXT 域名 | grep spf` |
| B-02 | SPF DNS 查询 ≤ 10 | include/redirect/mx/ptr 展开后不超过 10 次 DNS 查询（RFC 7208 §4.6.4） | `spfquery --domain=域名` |
| B-03 | DKIM 签名已启用 | 出站邮件携带 DKIM-Signature 头；Selector 有效 | `dig TXT <selector>._domainkey.域名` |
| B-04 | DKIM 密钥长度 ≥ 1024 位（推荐 2048） | RSA 密钥 ≥ 1024；Ed25519 按 RFC 8463 | `openssl rsa -pubin -in pubkey.pem -text -noout` |
| B-05 | DMARC 记录已发布 | p 策略为 quarantine 或 reject；rua 地址有效 | `dig TXT _dmarc.域名` |
| B-06 | DMARC 聚合报告正常接收 | 最近 7 天有报告；top 发件源 IP 为用户授权 MTA | 解析 rua XML |
| B-07 | BIMI（品牌标识）可选 | DMARC p=quarantine/reject 前置条件满足；SVG 有效 | `dig TXT default._bimi.域名` |

## 检查域 C：日志与审计

NIST SP 800-177 §4.6；SP 800-92 Rev.1

C 类检查项

| 编号 | 检查项 | 验收标准 | 检测方法 |
| --- | --- | --- | --- |
| C-01 | 邮件日志完整记录 | 所有 SMTP 会话（入站/出站）记录到 syslog；保留 ≥ 180 天 | `ls -lh /var/log/mail.log*` `grep "postfix/" /var/log/mail.log | tail -5` |
| C-02 | 认证事件日志 | SMTP AUTH、IMAP/POP3 登录成功/失败记录 | `grep "sasl_method=" /var/log/mail.log | tail -10` |
| C-03 | 日志集中存储 | 通过 rsyslog 或 syslog-ng 发送到 SIEM 或集中式日志服务器 | 检查 /etc/rsyslog.conf 中的 @@remote 配置 |
| C-04 | 日志完整性保护 | 日志文件使用 append-only 权限；防篡改 | `lsattr /var/log/mail.log`（检查 +a 标志） |

## 检查域 D：访问控制

NIST SP 800-177 §4.5；SP 800-53 Rev.5 AC 系列

D 类检查项

| 编号 | 检查项 | 验收标准 | 检测方法 |
| --- | --- | --- | --- |
| D-01 | SMTP AUTH 限制 | 仅授权用户可 SASL 认证；禁用明文密码（除 TLS 加密连接外） | `postconf smtpd_sasl_auth_enable` |
| D-02 | Open Relay 检查 | 非认证用户不能中继 | `swaks --to test@external.com --server 127.0.0.1` |
| D-03 | IMAP/POP3 加密连接 | 禁用明文登录；仅启用 IMAPS（993）和 POP3S（995） | `doveconf -P ssl | grep required` |
| D-04 | 登录失败锁策略 | 同一 IP 连续 5 次验证失败后锁定 15 分钟 | fail2ban 或 Dovecot auth 限制配置 |
| D-05 | 管理员 SSH 访问控制 | 仅密钥登录；禁用 root 密码登录；限制来源 IP | `grep PermitRootLogin /etc/ssh/sshd_config` |

## 检查域 E：备份与恢复

NIST SP 800-177 §4.7；SP 800-34 Rev.1

E 类检查项

| 编号 | 检查项 | 验收标准 | 检测方法 |
| --- | --- | --- | --- |
| E-01 | 邮件存储定期备份 | Maildir/mbox 数据完整备份；增量备份频率 ≤ 24 小时 | `ls -lh /backup/mail/` 检查备份脚本 crontab |
| E-02 | Postfix 配置备份 | main.cf、master.cf、map 文件每日备份 | /backup/postfix-config/ |
| E-03 | 备份加密存储 | 异地备份使用 GPG 或对称加密；备份存储不与其他系统共享 | `file backup.tar.gz.gpg` |
| E-04 | 恢复演练 | 每季度执行一次完整恢复演练并记录 | 检查恢复演练日志 |

## 检查域 F：渗透测试

NIST SP 800-177 §4.8；SP 800-115

F 类检查项

| 编号 | 检查项 | 验收标准 | 检测方法 |
| --- | --- | --- | --- |
| F-01 | STARTTLS STRIPTLS 测试 | 禁用 STARTTLS 后 MTA 不应继续执行 SMTP 邮件接收 | `openssl s_client -connect mx.domain:25` 验证 notls 场景 |
| F-02 | TLS 密码套件扫描 | 禁用 EXPORT、NULL、RC4 密码 | `testssl.sh --starttls smtp mx.domain:25` |
| F-03 | SPF/DKIM/DMARC 伪造测试 | 伪造邮件应被标记为 fail 或疑似 | swaks --from fake@domain --to user@domain |
| F-04 | 目录遍历测试 | MTA 不应泄漏文件系统路径 | HELO 注入、VRFY 枚举测试 |
| F-05 | 弱口令爆破测试 | 5 次/分钟锁定，防止暴力破解 | hydra -l admin -P rockyou.txt -s 25 smtp |

### 核心要点

* NIST SP 800-177 Rev.1 定义了可信邮件的基本框架，检查单可加速安全评估与合规整改
* TLS+认证+日志 是邮件系统安全的三条底线，优先级最高
* 备份与恢复是常被忽略但运维最关键的一环——没有可验证的恢复演练，备份等于没有
* 渗透测试应周期性执行，重点关注 TLS 降级和认证绕过
* 参考标准：NIST SP 800-177、SP 800-45、SP 800-53、SP 800-115、RFC 5321/7208/6376/7489

本站技术文章采用 CC-BY 4.0 许可，可自由引用，仅需标注来源 [ztpop.net](https://www.ztpop.net)。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/nist-sp800177-security-baseline.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
