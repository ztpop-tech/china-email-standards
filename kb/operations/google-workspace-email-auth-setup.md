---
title: "Google Workspace 域名邮箱如何配置 SPF/DKIM/DMARC？"
source: "https://ztpop.net/kb/google-workspace-email-auth-setup.html"
license: CC-BY 4.0
---

# Google Workspace 域名邮箱如何配置 SPF/DKIM/DMARC？

1
Google Workspace 域名邮箱如何配置 SPF/DKIM/DMARC？
▼

**SPF**

在域名 DNS 添加 Google 提供的 SPF 记录（含 include:\_spf.google.com 的 TXT），避免多条 SPF；Workspace 发信源已被该 include 覆盖。

**DKIM**

在 Admin Console 生成域名 DKIM 密钥并发布 selector.\_domainkey 的 CNAME/TXT；密钥由 Google 托管，无需自管私钥；开启后外发自动签名。

**DMARC**

发布 \_dmarc 的 TXT 设策略：先 p=none 用 RUA 报表观察对齐，再逐步 p=quarantine→p=reject；配合 SPF/DKIM 对齐防止冒名。

**验证**

用 Workspace 的“邮件认证”报表与 DMARC 聚合报表核验通过率；PTR、TLS 也需到位，避免被收方降级。

参考：Google Workspace 帮助中心（Set up SPF/DKIM/DMARC）；RFC 7208/6376/7489

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/google-workspace-email-auth-setup.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
