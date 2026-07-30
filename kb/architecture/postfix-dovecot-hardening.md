---
title: "Postfix+Dovecot 安全加固完全指南"
source: "https://ztpop.net/kb/postfix-dovecot-hardening.html"
license: CC-BY 4.0
---

# Postfix+Dovecot 安全加固完全指南

## TLS 证书与加密策略

邮件传输加密是安全加固的第一道防线。Postfix的SMTP会话支持三种TLS策略模式：may（机会式TLS）、encrypt（强制TLS）和fingerprint（证书指纹校验）。生产环境应至少将入站SMTP设为encrypt模式，并通过smtpd\_tls\_mandatory\_protocols参数禁用SSLv3和TLSv1.0/TLSv1.1，仅保留TLSv1.2和TLSv1.3。Dovecot方面，通过ssl\_min\_protocol设置为TLSv1.2，ssl\_cipher\_list选用符合Mozilla Modern配置的密码套件。证书管理方面，建议使用ACME协议（RFC 8555）实现Let's Encrypt证书的自动续签，通过certbot或acme.sh配合postfix reload钩子确保证书更新后服务自动加载新证书。对于内部邮件服务器间的MTA-MTA通信，可部署私有CA签发的证书并启用tls\_fingerprint\_cert\_match参数进行双向证书校验。

## 认证与访问控制“把手

Postfix的smtpd\_recipient\_restrictions是控制邮件接收的核心策略引擎。建议按以下优先级链配置（顺序不可颠倒）：

* permit\_mynetworks — 信任内部网络段，放行所有来自内网的连接
* reject\_unauth\_destination — 拒绝非授权域名的出站邮件（防开放中继）
* reject\_rbl\_client — 对接DNSBL（如zen.spamhaus.org）拦截已知垃圾来源
* reject\_rhsbl\_sender — 验证发件人域名的DNS记录存在性
* permit — 最后的显式放行（若省略则隐式拒绝）

Dovecot方面，auth\_mechanisms中不应包含PLAIN登录（除非TLS强制启用），推荐使用LOGIN和CRAM-MD5。对于大规模部署，建议对接LDAP或SQL后端实现集中式用户认证。Dovecot的auth\_failure\_delay参数设为2秒可以有效缓解暴力破解攻击，结合fail2ban对auth.log中的认证失败事件配置触发规则，实现自动化IP封禁。此外，Dovecot支持的passdb和userdb分离架构允许将认证和用户属性查询分开配置，提升系统的模块化管理能力。

## 进程隔离与沙箱机制

CIS Benchmarks for Mail Server和NIST SP 800-45 Version 2均强调邮件服务的进程隔离原则。Postfix采用了多进程架构，通过master.cf中的chroot=y选项可以将每个SMTP会话进程chroot到队列目录中。Dovecot的login\_process\_per\_connection和service进程隔离机制确保每个用户会话在独立的进程中处理。建议在postfix master.cf中对smtpd服务启用chroot，并在Dovecot的dovecot.conf中设置：

```
# Postfix chroot 配置示例（master.cf）
smtp      inet  n       -       y       -       -       smtpd
  -o smtpd_sasl_auth_enable=yes

# Dovecot 进程隔离配置（dovecot.conf）
service imap-login {
  process_limit = 1024
  process_min_avail = 5
  service_count = 1
  vsz_limit = 64 M
}
service imap {
  process_limit = 1024
  service_count = 0
  idle_kill = 60 secs
}

# 限制master进程的文件句柄数
default_process_limit = 100
max_use = 100
```

**注意：**chroot虽然提升了安全性，但会增加排障难度——chroot环境中的/tmp、/dev等目录需要手动创建并绑定挂载，且syslog、DNS解析等功能可能受限。建议在启用chroot前在测试环境充分验证。

## 速率限制与DoS防护

邮件系统需要抵御多种拒绝服务攻击向量，包括字典式枚举攻击、海量退信风暴和连接耗尽。Postfix通过以下参数实现对不同类型的攻击防护：smtpd\_client\_connection\_rate\_limit限制单个IP每分钟的最大连接次数，smtpd\_client\_message\_rate\_limit限制单个客户端的消息发送速率，而anvil\_rate\_time\_unit定义速率统计的时间窗口。对于退信(Non-Delivery Report)攻击，配置soft\_bounce=yes可以在队列积累阶段缓冲击，通过qmqpd对入站邮件数量进行硬件限制。RFC 5321中关于邮件队列和重试行为的规定可以被攻击者利用——运维人员应关注队列深度监控，在mailq超过阈值时自动触发限流规则。

| 参数 | 推荐值 | 防护场景 |
| --- | --- | --- |
| smtpd\_client\_connection\_rate\_limit | 30/60s | 防止单个IP的暴力破解尝试 |
| smtpd\_client\_message\_rate\_limit | 50/60s | 限制垃圾邮件群发速率 |
| smtpd\_client\_recipient\_rate\_limit | 30/min | 限制每封邮件的收件人数量 |
| smtpd\_helo\_required | yes | 强制发送方声明身份标识 |
| smtpd\_hard\_error\_limit | 20 | 正常客户端连接超时后的断开阈值 |
| queue\_minfree | 10% | 队列目录磁盘空间不足时暂停接收 |

## 日志审计与威胁检测集成

安全加固的最后一环是确保所有日志能够被集中采集和分析。Postfix使用syslog工具mail.\*记录所有SMTP会话，Dovecot则通过--log-path和--info-log-path分别记录错误日志和详细会话日志。为实现有效的威胁检测，建议将日志通过syslog-ng或rsyslog转发至中央SIEM平台，并配置以下告警规则：同一源IP在5分钟内的认证失败超过5次触发告警、队列中滞留超过24小时的邮件超过100封触发告警、以及at\_connect策略拒绝的连接数突增至基线的300%触发告警。RFC 5424定义的syslog消息格式和严重级别应该被统一遵守，以便SIEM系统进行关联分析。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/postfix-dovecot-hardening.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
