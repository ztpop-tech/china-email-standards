---
title: "攻击者用「授权一个第三方 App」来窃取邮件，不用密码也能持续访问，怎么防？"
source: "https://ztpop.net/kb/oauth-consent-phishing-defense.html"
license: CC-BY 4.0
---

# 攻击者用「授权一个第三方 App」来窃取邮件，不用密码也能持续访问，怎么防？

1
攻击者用「授权一个第三方 App」来窃取邮件，不用密码也能持续访问，怎么防？
▼

**非法同意授权攻击的本质**

Microsoft 将此类称为 illicit consent grant attack（非法同意授权攻击），其本质是滥用 OAuth 应用程序同意框架，且预设调用信息的实体是自动化程序而非人类。攻击者在 Microsoft Entra ID 中注册一个应用，请求访问联系人、邮件或文档的权限，再通过钓鱼或向可信网站注入恶意代码，诱使最终用户授予该应用同意；一旦授予，恶意应用便获得**账户级访问（account-level access）**，且无需组织内的账户。

**为什么重置密码、上 MFA 都拦不住**

Microsoft 明确：常规处置（例如重置密码或要求多因素认证 MFA）对此类攻击无效，因为这些应用是**组织外部的（external to the organization）**。攻击者拿到的是应用自身的持久令牌，而不是某次登录凭据，因此改密码、加 MFA 都不会让已授予的应用失效。

**检测：在审计日志里找同意活动**

Microsoft 指出需在 Microsoft Purview Audit（Standard 或 Premium）中搜索可疑的「Consent to application（同意授予应用）」活动，这些即是入侵指标（IOC）。重点看：活动详情中 **IsAdminConsent 为 True**——意味着可能有人以全局管理员身份授予了广泛数据访问；用 PowerShell 导出权限清单后，关注 ConsentType 为 AllPrincipals（允许访问租户内所有人内容）、Permission 含 Read/Write/All、以及拼写错误/极平淡/黑客风格的可疑 ClientDisplayName。

**修复与预防**

修复（How to stop and remediate）：在 Microsoft Entra 管理中心撤销（用户 > 应用 > Remove），或用 PowerShell 的 Remove-MgOauth2PermissionGrant 撤销 OAuth 权限授予、Remove-MgServicePrincipalAppRoleAssignment 撤销服务应用角色分配；撤销受影响账户的登录；用 Microsoft Defender for Cloud Apps 的 OAuth app policies 审批或禁止权限请求。预防层面：配置管理员同意策略、限制用户自助同意（user consent）、对高权限范围要求管理员审批，从源头压缩攻击面。

参考：https://learn.microsoft.com/en-us/defender-office-365/detect-and-remediate-illicit-consent-grants

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/oauth-consent-phishing-defense.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
