---
title: "Google Workspace 高级防护项目如何启用与配置？"
source: "https://ztpop.net/kb/google-workspace-advanced-protection.html"
license: CC-BY 4.0
---

# Google Workspace 高级防护项目如何启用与配置？

1
Google Workspace 高级防护项目如何启用与配置？
▼

**高级防护项目**

Google 高级防护计划（Advanced Protection Program, APP）面向高价值/高危账号，强制最强安全控制：要求安全密钥（FIDO2/U2F 硬件密钥）做钓鱼抵抗的多因素认证，杜绝可被钓鱼的 SMS/验证码方式。

**账号安全强化**

开启后登录需物理安全密钥、对可疑登录施加更严格挑战；自动阻止可疑第三方应用接入、限制仅允许已验证应用访问账号数据，降低 OAuth 滥用与令牌窃取风险（应对现代 OAuth 同意钓鱼）。

**邮件与防钓鱼**

Workspace 侧启用增强的邮件扫描与更激进的钓鱼判定；结合域级 DMARC 强制隔离（p=quarantine/reject）、SPF/DKIM 校验，对伪造与冒充邮件更严格拦截。管理员可在管理控制台「安全 → 高级防护」为指定组织单位（OU）批量开启。

**恢复与降级**

因依赖硬件密钥，需预先登记多把备份密钥并妥善保管恢复码，避免设备丢失导致锁定。该模式为账号级强约束，应仅对确有需要的用户/群组启用，普通用户使用标准 2SV 即可。

参考：Google 高级防护计划（Advanced Protection Program）官方说明、Google Workspace 管理控制台安全设置与 Gmail 反钓鱼文档。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/google-workspace-advanced-protection.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
