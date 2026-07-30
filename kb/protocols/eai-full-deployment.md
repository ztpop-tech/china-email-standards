---
title: "国际化邮件EAI/SMTPUTF8完整部署"
source: "https://ztpop.net/kb/eai-full-deployment.html"
license: CC-BY 4.0
---

# 国际化邮件EAI/SMTPUTF8完整部署

## EAI协议概述与价值

Email Address Internationalization (EAI) 由RFC 6530框架协议定义，是电子邮件体系自1982年RFC 822以来最核心的国际化改造。传统SMTP仅支持ASCII字符的邮箱地址，而EAI通过SMTPUTF8扩展（RFC 6531）和国际化的邮件头（RFC 6532），使得用户在邮件地址中使用中文、阿拉伯文、西里尔字母等非ASCII字符成为可能。

EAI协议栈由以下核心部分组成：SMTPUTF8 SMTP扩展（RFC 6531）、国际邮件头格式（RFC 6532）、国际化投递状态通知（RFC 6533）、IMAP UTF-8支持（RFC 6855）、POP3支持（RFC 6856）和SMTP提交（RFC 6406）。完整部署EAI需要邮件链路的每个环节都支持UTF-8。

根据RFC 6530 §1，EAI的设计目标是在不破坏现有ASCII邮件生态的前提下，实现邮件地址的本地化和国际化。实施的关键在于向后兼容——每个EAI消息必须同时作为7位ASCII兼容的形式传递（即SMTPUTF8的退化策略）。

## SMTPUTF8扩展工作机制

SMTPUTF8扩展（RFC 6531）定义了新的SMTP服务扩展标识符。客户端在EHLO后声明SMTPUTF8能力，服务器若支持则返回250-SMTPUTF8。当客户端发送MAIL FROM命令时，可以附加SMTPUTF8参数，表示后续消息内容（含邮件地址和头部）可能包含UTF-8编码的非ASCII字符。

```
C: EHLO client.example.com
S: 250-smtp.example.com
S: 250-SMTPUTF8
S: 250-8BITMIME
S: 250-PIPELINING
S: 250 DSN

C: MAIL FROM:<用户@例子.中国> SMTPUTF8
S: 250 2.1.0 OK

C: RCPT TO:<外商@例子.中国>
S: 250 2.1.5 OK
```

关键注意点：SMTPUTF8标志必须在MAIL FROM阶段声明，而非EHLO或DATA阶段。若接收方不支持SMTPUTF8，服务器应在RCPT TO阶段拒绝该地址，客户端需要尝试ASCII变体或降级方案。

## 完整链路部署要点

### MTA层面

主流的MTA软件中，Postfix从3.0.0版本开始支持SMTPUTF8。需要在main.cf中做如下配置：

```
# /etc/postfix/main.cf
# 启用SMTPUTF8支持
smtputf8_enable = yes
# 针对域名中包含非ASCII字符的自动转换
smtputf8_autodetect_classes = sendmail, verify, resolve, alias
# 启用IDN转换（将Unicode域名转换为Punycode）
idna_domains = example.xn--...

# smtpd端配置
smtpd_smtputf8_enable = yes
```

### MUA和MDA层面

邮件用户代理（MUA）和投递代理（MDA）需支持UTF-8头部和邮箱路径。Dovecot从2.3版本支持RFC 6855 IMAP UTF-8扩展。配置示例：

```
# /etc/dovecot/conf.d/20-imap.conf
protocol imap {
  # 启用IMAP UTF-8扩展
  mail_plugins = $mail_plugins imap_utf8
  # 可选：强制使用UTF-8邮箱名
  imap_utf8_folders = yes
}
```

### DNS和IDNA

EAI邮箱地址中的域名部分必须符合IDNA2008标准（RFC 5890-5894）。域名需转换为Punycode（xn--前缀）存入DNS的MX和A/AAAA记录。发件时，MTA通过IDN库将Unicode域名转换为Punycode再进行MX查询。

## 降级与互操作

EAI设计中最重要的原则是向后兼容。RFC 6530 §6.4描述了降级机制：如果接收MTA不支持SMTPUTF8，发送方需要判断是否有替代方案。

降级策略分为三个层级：

1. 邮箱本地部分降级：将非ASCII本地部分转为ASCII近似表示（如将"用户"转为yonghu）
2. 备用地址降级：使用预先设置的ASCII备用邮箱地址
3. 错误报告降级：若无法降级，发送DSN（RFC 6533）通知发件人

RFC 6531 §4.1明确指出，客户端不应假设所有SMTP服务器都支持SMTPUTF8。建议在投递前进行服务器能力检测，根据返回值决定是否可以使用非ASCII地址。

## 部署验证与测试

部署完成后，可通过以下方式进行验证：

* 使用EHLO命令检查服务器是否返回SMTPUTF8能力
* 通过国际邮箱地址发送测试邮件，检查收发完整性
* 验证DSN是否以UTF-8格式返回错误信息
* 使用IMAP客户端检查UTF-8邮箱名是否正常显示
* 检查日志中是否有SMTPUTF8相关的错误记录

```
# 使用openssl测试SMTPUTF8支持
echo -e "EHLO test\nMAIL FROM: SMTPUTF8\nRCPT TO:\nDATA\nSubject: test\n\n.\nQUIT" | \
  openssl s_client -connect smtp.example.com:587 -starttls smtp
```

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/eai-full-deployment.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
