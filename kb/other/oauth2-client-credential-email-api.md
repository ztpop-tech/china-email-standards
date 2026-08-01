---
title: "邮件 API 发送为什么推荐使用 OAuth 2.0 客户端凭据（Client Credentials）而非 SMTP 基本认证？"
source: "https://ztpop.net/kb/oauth2-client-credential-email-api.html"
license: CC-BY 4.0
---

# 邮件 API 发送为什么推荐使用 OAuth 2.0 客户端凭据（Client Credentials）而非 SMTP 基本认证？

1
邮件 API 发送为什么推荐使用 OAuth 2.0 客户端凭据（Client Credentials）而非 SMTP 基本认证？
▼

**基本认证被淘汰的原因**

SMTP 基本认证（用户名+密码明文或 Base64）长期是凭证泄露、密码喷洒与自动转发滥用的重灾区。Microsoft 365 已于 2022-10 起默认关闭所有租户的 SMTP 基本认证；Google 自 2024-09 起对新应用强制 OAuth。基本认证的口令一旦泄漏即等同于账户完全接管，且无设备/应用绑定与可吊销的细粒度授权。

**OAuth 2.0 客户端凭据模型**

客户端凭据授权（client\_credentials）适用于「服务到服务」发信：应用用自己的 client\_id + client\_secret 向令牌端点换取访问令牌，再以令牌通过 SMTP XOAUTH2 或 REST 邮件发送接口发信。相较用户口令，该凭据可被单独吊销、可限定作用域（scope 仅含 SMTP 发送）、不与具体用户登录绑定，且天然规避 MFA 疲劳类攻击。

**迁移要点**

①在租户后台登记应用并授予 Mail.Send 或 SMTP.Send 作用域；②将代码中的密码改为令牌请求+缓存刷新；③保留失败告警与令牌过期监控。注意 XOAUTH2 要求 SMTP 连接启用 STARTTLS/TLS，令牌有效期通常为 1 小时需自动续期。

参考：Microsoft Learn《Disable Basic authentication in Exchange Online》、Google Workspace《Using OAuth 2.0 to access Google APIs》、RFC 7628《SMTP Authentication Extension for OAuth 2.0》。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/oauth2-client-credential-email-api.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
