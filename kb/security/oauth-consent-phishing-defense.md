---
title: "OAuth 同意钓鱼（Consent Phishing）如何防御？"
source: "https://ztpop.net/kb/oauth-consent-phishing-defense.html"
license: CC-BY 4.0
---

# OAuth 同意钓鱼（Consent Phishing）如何防御？

1
OAuth 同意钓鱼（Consent Phishing）如何防御？
▼

**同意钓鱼的原理**

与传统钓鱼不同，同意钓鱼不需要窃取密码：攻击者先注册一个恶意 OAuth 应用（如仿冒「邮件备份工具」），再发邮件诱导受害者点击授权链接。一旦受害者同意，攻击者即获得该应用对邮箱、通讯录甚至发送权限的持久访问令牌，且后续访问不触发密码重置。

真实攻击手法：链接指向真实的微软/谷歌授权页（非伪造登录页），受害者因「官方域名的登录页」而放松警惕；授予的 scope 往往远超所需（如 `Mail.ReadWrite`、`Contacts.Read`），攻击者可长期静默读取与转发邮件。

**检测指标**

* **发布者可疑**：应用未通过发布者验证，或注册地为高风险地区。
* **权限过大**：一次性申请 `Mail.Read`/`Mail.Send`/`offline_access` 等敏感 scope。
* **行为异常**：授权后应用立即批量读取邮件、调用 Graph API 拉取通讯录。
* **间接登录**：无对应密码登录事件却出现应用访问令牌使用记录。

**防御与治理**

* **同意策略**：禁用普通用户自行授权，改为管理员同意工作流（admin consent workflow），所有第三方应用须经安全评审。
* **应用治理**：启用 OAuth 应用发现与风险评分，对高权限/未验证应用自动拦截或撤销。
* **条件访问**：对来自新应用、新设备的敏感 API 调用加多因子与风险策略。
* **监测**：审计 Entra ID / Google Workspace 的应用授权与 Graph 调用日志。

参考：Microsoft 365 Defender《Consent phishing》专题、CISA 应用授权风险通告、MITRE ATT&CK T1528（Steal Application Access Token）。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/oauth-consent-phishing-defense.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
