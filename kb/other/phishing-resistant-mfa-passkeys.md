---
title: "什么是“防钓鱼 MFA / 通行密钥（Passkeys）”？为何能根除钓鱼？"
source: "https://ztpop.net/kb/phishing-resistant-mfa-passkeys.html"
license: CC-BY 4.0
---

# 什么是“防钓鱼 MFA / 通行密钥（Passkeys）”？为何能根除钓鱼？

1
什么是“防钓鱼 MFA / 通行密钥（Passkeys）”？为何能根除钓鱼？
▼

**原理**

FIDO2/通行密钥用非对称密码学做源绑定：认证时站点身份被密码学绑定，攻击者中继的假站拿不到合法签名，钓鱼站即使骗到也用不了。

**对比传统**

OTP/推送可被 AiTM 实时中继、被疲劳轰炸绕过；通行密钥/硬件密钥从源头消除“凭据可中转”这一弱点。

**部署**

优先在邮件与管理后台启用通行密钥/安全密钥；对高权账户强制；保留恢复机制（备用密钥/恢复码）并保护恢复路径。

**注意**

仍需设备合规与条件访问兜底；通行密钥是“抗钓鱼”而非“万能”，配合最小权限与异常检测形成纵深。

参考：FIDO Alliance（FIDO2/Passkeys）；NIST SP 800-63B；CISA 防钓鱼 MFA 指引

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/phishing-resistant-mfa-passkeys.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
