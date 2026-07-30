---
title: "SMTP提交端口587/465 安全部署"
source: "https://ztpop.net/kb/smtp-submission-port-security.html"
license: CC-BY 4.0
---

# SMTP提交端口587/465 安全部署

## 提交端口标准化历史

电子邮件提交（Message Submission）与邮件中继（Relay）有着本质区别。RFC 5321定义的SMTP协议主要用于MTA之间的邮件中继（端口25），而RFC 6409定义了专门的邮件提交协议（端口587），区分了用户提交和服务器间中继。端口465（smtps）最初由IANA分配给SMTPS，后经RFC 8314重新确立为隐式TLS的邮件提交端口。

RFC 8314（2018年）是一个里程碑式的标准，明确宣布明文电子邮件传输协议已过时（Cleartext Considered Obsolete）。该RFC要求所有电子邮件提交和访问协议默认采用TLS加密，并强烈推荐端口465作为隐式TLS提交的标准端口。

## 端口587（SUBMISSION）配置规范

### STARTTLS模式

端口587使用STARTTLS（RFC 3207）进行机会性加密。客户端首先建立明文连接，然后通过STARTTLS命令升级为TLS加密通道。

```
C: EHLO client.example.com
S: 250-submission.example.com
S: 250-PIPELINING
S: 250-SIZE 52428800
S: 250-AUTH LOGIN PLAIN
S: 250-STARTTLS
S: 250 SMTPUTF8

C: STARTTLS
S: 220 Ready to start TLS
# TLS握手开始

# TLS建立后重新EHLO
C: EHLO client.example.com
S: 250-submission.example.com
S: 250-PIPELINING
S: 250-AUTH LOGIN PLAIN
S: 250-SIZE 52428800
S: 250 SMTPUTF8
```

Postfix配置端口587的提交服务（使用master.cf）：

```
# /etc/postfix/master.cf
submission inet n       -       n       -       -       smtpd
  -o smtpd_tls_security_level=may
  -o smtpd_sasl_auth_enable=yes
  -o smtpd_sasl_type=dovecot
  -o smtpd_sasl_path=private/auth
  -o smtpd_sasl_authenticated_header=no
  -o smtpd_recipient_restrictions=\n    permit_sasl_authenticated,\n    permit_mynetworks,\n    reject_unauth_destination
  -o milter_macro_daemon_name=ORIGINATING
  -o smtpd_relay_restrictions=
    permit_sasl_authenticated,
    reject_unauth_destination
```

### 用户认证配置

RFC 4954定义了SMTP AUTH扩展。身份验证由SASL框架承载（Postfix集成Dovecot SASL）：

```
# Dovecot SASL配置（/etc/dovecot/conf.d/10-master.conf）
service auth {
  unix_listener /var/spool/postfix/private/auth {
    mode = 0660
    user = postfix
    group = postfix
  }
}

# Dovecot SASL支持的机制（/etc/dovecot/conf.d/auth.conf）
auth_mechanisms = plain login
# 可选：CRAM-MD5（防止明文密码传输）
# 推荐：在TLS下使用PLAIN/LOGIN即可确保密码安全
```

## 端口465（SMTPS）安全部署

### 隐式TLS模式

端口465采用隐式TLS（Implicit TLS），客户端建立连接即开始TLS握手，无需STARTTLS命令。RFC 8314 §3.3明确推荐将端口465作为邮件提交的首选端口——因为隐式TLS消除了STARTTLS降级攻击的风险（即攻击者拦截STARTTLS命令使其不回显STARTTLS能力）。

```
# /etc/postfix/master.cf
smtps     inet  n       -       n       -       -       smtpd
  -o smtpd_tls_wrappermode=yes
  -o smtpd_sasl_auth_enable=yes
  -o smtpd_sasl_type=dovecot
  -o smtpd_sasl_path=private/auth
  -o smtpd_sasl_authenticated_header=no
  -o smtpd_recipient_restrictions=\n    permit_sasl_authenticated,\n    permit_mynetworks,\n    reject_unauth_destination
  -o milter_macro_daemon_name=ORIGINATING
  -o smtpd_tls_cert_file=/etc/ssl/certs/submit.example.com.pem
  -o smtpd_tls_key_file=/etc/ssl/private/submit.example.com.key
  -o smtpd_tls_security_level=encrypt
```

smtpd\_tls\_wrappermode=yes启用隐式TLS模式。此时Postfix不会等待STARTTLS命令，而是在TCP连接建立后立即启动TLS握手。

## TLS安全基线配置

### 协议和密码套件

```
# /etc/postfix/main.cf（安全基线配置）
# 禁用不安全的SSL/TLS版本
smtpd_tls_protocols = !SSLv2, !SSLv3, !TLSv1, !TLSv1.1
smtpd_tls_mandatory_protocols = !SSLv2, !SSLv3, !TLSv1, !TLSv1.1
smtpd_tls_eecdh_grade = strong

# 密码套件优先级
smtpd_tls_ciphers = high
smtpd_tls_mandatory_ciphers = high

# 强制ECDHE密钥交换
smtpd_tls_dh512_param_file = /etc/postfix/dh512.pem
smtpd_tls_dh1024_param_file = /etc/postfix/dh1024.pem

# HSTS-like MTA-STS的提交侧等效策略
smtpd_tls_always_use_starttls = no  # 端口587专用

# 客户端证书（可选）
smtpd_tls_ask_ccert = no
smtpd_tls_received_header = yes
```

### 有效性检查命令

```
# 使用openssl检查端口465的TLS配置
$ openssl s_client -connect submit.example.com:465 \
  -servername submit.example.com \
  -tls1_3 \
  -ciphersuites TLS_AES_256_GCM_SHA384

# 检查证书完整链
$ echo | openssl s_client -connect submit.example.com:465 \
  -showcerts 2>/dev/null | openssl x509 -text -noout

# 验证支持的前向安全
$ nmap --script ssl-enum-ciphers -p 465 submit.example.com
```

## 策略控制与访问限制

### 提交与中继分离

端口587和465的服务必须严格限制为已认证用户的邮件提交。端口25服务仅限于中继SMTP流量，不应开启SASL认证（避免恶意用户通过认证突破中继限制）。提交服务应强制执行以下策略：

* 拒绝未经认证的收件地址（reject\_unauth\_destination）
* 限制发件域为用户认证域（reject\_authenticated\_sender\_login\_mismatch）
* 限制单连接邮件数量（smtpd\_soft\_error\_limit和smtpd\_hard\_error\_limit）
* 拒绝无效的HELO主机名（reject\_invalid\_helo\_hostname）
* 拒绝不规范的邮件地址（reject\_non\_fqdn\_sender和reject\_non\_fqdn\_recipient）

端口25与提交端口的MTA架构分离是邮件安全的基础。RFC 6409 §4明确要求提交服务器必须执行策略管制，包括但不限于：验证发件人身份、限制邮件大小、拒绝滥用IP连接。严格区分提交和中继管道，是避免开放中继漏洞的最佳实践。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/smtp-submission-port-security.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
