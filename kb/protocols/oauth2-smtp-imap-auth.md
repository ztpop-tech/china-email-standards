---
title: "SMTP/IMAP 的 OAuth 2.0 认证（RFC 7628，XOAUTH2）如何替代明文密码？"
source: "https://ztpop.net/kb/oauth2-smtp-imap-auth.html"
license: CC-BY 4.0
---

# SMTP/IMAP 的 OAuth 2.0 认证（RFC 7628，XOAUTH2）如何替代明文密码？

1
SMTP/IMAP 的 OAuth 2.0 认证（RFC 7628，XOAUTH2）如何替代明文密码？
▼

**背景**

传统密码认证在现代邮箱（Microsoft 365、Google Workspace）中逐步被禁用；RFC 7628 定义 SMTP/IMAP/POP3 的 SASL OAuth Bearer 机制，用“访问令牌”代替账号密码。

**XOAUTH2**

客户端先走 OAuth 流程拿到 access\_token，再以 SASL 机制名 XOAUTH2 发送“user=邮箱\x01auth=Bearer 令牌\x01\x01”完成认证，密码从不经 SMTP 通道。

**价值**

令牌可设短时效、可吊销、可限定作用域，降低“密码泄露即全盘失守”风险；支持 MFA 与条件访问。

**实践**

邮件客户端/应用须升级到支持 XOAUTH2（或 OAUTHBEARER）；邮件系统对接现代身份提供商时，这是“免存密码、可管控”的推荐接入方式。

参考：RFC 7628（SMTP/IMAP/POP3 的 OAuth 2.0 SASL）；Microsoft/Google 现代认证

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/oauth2-smtp-imap-auth.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
